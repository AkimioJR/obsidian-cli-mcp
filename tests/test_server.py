from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from mcp.types import CallToolResult, TextContent

from obsidian_cli_mcp.cli import CommandExecutionResult
from obsidian_cli_mcp.server import create_server


def test_server_tools_registered():
    # 默认加载 standard 预设 (5 core + 27 standard = 32)
    server = create_server(cli_path="/mock/obsidian")
    tools = server._tool_manager._tools
    assert len(tools) == 32
    assert "read" in tools
    assert "create" in tools
    assert "tags" in tools
    assert "vaults" in tools
    assert "version" in tools
    assert "reload" in tools
    assert "restart" in tools

    # 显式指定 all 预设时启用全量 56 项工具
    server_all = create_server(cli_path="/mock/obsidian", features=["all"])
    assert len(server_all._tool_manager._tools) == 56


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
    server = create_server(cli_path="/mock/obsidian", features=["all"])
    tools = server._tool_manager._tools
    assert len(tools) == 56
    for tool in tools.values():
        assert tool.description and len(tool.description.strip()) > 0
        assert "properties" in tool.parameters


def test_feature_filtering_single():
    from obsidian_cli_mcp.tools import Feature

    server = create_server(cli_path="/mock/obsidian", features=[Feature.NOTE])
    tools = server._tool_manager._tools
    # 5 core tools (version, vaults, vault, reload, restart) + 11 note tools = 16
    assert len(tools) == 16
    assert "version" in tools
    assert "vaults" in tools
    assert "vault" in tools
    assert "reload" in tools
    assert "restart" in tools
    assert "read" in tools
    assert "create" in tools
    assert "delete" in tools
    # Other features should not be registered
    assert "tags" not in tools
    assert "files" not in tools
    assert "eval" not in tools


def test_feature_tag_and_task_split():
    from obsidian_cli_mcp.tools import Feature

    # Test Feature.TAG
    server_tag = create_server(cli_path="/mock/obsidian", features=[Feature.TAG])
    tag_tools = server_tag._tool_manager._tools
    assert len(tag_tools) == 7  # 5 core + 2 tag
    assert "version" in tag_tools
    assert "tags" in tag_tools
    assert "tag" in tag_tools
    assert "tasks" not in tag_tools
    assert "task" not in tag_tools

    # Test Feature.TASK
    server_task = create_server(cli_path="/mock/obsidian", features=[Feature.TASK])
    task_tools = server_task._tool_manager._tools
    assert len(task_tools) == 7  # 5 core + 2 task
    assert "version" in task_tools
    assert "tasks" in task_tools
    assert "task" in task_tools
    assert "tags" not in task_tools
    assert "tag" not in task_tools


def test_feature_filtering_by_string_and_env(monkeypatch):
    # 字符串列表方式指定
    server = create_server(cli_path="/mock/obsidian", features=["property", "task"])
    tools = server._tool_manager._tools
    assert len(tools) == 11  # 5 core + 4 property + 2 task
    assert "version" in tools
    assert "properties" in tools
    assert "tasks" in tools
    assert "tags" not in tools
    assert "read" not in tools

    # 环境变量方式指定
    monkeypatch.setenv("OBSIDIAN_FEATURES", "developer,graph")
    server_env = create_server(cli_path="/mock/obsidian")
    tools_env = server_env._tool_manager._tools
    assert len(tools_env) == 14  # 5 core + 8 graph + 1 eval
    assert "version" in tools_env
    assert "eval" in tools_env
    assert "backlinks" in tools_env
    assert "read" not in tools_env


def test_feature_plural_not_supported():
    # 复数形式已被移除，不再支持；仅保留 5 个必须的基础核心工具
    server = create_server(cli_path="/mock/obsidian", features=["notes", "tasks"])
    tools = server._tool_manager._tools
    assert len(tools) == 5
    assert "version" in tools
    assert "vaults" in tools
    assert "vault" in tools
    assert "reload" in tools
    assert "restart" in tools
    assert "read" not in tools


def test_core_tools_always_registered():
    # 即使 features 显式设置为空列表，核心探测工具也必须默认注册
    server = create_server(cli_path="/mock/obsidian", features=[])
    tools = server._tool_manager._tools
    assert len(tools) == 5
    assert "version" in tools
    assert "vaults" in tools
    assert "vault" in tools
    assert "reload" in tools
    assert "restart" in tools
    assert tools["version"].title == "Show Obsidian Version"
    assert tools["vaults"].title == "List All Vaults"
    assert tools["vault"].title == "Show Vault Info"
    assert tools["reload"].title == "Reload Vault"
    assert tools["restart"].title == "Restart Obsidian"


def test_feature_preset_standard():
    server = create_server(cli_path="/mock/obsidian", features=["standard"])
    tools = server._tool_manager._tools
    # standard: 5 core + 27 standard (note 11 + property 4 + tag 2 + task 2 + graph 8) = 32
    assert len(tools) == 32
    assert "read" in tools
    assert "property_read" in tools
    assert "tags" in tools
    assert "tasks" in tools
    assert "backlinks" in tools
    assert "eval" not in tools
    assert "plugin_enable" not in tools


def test_tool_annotations_all_present():
    server = create_server(cli_path="/mock/obsidian", features=["all"])
    tools = server._tool_manager._tools
    assert len(tools) == 56
    for name, tool in tools.items():
        assert tool.annotations is not None, f"Tool {name} is missing annotations"


def test_tool_annotations_hints_classification():
    server = create_server(cli_path="/mock/obsidian", features=["all"])
    tools = server._tool_manager._tools

    read_only_tools = {
        name
        for name, t in tools.items()
        if t.annotations and t.annotations.read_only_hint
    }
    assert len(read_only_tools) == 36
    assert "read" in read_only_tools
    assert "tags" in read_only_tools
    assert "tasks" in read_only_tools
    assert "backlinks" in read_only_tools
    assert "properties" in read_only_tools
    assert "vaults" in read_only_tools
    assert "base_query" in read_only_tools

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
        "bookmark",
        "command",
        "create",
        "eval",
        "prepend",
        "random",
        "tab_open",
        "base_create",
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
    server = create_server(cli_path="/mock/obsidian", lang="zh_CN", features=["all"])
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
    assert Feature.resolve(Feature.DEVELOPER) == {Feature.DEVELOPER}
    assert Feature.resolve("developer") == {Feature.DEVELOPER}
    assert Feature.resolve("eval") == set()
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
    assert "all" in presets and len(presets["all"]) == 10
    assert "safe" in presets and Feature.DEVELOPER not in presets["safe"]
    assert Feature.EXPLORER in presets["safe"]
    assert Feature.WORKSPACE in presets["safe"]

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


def test_server_timeout_configuration(monkeypatch):
    # 1. 支持通过参数传入 float 超时
    server_custom = create_server(cli_path="/mock/obsidian", timeout=15.5)
    assert server_custom is not None

    # 2. 支持环境变量 OBSIDIAN_TIMEOUT 传入 float
    monkeypatch.setenv("OBSIDIAN_TIMEOUT", "45.0")
    server_env = create_server(cli_path="/mock/obsidian")
    assert server_env is not None


@pytest.mark.asyncio
async def test_tool_registrar_extension_guard():
    from mcp.server.mcpserver import MCPServer

    from obsidian_cli_mcp.tools.base import READ_ONLY, ToolRegistrar

    # 1. enable_extensions=False 时，标记为 extension=True 的工具跳过注册
    srv_disabled = MCPServer(name="test_disabled")
    reg_disabled = ToolRegistrar(srv_disabled, "note", enable_extensions=False)

    @reg_disabled.tool(name="custom_ext_tool", annotations=READ_ONLY, extension=True)
    async def disabled_fn():
        return "ok"

    tools_disabled = await srv_disabled.list_tools()
    assert "custom_ext_tool" not in {t.name for t in tools_disabled}

    # 2. enable_extensions=True 时，标记为 extension=True 的工具正常注册
    srv_enabled = MCPServer(name="test_enabled")
    reg_enabled = ToolRegistrar(srv_enabled, "note", enable_extensions=True)

    @reg_enabled.tool(name="custom_ext_tool", annotations=READ_ONLY, extension=True)
    async def enabled_fn():
        return "ok"

    tools_enabled = await srv_enabled.list_tools()
    assert "custom_ext_tool" in {t.name for t in tools_enabled}


@pytest.mark.asyncio
async def test_server_enable_extensions_env_and_param(monkeypatch):
    from unittest.mock import patch as mock_patch

    # 1. 默认环境下（未设置环境变量），enable_extensions 为 False
    monkeypatch.delenv("OBSIDIAN_EXTENSIONS", raising=False)

    with mock_patch("obsidian_cli_mcp.tools.Feature.register_tools") as mock_reg:
        create_server(cli_path="/mock/obsidian")
        mock_reg.assert_called_once()
        assert mock_reg.call_args.kwargs["enable_extensions"] is False

    # 2. 显式参数 enable_extensions 覆盖
    with mock_patch("obsidian_cli_mcp.tools.Feature.register_tools") as mock_reg:
        create_server(cli_path="/mock/obsidian", enable_extensions=True)
        mock_reg.assert_called_once()
        assert mock_reg.call_args.kwargs["enable_extensions"] is True

    with mock_patch("obsidian_cli_mcp.tools.Feature.register_tools") as mock_reg:
        create_server(cli_path="/mock/obsidian", enable_extensions=False)
        mock_reg.assert_called_once()
        assert mock_reg.call_args.kwargs["enable_extensions"] is False

    # 3. 严格仅支持 "true"（不区分大小写）
    for val in ("true", "True", "TRUE", "TrUe", "  true  "):
        monkeypatch.setenv("OBSIDIAN_EXTENSIONS", val)
        with mock_patch("obsidian_cli_mcp.tools.Feature.register_tools") as mock_reg:
            create_server(cli_path="/mock/obsidian")
            mock_reg.assert_called_once()
            assert mock_reg.call_args.kwargs["enable_extensions"] is True

    # 4. 其余任何值（如 1, yes, on, false, 0 等）均严格为 False
    for val in (
        "1",
        "yes",
        "on",
        "enable",
        "false",
        "False",
        "0",
        "no",
        "off",
        "",
        "none",
        "random",
    ):
        monkeypatch.setenv("OBSIDIAN_EXTENSIONS", val)
        with mock_patch("obsidian_cli_mcp.tools.Feature.register_tools") as mock_reg:
            create_server(cli_path="/mock/obsidian")
            mock_reg.assert_called_once()
            assert mock_reg.call_args.kwargs["enable_extensions"] is False

    # 5. 严格仅识别 OBSIDIAN_EXTENSIONS，不识别其他别名
    monkeypatch.delenv("OBSIDIAN_EXTENSIONS", raising=False)
    monkeypatch.setenv("OBSIDIAN_ENABLE_EXTENSIONS", "true")
    monkeypatch.setenv("OBSIDIAN_EXTRA_TOOLS", "true")
    with mock_patch("obsidian_cli_mcp.tools.Feature.register_tools") as mock_reg:
        create_server(cli_path="/mock/obsidian")
        mock_reg.assert_called_once()
        assert mock_reg.call_args.kwargs["enable_extensions"] is False


def test_register_tools_enforces_keyword_only_parameters():
    import inspect

    from obsidian_cli_mcp.tools import (
        register_base_tools,
        register_core_tools,
        register_developer_tools,
        register_explorer_tools,
        register_graph_tools,
        register_note_tools,
        register_plugin_tools,
        register_property_tools,
        register_tag_tools,
        register_task_tools,
        register_workspace_tools,
    )

    all_reg_funcs = [
        register_base_tools,
        register_core_tools,
        register_developer_tools,
        register_graph_tools,
        register_explorer_tools,
        register_note_tools,
        register_plugin_tools,
        register_property_tools,
        register_tag_tools,
        register_task_tools,
        register_workspace_tools,
    ]

    for fn in all_reg_funcs:
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())

        # 前两个参数必须是位置参数 (server, client)
        assert params[0].name == "server"
        assert params[0].kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.POSITIONAL_ONLY,
        )
        assert params[1].name == "client"
        assert params[1].kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.POSITIONAL_ONLY,
        )

        # lang, version, enable_extensions 必须是 KEYWORD_ONLY
        for p in params[2:]:
            assert p.kind == inspect.Parameter.KEYWORD_ONLY, (
                f"{fn.__name__} parameter '{p.name}' is not KEYWORD_ONLY (got {p.kind})"
            )


def _extract_tool_text(res: Any) -> str:
    assert isinstance(res, CallToolResult)
    item = res.content[0]
    assert isinstance(item, TextContent)
    return item.text


@pytest.mark.asyncio
async def test_edit_tool_registration(monkeypatch):
    # 1. 默认未开启扩展时，edit 不注册
    monkeypatch.delenv("OBSIDIAN_EXTENSIONS", raising=False)
    server_default = create_server(cli_path="/mock/obsidian")
    tools_default = await server_default.list_tools()
    assert "edit" not in {t.name for t in tools_default}

    # 2. 显式开启 enable_extensions 时，edit 作为 note 的扩展工具注册
    server_ext = create_server(cli_path="/mock/obsidian", enable_extensions=True)
    tools_ext = await server_ext.list_tools()
    tool_map = {t.name: t for t in tools_ext}
    assert "edit" in tool_map
    edit_tool = tool_map["edit"]
    assert edit_tool.annotations is not None
    assert edit_tool.annotations.read_only_hint is False
    assert edit_tool.title in ("编辑修改笔记", "Edit Note Content")

    # 3. 环境变量 OBSIDIAN_EXTENSIONS=true 时注册
    monkeypatch.setenv("OBSIDIAN_EXTENSIONS", "true")
    server_env = create_server(cli_path="/mock/obsidian")
    tools_env = await server_env.list_tools()
    assert "edit" in {t.name for t in tools_env}

    # 4. 未启用 note 特性时（如只启用 property），即使开启扩展也不注册 edit
    server_no_note = create_server(
        cli_path="/mock/obsidian",
        features=["property"],
        enable_extensions=True,
    )
    tools_no_note = await server_no_note.list_tools()
    assert "edit" not in {t.name for t in tools_no_note}


@pytest.mark.asyncio
async def test_edit_tool_execution():
    from unittest.mock import AsyncMock, patch

    server = create_server(cli_path="/mock/obsidian", enable_extensions=True)

    # 模拟底层的 CLI 执行 (先 read，再 create)
    mock_run = AsyncMock()
    mock_run.side_effect = [
        # read 结果
        CommandExecutionResult(
            returncode=0,
            stdout="# My Note\n\nOriginal line\nFooter",
            stderr="",
        ),
        # create overwrite 结果
        CommandExecutionResult(
            returncode=0,
            stdout="",
            stderr="",
        ),
    ]

    with patch("obsidian_cli_mcp.client.run_cli_command", new=mock_run):
        res = await server.call_tool(
            "edit",
            {
                "file": "MyNote.md",
                "old_str": "Original line",
                "new_str": "Modified content",
            },
        )
        assert isinstance(res, CallToolResult)
        assert not res.is_error
        text = _extract_tool_text(res)
        assert (
            "The file 'MyNote.md' has been updated successfully (1 occurrence(s) replaced)."
            in text
        )

        # 验证 create 命令参数收到的文本确实包含替换后的内容
        assert mock_run.call_count == 2
        create_call_args = mock_run.call_args_list[1][0][1]
        assert "create" in create_call_args
        assert any(
            "content=# My Note\n\nModified content\nFooter" in arg
            for arg in create_call_args
        )


@pytest.mark.asyncio
async def test_edit_tool_validation_and_errors():
    from unittest.mock import AsyncMock, patch

    server = create_server(cli_path="/mock/obsidian", enable_extensions=True)

    # 1. 没有 file 也没有 path
    res1 = await server.call_tool("edit", {"old_str": "a", "new_str": "b"})
    assert "Either 'file' or 'path' must be provided" in _extract_tool_text(res1)

    # 2. old_str 为空
    res2 = await server.call_tool(
        "edit", {"file": "Test.md", "old_str": "", "new_str": "b"}
    )
    assert "'old_str' must not be empty" in _extract_tool_text(res2)

    # 3. old_str == new_str (直接返回无变动)
    res3 = await server.call_tool(
        "edit", {"file": "Test.md", "old_str": "same", "new_str": "same"}
    )
    assert "No changes needed" in _extract_tool_text(res3)

    # 4. 未找到目标内容 (count == 0)
    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0, stdout="Some file content", stderr=""
            )
        ),
    ):
        res4 = await server.call_tool(
            "edit",
            {"file": "Test.md", "old_str": "NonExistentText", "new_str": "NewText"},
        )
        assert "Target string not found" in _extract_tool_text(res4)

    # 5. 出现多次匹配且 replace_all 为 False (要求唯一性)
    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0, stdout="apple orange apple banana", stderr=""
            )
        ),
    ):
        res5 = await server.call_tool(
            "edit",
            {
                "file": "Test.md",
                "old_str": "apple",
                "new_str": "pear",
                "replace_all": False,
            },
        )
        text5 = _extract_tool_text(res5)
        assert "Found 2 occurrences of 'old_str'" in text5
        assert "replace_all is false" in text5

    # 6. 出现多次匹配但 replace_all 为 True (全部替换成功)
    mock_multi = AsyncMock()
    mock_multi.side_effect = [
        CommandExecutionResult(returncode=0, stdout="apple orange apple", stderr=""),
        CommandExecutionResult(returncode=0, stdout="", stderr=""),
    ]
    with patch("obsidian_cli_mcp.client.run_cli_command", new=mock_multi):
        res6 = await server.call_tool(
            "edit",
            {
                "file": "Test.md",
                "old_str": "apple",
                "new_str": "pear",
                "replace_all": True,
            },
        )
        assert "updated successfully (2 occurrence(s) replaced)" in _extract_tool_text(
            res6
        )

    # 7. 删除操作 (new_str 为空字符串)
    mock_del = AsyncMock()
    mock_del.side_effect = [
        CommandExecutionResult(returncode=0, stdout="delete me please", stderr=""),
        CommandExecutionResult(returncode=0, stdout="", stderr=""),
    ]
    with patch("obsidian_cli_mcp.client.run_cli_command", new=mock_del):
        res7 = await server.call_tool(
            "edit",
            {
                "file": "Test.md",
                "old_str": " me",
                "new_str": "",
                "replace_all": False,
            },
        )
        assert "updated successfully (1 occurrence(s) replaced)" in _extract_tool_text(
            res7
        )
        create_args = mock_del.call_args_list[1][0][1]
        assert any("content=delete please" in arg for arg in create_args)


@pytest.mark.asyncio
async def test_import_file_tool_registration(monkeypatch):
    # 1. 默认未开启扩展时，import_file 不注册
    monkeypatch.delenv("OBSIDIAN_EXTENSIONS", raising=False)
    server_default = create_server(cli_path="/mock/obsidian")
    tools_default = await server_default.list_tools()
    assert "import_file" not in {t.name for t in tools_default}

    # 2. 显式开启 enable_extensions 时，import_file 作为 note 的扩展工具注册
    server_ext = create_server(cli_path="/mock/obsidian", enable_extensions=True)
    tools_ext = await server_ext.list_tools()
    tool_map = {t.name: t for t in tools_ext}
    assert "import_file" in tool_map
    import_tool = tool_map["import_file"]
    assert import_tool.annotations is not None
    assert import_tool.annotations.read_only_hint is False
    assert import_tool.title in ("导入外部文件", "Import External File")


@pytest.mark.asyncio
async def test_import_file_validation_and_errors(tmp_path):
    from unittest.mock import AsyncMock, patch

    server = create_server(cli_path="/mock/obsidian", enable_extensions=True)

    # 1. source_path 为空
    res1 = await server.call_tool("import_file", {"source_path": ""})
    assert "'source_path' must be provided" in _extract_tool_text(res1)

    # 2. source_path 文件不存在
    res2 = await server.call_tool(
        "import_file", {"source_path": str(tmp_path / "nonexistent.md")}
    )
    assert "does not exist" in _extract_tool_text(res2)

    # 3. source_path 是目录而非文件
    test_dir = tmp_path / "somedir"
    test_dir.mkdir()
    res3 = await server.call_tool("import_file", {"source_path": str(test_dir)})
    assert "not a regular file" in _extract_tool_text(res3)

    # 4. 路径遍历跨越库目录 (Path Traversal)
    valid_file = tmp_path / "test.md"
    valid_file.write_text("sample content", encoding="utf-8")
    mock_vault_dir = tmp_path / "mock_vault"
    mock_vault_dir.mkdir()

    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0, stdout=str(mock_vault_dir), stderr=""
            )
        ),
    ):
        res4 = await server.call_tool(
            "import_file",
            {"source_path": str(valid_file), "path": "../../escaped.md"},
        )
        assert "resolves outside the vault directory" in _extract_tool_text(res4)

    # 5. 目标已存在且 overwrite=False
    existing_dest = mock_vault_dir / "already_exists.md"
    existing_dest.write_text("old", encoding="utf-8")
    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0, stdout=str(mock_vault_dir), stderr=""
            )
        ),
    ):
        res5 = await server.call_tool(
            "import_file",
            {
                "source_path": str(valid_file),
                "path": "already_exists.md",
                "overwrite": False,
            },
        )
        assert "already exists in vault" in _extract_tool_text(res5)


@pytest.mark.asyncio
async def test_import_file_copy_and_move(tmp_path):
    from unittest.mock import AsyncMock, patch

    server = create_server(cli_path="/mock/obsidian", enable_extensions=True)
    mock_vault_dir = tmp_path / "vault_root"
    mock_vault_dir.mkdir()

    # 1. 测试常规复制 (move=False)
    src_file1 = tmp_path / "workspace_doc.md"
    src_file1.write_text("# Hello Obsidian\nZero JSON escaping!", encoding="utf-8")

    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0, stdout=str(mock_vault_dir), stderr=""
            )
        ),
    ):
        res1 = await server.call_tool(
            "import_file",
            {
                "source_path": str(src_file1),
                "path": "Deep/Folder/imported.md",
                "move": False,
            },
        )
        assert "successfully copied into the vault" in _extract_tool_text(res1)
        dest1 = mock_vault_dir / "Deep" / "Folder" / "imported.md"
        assert dest1.is_file()
        assert dest1.read_text(encoding="utf-8") == src_file1.read_text(
            encoding="utf-8"
        )
        assert src_file1.is_file()  # copy 保持源文件依然存在

    # 2. 测试剪切移动 (move=True)
    src_file2 = tmp_path / "workspace_moved.md"
    src_file2.write_text("move me into vault", encoding="utf-8")

    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0, stdout=str(mock_vault_dir), stderr=""
            )
        ),
    ):
        res2 = await server.call_tool(
            "import_file",
            {
                "source_path": str(src_file2),
                "path": "moved.md",
                "move": True,
            },
        )
        assert "successfully moved into the vault" in _extract_tool_text(res2)
        dest2 = mock_vault_dir / "moved.md"
        assert dest2.is_file()
        assert dest2.read_text(encoding="utf-8") == "move me into vault"
        assert not src_file2.exists()  # move 剪切后源文件不再存在


@pytest.mark.asyncio
async def test_set_default_vault_registration(monkeypatch):
    # 1. 默认未开启扩展时，set_default_vault 不注册
    monkeypatch.delenv("OBSIDIAN_EXTENSIONS", raising=False)
    server_default = create_server(cli_path="/mock/obsidian")
    tools_default = await server_default.list_tools()
    assert "set_default_vault" not in {t.name for t in tools_default}

    # 2. 显式开启 enable_extensions 时，set_default_vault 在核心工具中注册
    server_ext = create_server(cli_path="/mock/obsidian", enable_extensions=True)
    tools_ext = await server_ext.list_tools()
    tool_map = {t.name: t for t in tools_ext}
    assert "set_default_vault" in tool_map
    set_vault_tool = tool_map["set_default_vault"]
    assert set_vault_tool.annotations is not None
    assert set_vault_tool.annotations.idempotent_hint is True
    assert set_vault_tool.title in ("切换默认笔记库", "Set Default Vault")


@pytest.mark.asyncio
async def test_set_default_vault_execution_and_switching():
    from unittest.mock import AsyncMock, patch

    server = create_server(cli_path="/mock/obsidian", enable_extensions=True)

    # 1. 设置默认笔记库为已知存在的 "ScholarHub"
    mock_run = AsyncMock()
    mock_run.side_effect = [
        # vaults 输出
        CommandExecutionResult(
            returncode=0,
            stdout="ScholarHub\t/path/to/sh\nWork\t/path/to/work",
            stderr="",
        ),
        # 后续 read 调用的输出
        CommandExecutionResult(returncode=0, stdout="content of note", stderr=""),
        # 带有覆盖参数 vault="Work" 的 read 调用
        CommandExecutionResult(returncode=0, stdout="content of work note", stderr=""),
    ]

    with patch("obsidian_cli_mcp.client.run_cli_command", new=mock_run):
        # 调用 set_default_vault
        res1 = await server.call_tool("set_default_vault", {"vault": "ScholarHub"})
        assert (
            "Default vault successfully switched from '(none)' to 'ScholarHub'"
            in _extract_tool_text(res1)
        )

        # 接下来调用 read 工具（未显式传递 vault 参数），验证底层自动附加 vault=ScholarHub
        res2 = await server.call_tool("read", {"file": "TestNote.md"})
        assert isinstance(res2, CallToolResult)
        assert not res2.is_error
        read_args = mock_run.call_args_list[1][0][1]
        assert "vault=ScholarHub" in read_args

        # 临时调用需要访问 Work 库（显式传参 vault="Work"），验证单次覆盖生效
        res3 = await server.call_tool("read", {"file": "WorkNote.md", "vault": "Work"})
        assert isinstance(res3, CallToolResult)
        assert not res3.is_error
        read_work_args = mock_run.call_args_list[2][0][1]
        assert "vault=Work" in read_work_args


@pytest.mark.asyncio
async def test_set_default_vault_validation_and_reset():
    from unittest.mock import AsyncMock, patch

    server = create_server(cli_path="/mock/obsidian", enable_extensions=True)

    # 1. 尝试切换到不存在的未知库
    with patch(
        "obsidian_cli_mcp.client.run_cli_command",
        new=AsyncMock(
            return_value=CommandExecutionResult(
                returncode=0, stdout="ScholarHub\nPersonal", stderr=""
            )
        ),
    ):
        res_unknown = await server.call_tool(
            "set_default_vault", {"vault": "NonExistentVault"}
        )
        text_unknown = _extract_tool_text(res_unknown)
        assert (
            "Error: Vault 'NonExistentVault' not found among known vaults"
            in text_unknown
        )

    # 2. 清空/重置默认笔记库 (传入空字符串或 None)
    res_clear = await server.call_tool("set_default_vault", {"vault": ""})
    text_clear = _extract_tool_text(res_clear)
    assert "Default vault cleared" in text_clear
    assert "Subsequent tool calls will target Obsidian's active vault" in text_clear


@pytest.mark.asyncio
async def test_feature_explorer_and_workspace_registration_and_titles():
    from obsidian_cli_mcp.tools import Feature

    # 1. Registration Explorer (5 core + 5 explorer = 10)
    server_exp = create_server(cli_path="/mock/obsidian", features=[Feature.EXPLORER])
    exp_tools = server_exp._tool_manager._tools
    assert len(exp_tools) == 10
    expected_exp = {"files", "file", "folders", "folder", "recents"}
    assert expected_exp.issubset(exp_tools.keys())

    # 2. Registration Workspace (5 core + 5 workspace = 10)
    server_ws = create_server(cli_path="/mock/obsidian", features=[Feature.WORKSPACE])
    ws_tools = server_ws._tool_manager._tools
    assert len(ws_tools) == 10
    expected_ws = {"workspace", "tabs", "tab_open", "bookmarks", "bookmark"}
    assert expected_ws.issubset(ws_tools.keys())

    # 3. Titles in zh_CN
    server_zh = create_server(
        cli_path="/mock/obsidian",
        lang="zh_CN",
        features=[Feature.EXPLORER, Feature.WORKSPACE],
    )
    tools_zh = server_zh._tool_manager._tools
    assert tools_zh["file"].title == "查询文件信息"
    assert tools_zh["files"].title == "检索库内文件"
    assert tools_zh["folders"].title == "列出文件夹目录"
    assert tools_zh["folder"].title == "查询文件夹详情"
    assert tools_zh["recents"].title == "列出最近访问文件"
    assert tools_zh["workspace"].title == "查询工作区布局"
    assert tools_zh["tabs"].title == "列出打开的标签页"
    assert tools_zh["tab_open"].title == "打开新标签页"
    assert tools_zh["bookmarks"].title == "查看书签星标"
    assert tools_zh["bookmark"].title == "添加书签"

    # 4. Titles in en_US
    server_en = create_server(
        cli_path="/mock/obsidian",
        lang="en_US",
        features=[Feature.EXPLORER, Feature.WORKSPACE],
    )
    tools_en = server_en._tool_manager._tools
    assert tools_en["file"].title == "Show File Details"
    assert tools_en["files"].title == "List Files in Vault"
    assert tools_en["folders"].title == "List Folders"
    assert tools_en["folder"].title == "Show Folder Details"
    assert tools_en["recents"].title == "List Recent Files"
    assert tools_en["workspace"].title == "Get Workspace Layout"
    assert tools_en["tabs"].title == "List Open Tabs"
    assert tools_en["tab_open"].title == "Open New Tab"
    assert tools_en["bookmarks"].title == "List Bookmarks"
    assert tools_en["bookmark"].title == "Add Bookmark"


@pytest.mark.asyncio
async def test_feature_explorer_and_workspace_tool_executions():
    from unittest.mock import AsyncMock, patch

    from obsidian_cli_mcp.tools import Feature

    server = create_server(
        cli_path="/mock/obsidian", features=[Feature.EXPLORER, Feature.WORKSPACE]
    )

    mock_run = AsyncMock(
        return_value=CommandExecutionResult(
            returncode=0, stdout="mock_output", stderr=""
        )
    )

    with patch("obsidian_cli_mcp.client.run_cli_command", new=mock_run):
        # 1. file in explorer
        res_file = await server.call_tool(
            "file", {"file": "TestNote", "path": "Docs/TestNote.md"}
        )
        assert _extract_tool_text(res_file) == "mock_output"
        assert mock_run.call_args_list[0][0][1] == [
            "file",
            "file=TestNote",
            "path=Docs/TestNote.md",
        ]

        # 2. bookmark in workspace
        res_bm = await server.call_tool(
            "bookmark",
            {
                "file": "MyNote.md",
                "subpath": "#Heading",
                "folder": "Docs",
                "search": "tag:#todo",
                "url": "https://obsidian.md",
                "title": "My Bookmark",
                "vault": "WorkVault",
            },
        )
        assert _extract_tool_text(res_bm) == "mock_output"
        assert mock_run.call_args_list[1][0][1] == [
            "bookmark",
            "file=MyNote.md",
            "subpath=#Heading",
            "folder=Docs",
            "search=tag:#todo",
            "url=https://obsidian.md",
            "title=My Bookmark",
            "vault=WorkVault",
        ]

        # 3. tabs in workspace
        res_tabs = await server.call_tool("tabs", {"ids": True})
        assert _extract_tool_text(res_tabs) == "mock_output"
        assert mock_run.call_args_list[2][0][1] == ["tabs", "ids"]

        # 4. tab_open in workspace
        res_to = await server.call_tool(
            "tab_open",
            {"file": "Note.md", "group": "group-1", "view": "markdown"},
        )
        assert _extract_tool_text(res_to) == "mock_output"
        assert mock_run.call_args_list[3][0][1] == [
            "tab:open",
            "file=Note.md",
            "group=group-1",
            "view=markdown",
        ]


@pytest.mark.asyncio
async def test_core_reload_and_restart_execution():
    server = create_server(cli_path="/mock/obsidian", features=[])
    mock_run = AsyncMock(
        return_value=CommandExecutionResult(
            returncode=0, stdout="mock_output", stderr=""
        )
    )

    with patch("obsidian_cli_mcp.client.run_cli_command", new=mock_run):
        # 1. reload without vault
        res1 = await server.call_tool("reload", {})
        assert _extract_tool_text(res1) == "mock_output"
        assert mock_run.call_args_list[0][0][1] == ["reload"]

        # 2. reload with vault
        res2 = await server.call_tool("reload", {"vault": "MyVault"})
        assert _extract_tool_text(res2) == "mock_output"
        assert mock_run.call_args_list[1][0][1] == ["reload", "vault=MyVault"]

        # 3. restart
        res3 = await server.call_tool("restart", {})
        assert _extract_tool_text(res3) == "mock_output"
        assert mock_run.call_args_list[2][0][1] == ["restart"]


@pytest.mark.asyncio
async def test_note_diff_random_and_plugin_templates():
    from unittest.mock import AsyncMock, patch

    from obsidian_cli_mcp.tools import Feature

    server = create_server(
        cli_path="/mock/obsidian", features=[Feature.NOTE, Feature.PLUGIN]
    )
    mock_run = AsyncMock(
        return_value=CommandExecutionResult(
            returncode=0, stdout="mock_output", stderr=""
        )
    )

    with patch("obsidian_cli_mcp.client.run_cli_command", new=mock_run):
        # 1. diff in note
        res_diff = await server.call_tool(
            "diff",
            {
                "file": "TestNote",
                "path": "Docs/TestNote.md",
                "from_version": 1,
                "to_version": 5,
                "filter": "local",
            },
        )
        assert _extract_tool_text(res_diff) == "mock_output"
        assert mock_run.call_args_list[0][0][1] == [
            "diff",
            "file=TestNote",
            "path=Docs/TestNote.md",
            "from=1",
            "to=5",
            "filter=local",
        ]

        # 2. random in note
        res_rnd = await server.call_tool(
            "random", {"folder": "Articles", "newtab": True}
        )
        assert _extract_tool_text(res_rnd) == "mock_output"
        assert mock_run.call_args_list[1][0][1] == [
            "random",
            "folder=Articles",
            "newtab",
        ]

        # 3. templates in plugin
        res_tpl = await server.call_tool(
            "templates", {"total": True, "vault": "WorkVault"}
        )
        assert _extract_tool_text(res_tpl) == "mock_output"
        assert mock_run.call_args_list[2][0][1] == [
            "templates",
            "total",
            "vault=WorkVault",
        ]
