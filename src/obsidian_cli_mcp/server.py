import os
from collections.abc import Iterable

from mcp.server.mcpserver import MCPServer

from .client import ObsidianClient
from .tools import Feature


def create_server(
    vault: str | None = None,
    cli_path: str | None = None,
    timeout: int = 30,
    features: Iterable[Feature | str] | None = None,
    lang: str | None = None,
) -> MCPServer:
    """创建并配置 Obsidian MCP 服务器实例。支持通过 features 过滤工具集，通过 lang 配置本地化语言。"""
    client = ObsidianClient(vault=vault, cli_path=cli_path, timeout=timeout)
    server = MCPServer(
        name="obsidian-cli-mcp",
        version="0.1.0",
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

    Feature.register_tools(
        server,
        client,
        features=resolved_features,
        lang=resolved_lang,
    )
    return server
