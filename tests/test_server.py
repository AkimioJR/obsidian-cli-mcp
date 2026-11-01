from unittest.mock import AsyncMock, patch

import pytest
from mcp.types import CallToolResult, TextContent

from obsidian_mcp.cli import CommandExecutionResult
from obsidian_mcp.server import create_server


def test_server_tools_registered():
    server = create_server(cli_path="/mock/obsidian")
    tools = server._tool_manager._tools
    assert len(tools) == 45
    assert "obsidian_read" in tools
    assert "obsidian_create" in tools
    assert "obsidian_tags" in tools
    assert "obsidian_vaults" in tools
    assert "obsidian_version" in tools


@pytest.mark.asyncio
async def test_tool_call_success():
    server = create_server(cli_path="/mock/obsidian")
    with patch(
        "obsidian_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0, stdout="1.14.5", stderr=""
            )
        ),
    ):
        result = await server.call_tool("obsidian_version", {})
        assert isinstance(result, CallToolResult)
        item = result.content[0]
        assert isinstance(item, TextContent)
        assert item.text == "1.14.5"


@pytest.mark.asyncio
async def test_tool_call_error_caught_gracefully():
    server = create_server(cli_path="/mock/obsidian")
    with patch(
        "obsidian_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0,
                stdout='Error: File "missing.md" not found.',
                stderr="",
            )
        ),
    ):
        result = await server.call_tool("obsidian_read", {"file": "missing.md"})
        assert isinstance(result, CallToolResult)
        item = result.content[0]
        assert isinstance(item, TextContent)
        assert "Error:" in item.text
        assert "missing.md" in item.text


def test_tool_literal_schema_enums():
    server = create_server(cli_path="/mock/obsidian")
    vault_tool = server._tool_manager._tools["obsidian_vault"]
    info_param = vault_tool.parameters["properties"]["info"]
    # 验证 Literal 会被转换为 schema 中的 enum 约束
    any_of = info_param.get("anyOf", [])
    enum_vals = None
    for branch in any_of:
        if "enum" in branch:
            enum_vals = branch["enum"]
            break
    assert enum_vals == ["name", "path", "files", "folders", "size"]
