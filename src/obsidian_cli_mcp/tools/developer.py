from typing import Any

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import DYNAMIC_EVAL, ToolRegistrar, call_tool


def register_developer_tools(
    server: MCPServer,
    client: ObsidianClient,
    *,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register developer tools (Feature: developer)."""
    reg = ToolRegistrar(
        server, "developer", lang, version=version, enable_extensions=enable_extensions
    )

    @reg.tool(
        name="eval",
        annotations=DYNAMIC_EVAL,
        description="Execute JavaScript code inside the Obsidian Electron runtime and return the result.",
    )
    async def eval_js(
        code: str = Field(
            description="JavaScript code to execute (required).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "eval", {"code": code}, vault=vault)


__all__ = [
    "register_developer_tools",
]
