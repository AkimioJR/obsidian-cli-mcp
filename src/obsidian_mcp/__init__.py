import asyncio
import sys

from .client import ObsidianClient
from .exceptions import ObsidianCLIError, ObsidianError, ObsidianNotFoundError
from .server import create_server

__all__ = [
    "ObsidianClient",
    "ObsidianError",
    "ObsidianCLIError",
    "ObsidianNotFoundError",
    "create_server",
    "main",
]


async def _run_server() -> None:
    try:
        server = create_server()
        await server.run_stdio_async()
    except ObsidianNotFoundError as e:
        print(f"Error starting obsidian-mcp: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass


def main() -> None:
    """CLI 入口点，启动 MCP Stdio 通信服务。"""
    asyncio.run(_run_server())
