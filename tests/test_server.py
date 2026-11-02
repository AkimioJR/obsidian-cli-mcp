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


def test_tool_annotations_all_present():
    server = create_server(cli_path="/mock/obsidian")
    tools = server._tool_manager._tools
    assert len(tools) == 45
    for name, tool in tools.items():
        assert tool.annotations is not None, f"Tool {name} is missing annotations"


def test_tool_annotations_hints_classification():
    server = create_server(cli_path="/mock/obsidian")
    tools = server._tool_manager._tools

    read_only_tools = {
        name
        for name, t in tools.items()
        if t.annotations and t.annotations.read_only_hint
    }
    assert len(read_only_tools) == 29
    assert "read" in read_only_tools
    assert "tags" in read_only_tools
    assert "tasks" in read_only_tools
    assert "backlinks" in read_only_tools
    assert "properties" in read_only_tools
    assert "vaults" in read_only_tools

    destructive_tools = {
        name
        for name, t in tools.items()
        if t.annotations and t.annotations.destructive_hint
    }
    assert destructive_tools == {"delete", "eval"}

    non_idempotent_tools = {
        name
        for name, t in tools.items()
        if t.annotations and not t.annotations.idempotent_hint
    }
    assert non_idempotent_tools == {
        "append",
        "command",
        "create",
        "eval",
        "prepend",
        "task",
        "template_insert",
    }

    open_world_tools = {
        name
        for name, t in tools.items()
        if t.annotations and t.annotations.open_world_hint
    }
    assert open_world_tools == {"eval"}


def test_tool_i18n_titles_zh_cn():
    server = create_server(cli_path="/mock/obsidian", lang="zh_CN")
    tools = server._tool_manager._tools

    # Note operations with explicit note context
    assert tools["read"].title == "读取笔记"
    assert (
        tools["read"].annotations is not None
        and tools["read"].annotations.title == "读取笔记"
    )
    assert tools["create"].title == "创建笔记"
    assert tools["append"].title == "追加笔记内容"
    assert (
        tools["append"].annotations is not None
        and tools["append"].annotations.title == "追加笔记内容"
    )
    assert tools["prepend"].title == "前置插入笔记"
    assert (
        tools["prepend"].annotations is not None
        and tools["prepend"].annotations.title == "前置插入笔记"
    )
    assert tools["delete"].title == "删除笔记"

    # Other domains
    assert tools["properties"].title == "查看属性概览"
    assert tools["backlinks"].title == "获取反向链接"
    assert tools["tags"].title == "列出所有标签"
    assert tools["tasks"].title == "多维筛选任务"
    assert tools["vault"].title == "查询当前库信息"
    assert tools["command"].title == "执行命令"
    assert tools["eval"].title == "执行 JavaScript 代码"


def test_tool_i18n_titles_en_us_and_fallback(monkeypatch):
    # Explicit en_US
    server_en = create_server(cli_path="/mock/obsidian", lang="en_US")
    tools_en = server_en._tool_manager._tools
    assert tools_en["read"].title == "Read Note"
    assert tools_en["append"].title == "Append Note Content"
    assert tools_en["prepend"].title == "Prepend Note Content"
    assert tools_en["delete"].title == "Delete Note"

    # Via OBSIDIAN_LANG=zh
    monkeypatch.setenv("OBSIDIAN_LANG", "zh")
    server_zh_env = create_server(cli_path="/mock/obsidian")
    assert server_zh_env._tool_manager._tools["append"].title == "追加笔记内容"

    # Via unrecognized language fallback to en_US
    monkeypatch.setenv("OBSIDIAN_LANG", "invalid_lang")
    server_fallback = create_server(cli_path="/mock/obsidian")
    assert server_fallback._tool_manager._tools["read"].title == "Read Note"


def test_supported_lang_enum_and_methods(monkeypatch):
    from obsidian_cli_mcp.i18n import SupportedLang

    assert SupportedLang.normalize("zh") == SupportedLang.ZH_CN
    assert SupportedLang.normalize("zh-CN") == SupportedLang.ZH_CN
    assert SupportedLang.normalize("en") == SupportedLang.EN_US
    assert SupportedLang.normalize("en-US") == SupportedLang.EN_US
    assert SupportedLang.normalize("fr_FR") is None
    assert SupportedLang.normalize(None) is None

    # tool_title lookup
    assert SupportedLang.ZH_CN.tool_title("note", "read") == "读取笔记"
    assert SupportedLang.EN_US.tool_title("note", "read") == "Read Note"

    # titles property and all_titles
    assert "read" in SupportedLang.ZH_CN.titles["note"]
    assert "read" in SupportedLang.EN_US.titles["note"]
    assert SupportedLang.all_titles()[SupportedLang.ZH_CN] == SupportedLang.ZH_CN.titles

    # tool_title fallback to en_US when missing in zh_CN
    monkeypatch.setitem(
        SupportedLang.EN_US.titles["note"], "mock_tool", "Mock Tool Title"
    )
    assert SupportedLang.ZH_CN.tool_title("note", "mock_tool") == "Mock Tool Title"

    # tool_title returns None when missing in both zh_CN and en_US
    assert SupportedLang.ZH_CN.tool_title("note", "completely_unknown") is None
    assert SupportedLang.EN_US.tool_title("note", "completely_unknown") is None


def test_feature_enum_class_and_instance_methods():
    from mcp.server.mcpserver import MCPServer

    from obsidian_cli_mcp.client import ObsidianClient
    from obsidian_cli_mcp.tools import Feature

    # 1. Feature.resolve
    assert Feature.resolve(Feature.NOTE) == {Feature.NOTE}
    assert Feature.resolve("note") == {Feature.NOTE}
    assert Feature.resolve("minimal") == {Feature.NOTE}
    assert Feature.resolve("standard") == {
        Feature.NOTE,
        Feature.PROPERTY,
        Feature.TAG,
        Feature.TASK,
        Feature.GRAPH,
    }
    assert Feature.resolve("non_existent_feature") == set()

    # 2. Feature.presets
    presets = Feature.presets()
    assert "all" in presets and len(presets["all"]) == 8
    assert "safe" in presets and Feature.EVAL not in presets["safe"]

    # 3. Instance method: feature.register
    server = MCPServer("single-feature-server")
    client = ObsidianClient(cli_path="/mock/obsidian")
    Feature.TAG.register(server, client)
    assert len(server._tool_manager._tools) == 2
    assert "tags" in server._tool_manager._tools
    assert "tag" in server._tool_manager._tools

    # 4. Class method: Feature.register_tools
    server_multi = MCPServer("multi-feature-server")
    Feature.register_tools(server_multi, client, features=["task"])
    assert len(server_multi._tool_manager._tools) == 2
    assert "tasks" in server_multi._tool_manager._tools
    assert "task" in server_multi._tool_manager._tools


def test_package_and_server_version():
    import re
    from pathlib import Path

    import obsidian_cli_mcp
    from obsidian_cli_mcp._version import __version__

    # 1. 验证包导出一致性与基本有效性
    assert obsidian_cli_mcp.__version__ == __version__
    assert isinstance(__version__, str)
    assert __version__ not in ("", "0.0.0.dev")

    # 2. 验证符合语义化版本规范 (SemVer / PEP 440)
    assert re.match(r"^\d+\.\d+\.\d+", __version__) is not None

    # 3. 验证与 pyproject.toml 中的版本号保持动态一致（单一事实来源 SSOT）
    pyproject_file = Path(__file__).resolve().parent.parent / "pyproject.toml"
    if pyproject_file.is_file():
        match = re.search(
            r'^version\s*=\s*["\']([^"\']+)["\']',
            pyproject_file.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        assert match is not None
        assert __version__ == match.group(1)

    # 4. 验证注入到 MCPServer 实例的 version 字段
    server = create_server(cli_path="/mock/obsidian")
    assert server.version == __version__
