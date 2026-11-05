import json
import os
import shutil
import subprocess
from typing import Any

from .cli import CommandExecutionResult, run_cli_command
from .exceptions import ObsidianCLIError, ObsidianNotFoundError
from .version import Version

# 允许保留空字符串的参数（如清空属性值、创建空白内容等）
ALLOW_EMPTY_VALUE_KEYS = {"content", "value"}


class ObsidianClient:
    """Obsidian CLI 异步客户端。负责参数序列化、环境变量回退、执行控制与结果解析。"""

    def __init__(
        self,
        vault: str | None = None,
        cli_path: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.vault = vault or os.getenv("OBSIDIAN_VAULT")
        resolved_cli = (
            cli_path or os.getenv("OBSIDIAN_CLI_PATH") or shutil.which("obsidian")
        )
        if not resolved_cli:
            raise ObsidianNotFoundError(
                "Obsidian CLI executable not found. Please install Obsidian CLI or set OBSIDIAN_CLI_PATH."
            )
        self.cli_path = resolved_cli

        # 确定超时时间：显式参数 > 环境变量 OBSIDIAN_TIMEOUT > 默认 30.0 秒
        if timeout is not None:
            self.timeout: float | None = timeout
        else:
            env_timeout = os.getenv("OBSIDIAN_TIMEOUT")
            if env_timeout is not None:
                env_val = env_timeout.strip().lower()
                if env_val in ("none", "null"):
                    self.timeout = None
                else:
                    try:
                        self.timeout = float(env_val)
                    except ValueError:
                        self.timeout = 30.0
            else:
                self.timeout = 30.0

    def get_version(self) -> Version | None:
        """查询 Obsidian 桌面客户端版本并解析为 Version 对象。

        优先读取环境变量 OBSIDIAN_VERSION，未设置时通过 CLI 'obsidian version' 探针探测。
        """
        env_ver = os.getenv("OBSIDIAN_VERSION")
        if env_ver:
            parsed = Version.try_parse(env_ver)
            if parsed:
                return parsed

        try:
            proc = subprocess.run(
                [self.cli_path, "version"],
                capture_output=True,
                text=True,
                timeout=5.0,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout:
                return Version.try_parse(proc.stdout)
        except (subprocess.SubprocessError, OSError, ValueError):
            return None
        return None

    def set_vault(self, vault: str | None) -> None:
        """动态设置或重置该客户端实例的默认目标笔记库。"""
        self.vault = vault.strip() if vault and vault.strip() else None

    def _build_args(
        self,
        command: str,
        params: dict[str, Any] | None = None,
        vault: str | None = None,
    ) -> list[str]:
        """将 Python 字典转换为 Obsidian CLI 参数列表。

        规则：
        - True: 转换为裸 flag（例如 verbose=True -> 'verbose'）
        - False / None: 忽略该参数
        - 纯空白字符串（若非 content/value 白名单）: 忽略该参数，防止意外触发 CLI 对活跃文件的回退行为
        - 其余类型: 转换为 key=value 字符串
        """
        args = [command]
        merged_params = dict(params or {})

        # 确定目标 vault：参数指定 > 实例/环境变量默认 > 不传（回退到活跃库）
        target_vault = vault if vault is not None else self.vault
        if target_vault and target_vault.strip() and "vault" not in merged_params:
            merged_params["vault"] = target_vault.strip()

        for key, val in merged_params.items():
            if val is None or val is False:
                continue
            if val is True:
                args.append(key)
            elif (
                isinstance(val, str)
                and not val.strip()
                and key not in ALLOW_EMPTY_VALUE_KEYS
            ):
                continue
            else:
                args.append(f"{key}={val}")

        return args

    async def execute(
        self,
        command: str,
        params: dict[str, Any] | None = None,
        *,
        parse_json: bool = False,
        vault: str | None = None,
        timeout: float | None = None,
    ) -> Any:
        """执行 Obsidian CLI 命令并返回文本或解析后的 JSON。"""
        cli_args = self._build_args(command, params, vault=vault)
        effective_timeout = timeout if timeout is not None else self.timeout
        res: CommandExecutionResult = await run_cli_command(
            self.cli_path, cli_args, timeout=effective_timeout
        )

        # 检查错误：非零退出码或 stdout 以 Error: 开头
        if res.returncode != 0:
            err_msg = (
                res.stderr
                or res.stdout
                or f"Command '{command}' failed with exit code {res.returncode}"
            )
            raise ObsidianCLIError(
                err_msg, returncode=res.returncode, stderr=res.stderr, stdout=res.stdout
            )

        if res.stdout.startswith("Error:"):
            raise ObsidianCLIError(
                res.stdout,
                returncode=res.returncode,
                stderr=res.stderr,
                stdout=res.stdout,
            )

        if parse_json:
            try:
                return json.loads(res.stdout)
            except json.JSONDecodeError:
                return res.stdout

        return res.stdout
