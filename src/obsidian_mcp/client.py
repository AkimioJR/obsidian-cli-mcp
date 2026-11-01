import json
import os
import shutil
from typing import Any

from .cli import CommandExecutionResult, run_cli_command
from .exceptions import ObsidianCLIError, ObsidianNotFoundError


class ObsidianClient:
    """Obsidian CLI 异步客户端。负责参数序列化、环境变量回退、执行控制与结果解析。"""

    def __init__(
        self,
        vault: str | None = None,
        cli_path: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.vault = vault or os.getenv("OBSIDIAN_VAULT")
        resolved_cli = cli_path or os.getenv("OBSIDIAN_CLI_PATH") or shutil.which("obsidian")
        if not resolved_cli:
            raise ObsidianNotFoundError(
                "Obsidian CLI executable not found. Please install Obsidian CLI or set OBSIDIAN_CLI_PATH."
            )
        self.cli_path = resolved_cli
        self.timeout = timeout

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
        - 其余类型: 转换为 key=value 字符串
        """
        args = [command]
        merged_params = dict(params or {})

        # 确定目标 vault：参数指定 > 实例/环境变量默认 > 不传（回退到活跃库）
        target_vault = vault if vault is not None else self.vault
        if target_vault is not None and "vault" not in merged_params:
            merged_params["vault"] = target_vault

        for key, val in merged_params.items():
            if val is None or val is False:
                continue
            if val is True:
                args.append(key)
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
        timeout: int | None = None,
    ) -> Any:
        """执行 Obsidian CLI 命令并返回文本或解析后的 JSON。"""
        cli_args = self._build_args(command, params, vault=vault)
        res: CommandExecutionResult = await run_cli_command(
            self.cli_path, cli_args, timeout=timeout or self.timeout
        )

        # 检查错误：非零退出码或 stdout 以 Error: 开头
        if res.returncode != 0:
            err_msg = res.stderr or res.stdout or f"Command '{command}' failed with exit code {res.returncode}"
            raise ObsidianCLIError(
                err_msg, returncode=res.returncode, stderr=res.stderr, stdout=res.stdout
            )

        if res.stdout.startswith("Error:"):
            raise ObsidianCLIError(
                res.stdout, returncode=res.returncode, stderr=res.stderr, stdout=res.stdout
            )

        if parse_json:
            try:
                return json.loads(res.stdout)
            except json.JSONDecodeError:
                return res.stdout

        return res.stdout
