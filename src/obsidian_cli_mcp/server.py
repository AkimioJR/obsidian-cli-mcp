import os
from collections.abc import Iterable

from mcp.server.mcpserver import MCPServer

from ._version import __version__
from .client import ObsidianClient
from .tools import Feature, register_core_tools


def create_server(
    vault: str | None = None,
    cli_path: str | None = None,
    timeout: float | None = None,
    features: Iterable[Feature | str] | None = None,
    lang: str | None = None,
) -> MCPServer:
    """创建并配置 Obsidian MCP 服务器实例。

    无条件注册基础核心工具（Core Tools: version, vaults, vault），
    支持通过 features 过滤业务特性集，通过 lang 配置本地化语言。
    """
    client = ObsidianClient(vault=vault, cli_path=cli_path, timeout=timeout)
    server = MCPServer(
        name="obsidian-cli-mcp",
        version=__version__,
        instructions="Obsidian CLI MCP server providing full control over Obsidian vaults.",
    )

    # 优先使用显式传入的 features 参数，未指定时尝试读取环境变量 OBSIDIAN_FEATURES
    resolved_features = features
    if resolved_features is None:
        env_feat = os.getenv("OBSIDIAN_FEATURES")
        if env_feat:
            resolved_features = [f.strip() for f in env_feat.split(",") if f.strip()]

    # 优先使用显式传入的 lang 参数，未指定时尝试读取环境变量 OBSIDIAN_LANG
    resolved_lang = lang or os.getenv("OBSIDIAN_LANG")

    # 1. 始终注册基础核心工具（Core Tools: version, vaults, vault）
    register_core_tools(server, client, lang=resolved_lang)

    # 2. 按需注册各业务特性工具集（Feature Tools）
    Feature.register_tools(
        server, client, features=resolved_features, lang=resolved_lang
    )
    return server
