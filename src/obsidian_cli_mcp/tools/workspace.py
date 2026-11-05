from typing import Any

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import (
    NON_IDEMPOTENT_WRITE,
    READ_ONLY,
    ToolRegistrar,
    call_tool,
)


def register_workspace_tools(
    server: MCPServer,
    client: ObsidianClient,
    *,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register workspace layout and tab navigation tools (Feature: workspace)."""
    reg = ToolRegistrar(
        server, "workspace", lang, version=version, enable_extensions=enable_extensions
    )

    @reg.tool(
        name="workspace",
        annotations=READ_ONLY,
        description="Get the current workspace window layout tree.",
    )
    async def workspace(
        ids: bool = Field(
            default=False,
            description="Include workspace item IDs.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "workspace", {"ids": ids}, vault=vault)

    @reg.tool(
        name="tabs",
        annotations=READ_ONLY,
        description="List open tabs in the workspace.",
    )
    async def tabs(
        ids: bool = Field(
            default=False,
            description="Include tab IDs.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "tabs", {"ids": ids}, vault=vault)

    @reg.tool(
        name="tab_open",
        annotations=NON_IDEMPOTENT_WRITE,
        description="Open a new tab in the workspace.",
    )
    async def tab_open(
        file: str | None = Field(
            default=None,
            description="File to open.",
        ),
        group: str | None = Field(
            default=None,
            description="Tab group ID.",
        ),
        view: str | None = Field(
            default=None,
            description="View type to open.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "tab:open",
            {"file": file, "group": group, "view": view},
            vault=vault,
        )


__all__ = ["register_workspace_tools"]
