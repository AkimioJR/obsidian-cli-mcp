from unittest.mock import AsyncMock, patch

import pytest

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
        assert result.content[0].text == "1.14.5"


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
        assert "Error:" in result.content[0].text
        assert "missing.md" in result.content[0].text
