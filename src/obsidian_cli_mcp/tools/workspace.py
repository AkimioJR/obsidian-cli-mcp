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
    """Register workspace layout, tab navigation, and bookmark tools (Feature: workspace)."""
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

    @reg.tool(
        name="bookmarks",
        annotations=READ_ONLY,
        description="List all bookmarks in the vault (returns JSON).",
    )
    async def bookmarks(
        total: bool = Field(
            default=False,
            description="Return bookmark count.",
        ),
        verbose: bool = Field(
            default=False,
            description="Include bookmark types.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "bookmarks",
            {"total": total, "verbose": verbose, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @reg.tool(
        name="bookmark",
        annotations=NON_IDEMPOTENT_WRITE,
        description="Add a bookmark for a file, subpath, folder, search query, or URL.",
    )
    async def bookmark(
        file: str | None = Field(
            default=None,
            description="File to bookmark.",
        ),
        subpath: str | None = Field(
            default=None,
            description="Subpath (heading or block) within file.",
        ),
        folder: str | None = Field(
            default=None,
            description="Folder to bookmark.",
        ),
        search: str | None = Field(
            default=None,
            description="Search query to bookmark.",
        ),
        url: str | None = Field(
            default=None,
            description="URL to bookmark.",
        ),
        title: str | None = Field(
            default=None,
            description="Bookmark title.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "bookmark",
            {
                "file": file,
                "subpath": subpath,
                "folder": folder,
                "search": search,
                "url": url,
                "title": title,
            },
            vault=vault,
        )


__all__ = ["register_workspace_tools"]
