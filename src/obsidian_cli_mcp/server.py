import os
from collections.abc import Iterable

from mcp.server.mcpserver import MCPServer

from ._version import __version__
from .client import ObsidianClient
from .tools import Feature, register_core_tools
from .version import Version


def create_server(
    vault: str | None = None,
    cli_path: str | None = None,
    timeout: float | None = None,
    features: Iterable[Feature | str] | None = None,
    lang: str | None = None,
    obsidian_version: Version | str | None = None,
) -> MCPServer:
    """创建并配置 Obsidian MCP 服务器实例。

    无条件注册基础核心工具（Core Tools: version, vaults, vault），
    启动时检测 Obsidian 客户端版本并根据各工具版本要求动态检查与注册。
    """
    client = ObsidianClient(vault=vault, cli_path=cli_path, timeout=timeout)

    # 确定当前 Obsidian 客户端版本
    if isinstance(obsidian_version, str):
        current_version: Version | None = Version.try_parse(obsidian_version)
    elif isinstance(obsidian_version, Version):
        current_version = obsidian_version
    else:
        current_version = client.get_version()
    server = MCPServer(
        name="obsidian-cli-mcp",
        version=__version__,
        instructions="Obsidian CLI MCP server providing full control over Obsidian vaults.",
    )

    # 优先使用显式传入的 features 参数，未指定时尝试读取环境变量 OBSIDIAN_FEATURES，默认采用 standard 预设
    resolved_features = features
    if resolved_features is None:
        env_feat = os.getenv("OBSIDIAN_FEATURES")
        if env_feat:
            resolved_features = [f.strip() for f in env_feat.split(",") if f.strip()]
        else:
            resolved_features = ["standard"]

    # 优先使用显式传入的 lang 参数，未指定时尝试读取环境变量 OBSIDIAN_LANG
    resolved_lang = lang or os.getenv("OBSIDIAN_LANG")

    # 1. 始终注册基础核心工具（Core Tools: version, vaults, vault）
    register_core_tools(server, client, lang=resolved_lang, version=current_version)

    # 2. 按需注册各业务特性工具集（Feature Tools，附带版本约束检查）
    Feature.register_tools(
        server,
        client,
        features=resolved_features,
        lang=resolved_lang,
        version=current_version,
    )
    return server
