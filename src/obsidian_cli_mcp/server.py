from mcp.server.mcpserver import MCPServer

from .client import ObsidianClient
from .tools import register_tools


def create_server(
    vault: str | None = None,
    cli_path: str | None = None,
    timeout: int = 30,
) -> MCPServer:
    """创建并配置 Obsidian MCP 服务器实例。"""
    client = ObsidianClient(vault=vault, cli_path=cli_path, timeout=timeout)
    server = MCPServer(
        name="obsidian-cli-mcp",
        version="0.1.0",
        instructions="Obsidian CLI MCP server providing full control over Obsidian vaults.",
    )
    register_tools(server, client)
    return server
