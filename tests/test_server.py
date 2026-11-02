from unittest.mock import AsyncMock, patch

import pytest
from mcp.types import CallToolResult, TextContent

from obsidian_cli_mcp.cli import CommandExecutionResult
from obsidian_cli_mcp.server import create_server


def test_server_tools_registered():
    server = create_server(cli_path="/mock/obsidian")
    tools = server._tool_manager._tools
    assert len(tools) == 45
    assert "read" in tools
    assert "create" in tools
    assert "tags" in tools
    assert "vaults" in tools
    assert "version" in tools


@pytest.mark.asyncio
async def test_tool_call_success():
    server = create_server(cli_path="/mock/obsidian")
    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0, stdout="1.14.5", stderr=""
            )
        ),
    ):
        result = await server.call_tool("version", {})
        assert isinstance(result, CallToolResult)
        item = result.content[0]
        assert isinstance(item, TextContent)
        assert item.text == "1.14.5"


@pytest.mark.asyncio
async def test_tool_call_error_caught_gracefully():
    server = create_server(cli_path="/mock/obsidian")
    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0,
                stdout='Error: File "missing.md" not found.',
                stderr="",
            )
        ),
    ):
        result = await server.call_tool("read", {"file": "missing.md"})
        assert isinstance(result, CallToolResult)
        item = result.content[0]
        assert isinstance(item, TextContent)
        assert "Error:" in item.text
        assert "missing.md" in item.text


def test_tool_literal_schema_enums():
    server = create_server(cli_path="/mock/obsidian")
    vault_tool = server._tool_manager._tools["vault"]
    info_param = vault_tool.parameters["properties"]["info"]
    # 验证 Literal 会被转换为 schema 中的 enum 约束
    any_of = info_param.get("anyOf", [])
    enum_vals = None
    for branch in any_of:
        if "enum" in branch:
            enum_vals = branch["enum"]
            break
    assert enum_vals == ["name", "path", "files", "folders", "size"]


def test_tool_parameter_descriptions():
    server = create_server(cli_path="/mock/obsidian")
    read_tool = server._tool_manager._tools["read"]
    file_param = read_tool.parameters["properties"]["file"]
    assert "resolves like wikilinks" in file_param.get("description", "")

    append_tool = server._tool_manager._tools["append"]
    content_param = append_tool.parameters["properties"]["content"]
    assert "Content to append" in content_param.get("description", "")
    assert "content" in append_tool.parameters.get("required", [])


@pytest.mark.asyncio
async def test_tool_call_json_result():
    server = create_server(cli_path="/mock/obsidian")
    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0,
                stdout='[{"tag": "#obsidian", "count": 12}]',
                stderr="",
            )
        ),
    ):
        result = await server.call_tool("tags", {})
        assert isinstance(result, CallToolResult)
        item = result.content[0]
        assert isinstance(item, TextContent)
        assert "#obsidian" in item.text


def test_all_tools_have_description_and_schema():
    server = create_server(cli_path="/mock/obsidian")
    tools = server._tool_manager._tools
    assert len(tools) == 45
    for tool in tools.values():
        assert tool.description and len(tool.description.strip()) > 0
        assert "properties" in tool.parameters


def test_feature_filtering_single():
    from obsidian_cli_mcp.tools import Feature

    server = create_server(cli_path="/mock/obsidian", features=[Feature.NOTE])
    tools = server._tool_manager._tools
    assert len(tools) == 9
    assert "read" in tools
    assert "create" in tools
    assert "delete" in tools
    # Other features should not be registered
    assert "tags" not in tools
    assert "vault" not in tools
    assert "eval" not in tools


def test_feature_tag_and_task_split():
    from obsidian_cli_mcp.tools import Feature

    # Test Feature.TAG
    server_tag = create_server(cli_path="/mock/obsidian", features=[Feature.TAG])
    tag_tools = server_tag._tool_manager._tools
    assert len(tag_tools) == 2
    assert "tags" in tag_tools
    assert "tag" in tag_tools
    assert "tasks" not in tag_tools
    assert "task" not in tag_tools

    # Test Feature.TASK
    server_task = create_server(cli_path="/mock/obsidian", features=[Feature.TASK])
    task_tools = server_task._tool_manager._tools
    assert len(task_tools) == 2
    assert "tasks" in task_tools
    assert "task" in task_tools
    assert "tags" not in task_tools
    assert "tag" not in task_tools


def test_feature_filtering_by_string_and_env(monkeypatch):
    # 字符串列表方式指定
    server = create_server(cli_path="/mock/obsidian", features=["property", "task"])
    tools = server._tool_manager._tools
    assert len(tools) == 6  # 4 property + 2 task
    assert "properties" in tools
    assert "tasks" in tools
    assert "tags" not in tools
    assert "read" not in tools

    # 环境变量方式指定
    monkeypatch.setenv("OBSIDIAN_FEATURES", "eval,graph")
    server_env = create_server(cli_path="/mock/obsidian")
    tools_env = server_env._tool_manager._tools
    assert len(tools_env) == 9  # 8 graph + 1 eval
    assert "eval" in tools_env
    assert "backlinks" in tools_env
    assert "read" not in tools_env


def test_feature_plural_not_supported():
    # 复数形式已被移除，不再支持
    server = create_server(cli_path="/mock/obsidian", features=["notes", "tasks"])
    tools = server._tool_manager._tools
    assert len(tools) == 0


def test_feature_preset_standard():
    server = create_server(cli_path="/mock/obsidian", features=["standard"])
    tools = server._tool_manager._tools
    # standard: note (9) + property (4) + tag (2) + task (2) + graph (8) = 25
    assert len(tools) == 25
    assert "read" in tools
    assert "property_read" in tools
    assert "tags" in tools
    assert "tasks" in tools
    assert "backlinks" in tools
    assert "eval" not in tools
    assert "plugin_enable" not in tools
