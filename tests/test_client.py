from unittest.mock import AsyncMock, patch

import pytest

from obsidian_cli_mcp.cli import CommandExecutionResult
from obsidian_cli_mcp.client import ObsidianClient
from obsidian_cli_mcp.exceptions import ObsidianCLIError, ObsidianNotFoundError


def test_build_args_basic():
    client = ObsidianClient(cli_path="/mock/obsidian")
    args = client._build_args(
        "create",
        {
            "name": "My Note",
            "content": "Hello World",
            "overwrite": True,
            "open": False,
            "template": None,
        },
    )
    assert args == [
        "create",
        "name=My Note",
        "content=Hello World",
        "overwrite",
    ]


def test_build_args_vault_priority(monkeypatch):
    monkeypatch.setenv("OBSIDIAN_VAULT", "EnvVault")

    # 1. 未显式指定且 client 无 default -> 使用环境变量
    client_env = ObsidianClient(cli_path="/mock/obsidian")
    args = client_env._build_args("read", {"file": "test.md"})
    assert "vault=EnvVault" in args

    # 2. client 实例指定了 vault -> 优先于环境变量
    client_inst = ObsidianClient(vault="ClientVault", cli_path="/mock/obsidian")
    args = client_inst._build_args("read", {"file": "test.md"})
    assert "vault=ClientVault" in args

    # 3. 方法参数显式传 vault -> 最高优先级
    args = client_inst._build_args("read", {"file": "test.md"}, vault="OverrideVault")
    assert "vault=OverrideVault" in args


def test_cli_not_found(monkeypatch):
    monkeypatch.delenv("OBSIDIAN_CLI_PATH", raising=False)
    monkeypatch.setattr("shutil.which", lambda _: None)
    with pytest.raises(ObsidianNotFoundError):
        ObsidianClient(cli_path=None)


@pytest.mark.asyncio
async def test_execute_success():
    client = ObsidianClient(cli_path="/mock/obsidian")
    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0, stdout="Success output", stderr=""
            )
        ),
    ):
        out = await client.execute("version")
        assert out == "Success output"


@pytest.mark.asyncio
async def test_execute_json_parsing():
    client = ObsidianClient(cli_path="/mock/obsidian")
    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0,
                stdout='[{"tag": "#test", "count": 5}]',
                stderr="",
            )
        ),
    ):
        out = await client.execute("tags", parse_json=True)
        assert isinstance(out, list)
        assert out[0]["tag"] == "#test"
        assert out[0]["count"] == 5


@pytest.mark.asyncio
async def test_execute_error_handling():
    client = ObsidianClient(cli_path="/mock/obsidian")

    # 非零退出码错误
    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=1, stdout="", stderr="Something failed"
            )
        ),
    ):
        with pytest.raises(ObsidianCLIError) as exc_info:
            await client.execute("read", {"file": "bad.md"})
        assert "Something failed" in str(exc_info.value)

    # 退出码为 0 但内容输出 Error: ...
    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0, stdout='Error: File "missing.md" not found.', stderr=""
            )
        ),
    ):
        with pytest.raises(ObsidianCLIError) as exc_info:
            await client.execute("read", {"file": "missing.md"})
        assert 'Error: File "missing.md" not found.' in str(exc_info.value)


def test_build_args_empty_string_guard():
    client = ObsidianClient(cli_path="/mock/obsidian")
    args = client._build_args(
        "create",
        {
            "name": "Note.md",
            "file": "",
            "path": "   ",
            "content": "",  # 白名单，保留
            "template": None,
        },
    )
    assert args == ["create", "name=Note.md", "content="]
