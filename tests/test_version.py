from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from mcp.server.mcpserver import MCPServer

from obsidian_cli_mcp.client import ObsidianClient
from obsidian_cli_mcp.server import create_server
from obsidian_cli_mcp.tools.base import READ_ONLY, ToolRegistrar
from obsidian_cli_mcp.version import Version


def test_version_parse_success():
    # 1. 标准 x.y.z
    v1 = Version.parse("1.14.5")
    assert v1.major == 1
    assert v1.minor == 14
    assert v1.patch == 5
    assert str(v1) == "1.14.5"

    # 2. 短版本号 x.y
    v2 = Version.parse("1.15")
    assert v2 == Version(1, 15, 0)
    assert str(v2) == "1.15.0"

    # 3. 带 v 前缀
    v3 = Version.parse("v2.0.1")
    assert v3 == Version(2, 0, 1)

    # 4. 实际 Obsidian CLI 返回格式 "1.14.5 (installer 1.14.5)"
    v4 = Version.parse("1.14.5 (installer 1.14.5)")
    assert v4 == Version(1, 14, 5)

    # 5. 空白符处理
    v5 = Version.parse("  0.9.12 \n")
    assert v5 == Version(0, 9, 12)


def test_version_parse_invalid():
    with pytest.raises(ValueError, match="Invalid version string"):
        Version.parse("invalid_version")

    with pytest.raises(ValueError, match="Invalid version string"):
        Version.parse("")

    with pytest.raises(TypeError):
        Version.parse(cast(str, 123))


def test_version_try_parse():
    assert Version.try_parse(None) is None
    assert Version.try_parse("") is None
    assert Version.try_parse("not_a_version") is None
    assert Version.try_parse("1.14.5") == Version(1, 14, 5)


def test_version_comparisons():
    v1 = Version(1, 14, 5)
    v2 = Version(1, 14, 0)
    v3 = Version(1, 15, 0)
    v4 = Version(2, 0, 0)

    # 1. 实例间比较
    assert v1 > v2
    assert v1 >= v2
    assert v2 < v1
    assert v2 <= v1
    assert v1 < v3
    assert v3 < v4
    assert v1 != v3
    assert v1 == Version(1, 14, 5)

    # 2. 与字符串直接比较
    assert v1 > "1.14.0"
    assert v1 >= "1.14.5"
    assert v1 <= "1.14.5"
    assert v1 < "1.15.0"
    assert v1 == "1.14.5"
    assert v1 != "1.14.6"

    # 3. 字符串与 Version 反射比较
    assert "1.14.0" < v1
    assert "1.15.0" > v1
    assert "1.14.5" == v1

    # 4. 非法类型相等性返回 False，不等性返回 True
    assert (v1 == 123) is False
    assert (v1 != 123) is True


def test_version_hashable():
    # 测试在 set 和 dict 中的可用性
    v_set = {Version(1, 14, 5), Version(1, 14, 5), Version(1, 15, 0)}
    assert len(v_set) == 2


def test_tool_registrar_version_filtering():
    server = MCPServer("test-version-server")

    # 场景 1: 当前版本 1.14.5
    current_ver = Version(1, 14, 5)
    reg = ToolRegistrar(server, "test_feature", version=current_ver)

    # 工具 A: 需要最低 1.14.0 (满足)
    @reg.tool(name="tool_a", annotations=READ_ONLY, min_version="1.14.0")
    async def tool_a():
        return "a"

    # 工具 B: 需要最低 1.15.0 (不满足，应跳过注册)
    @reg.tool(name="tool_b", annotations=READ_ONLY, min_version="1.15.0")
    async def tool_b():
        return "b"

    # 工具 C: 最高支持到 1.14.0 (已废弃/超期，应跳过注册)
    @reg.tool(name="tool_c", annotations=READ_ONLY, max_version="1.14.0")
    async def tool_c():
        return "c"

    # 工具 D: 无版本限制 (满足)
    @reg.tool(name="tool_d", annotations=READ_ONLY)
    async def tool_d():
        return "d"

    registered = server._tool_manager._tools
    assert "tool_a" in registered
    assert "tool_d" in registered
    assert "tool_b" not in registered
    assert "tool_c" not in registered


def test_client_get_version(monkeypatch):
    # 1. 优先读取 OBSIDIAN_VERSION 环境变量
    monkeypatch.setenv("OBSIDIAN_VERSION", "1.16.2")
    client_env = ObsidianClient(cli_path="/mock/obsidian")
    assert client_env.get_version() == Version(1, 16, 2)

    # 2. 模拟 subprocess 真实返回
    monkeypatch.delenv("OBSIDIAN_VERSION", raising=False)
    client_subproc = ObsidianClient(cli_path="/mock/obsidian")
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "1.14.5 (installer 1.14.5)"

    with patch("subprocess.run", return_value=mock_proc):
        assert client_subproc.get_version() == Version(1, 14, 5)

    # 3. 模拟可执行文件不存在或执行异常，安全回退到 None
    with patch("subprocess.run", side_effect=OSError):
        assert client_subproc.get_version() is None


def test_create_server_with_obsidian_version(monkeypatch):
    # 支持在 create_server 中显式传入 obsidian_version 字符串或 Version 对象
    server = create_server(
        cli_path="/mock/obsidian",
        obsidian_version="1.14.5",
    )
    assert server is not None


def test_server_version_evolution_v1_12_0():
    # 在 1.12.0 版本下：
    # 1. rename 尚未引入，不应被注册 (min_version="1.12.1")
    # 2. base 相关工具尚未引入，不应被注册 (min_version="1.14.0")
    # 3. append/prepend 应初始化为无 heading 参数的历史版本
    server = create_server(
        cli_path="/mock/obsidian",
        obsidian_version="1.12.0",
        features=["all"],
    )
    tools = server._tool_manager._tools

    assert "rename" not in tools
    assert "bases" not in tools
    assert "base_query" not in tools
    assert "append" in tools
    assert "prepend" in tools

    append_params = tools["append"].parameters["properties"]
    assert "heading" not in append_params
    assert "content" in append_params
    assert "file" in append_params


def test_server_version_evolution_v1_12_1():
    # 在 1.12.1 版本下：
    # 1. rename 已引入，应该被成功注册
    # 2. base 相关工具尚未引入，不应被注册
    # 3. append/prepend 仍为无 heading 的历史版本
    server = create_server(
        cli_path="/mock/obsidian",
        obsidian_version="1.12.1",
        features=["all"],
    )
    tools = server._tool_manager._tools

    assert "rename" in tools
    assert "bases" not in tools
    assert "heading" not in tools["append"].parameters["properties"]


def test_server_version_evolution_v1_14_5():
    # 在 1.14.5 版本下：
    # 1. rename 正常注册
    # 2. base 全部 4 个工具正常注册
    # 3. append/prepend 自动升级为支持 heading 参数的新版本
    server = create_server(
        cli_path="/mock/obsidian",
        obsidian_version="1.14.5",
        features=["all"],
    )
    tools = server._tool_manager._tools

    assert "rename" in tools
    assert "bases" in tools
    assert "base_views" in tools
    assert "base_query" in tools
    assert "base_create" in tools

    append_params = tools["append"].parameters["properties"]
    assert "heading" in append_params
    assert "Obsidian 1.14+" in append_params["heading"]["description"]


def test_server_version_evolution_default_fallback():
    # 未指定版本（或无法获取版本）时，默认假定最新版本，加载最新的工具模式
    server = create_server(
        cli_path="/mock/obsidian",
        obsidian_version=None,
        features=["all"],
    )
    tools = server._tool_manager._tools

    assert "rename" in tools
    assert "bases" in tools
    assert "heading" in tools["append"].parameters["properties"]
