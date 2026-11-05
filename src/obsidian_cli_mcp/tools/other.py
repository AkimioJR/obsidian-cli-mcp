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


def register_other_tools(
    server: MCPServer,
    client: ObsidianClient,
    *,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register temporary miscellaneous tools: bookmark, file, tabs, tab_open (Feature: other).

    WARNING: This feature group temporarily holds tools that have not yet been cleanly categorized into dedicated
    feature domains. It may undergo breaking changes in future releases as tools are moved. Do not rely on this
    feature group for long-term stability.
    """
    reg = ToolRegistrar(
        server, "other", lang, version=version, enable_extensions=enable_extensions
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

    @reg.tool(
        name="file",
        annotations=READ_ONLY,
        description="Show information about a specific file.",
    )
    async def file_info(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client, "file", {"file": file, "path": path}, vault=vault
        )

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


__all__ = [
    "register_other_tools",
]
