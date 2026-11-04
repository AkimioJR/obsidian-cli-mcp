from typing import Any

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import READ_ONLY, ToolRegistrar, call_tool


def register_graph_tools(
    server: MCPServer,
    client: ObsidianClient,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register graph, links, and structure tools (Feature: graph)."""
    reg = ToolRegistrar(
        server, "graph", lang, version=version, enable_extensions=enable_extensions
    )

    @reg.tool(
        name="backlinks",
        annotations=READ_ONLY,
        description="List backlinks pointing to a specified note (returns JSON).",
    )
    async def backlinks(
        file: str | None = Field(
            default=None,
            description="Target file name.",
        ),
        path: str | None = Field(
            default=None,
            description="Target file path.",
        ),
        total: bool = Field(
            default=False,
            description="Return backlink count.",
        ),
        counts: bool = Field(
            default=False,
            description="Include link counts per file.",
        ),
        active: bool = Field(
            default=False,
            description="Target currently active file.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "backlinks",
            {
                "file": file,
                "path": path,
                "total": total,
                "counts": counts,
                "active": active,
                "format": "json",
            },
            parse_json=True,
            vault=vault,
        )

    @reg.tool(
        name="links",
        annotations=READ_ONLY,
        description="List outgoing links from a specified note.",
    )
    async def links(
        file: str | None = Field(
            default=None,
            description="Source file name.",
        ),
        path: str | None = Field(
            default=None,
            description="Source file path.",
        ),
        total: bool = Field(
            default=False,
            description="Return link count.",
        ),
        active: bool = Field(
            default=False,
            description="Target currently active file.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "links",
            {"file": file, "path": path, "total": total, "active": active},
            vault=vault,
        )

    @reg.tool(
        name="unresolved",
        annotations=READ_ONLY,
        description="List unresolved links in the vault pointing to non-existent notes (returns JSON).",
    )
    async def unresolved(
        total: bool = Field(
            default=False,
            description="Return unresolved link count.",
        ),
        counts: bool = Field(
            default=False,
            description="Include link counts.",
        ),
        verbose: bool = Field(
            default=False,
            description="Include source files.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "unresolved",
            {
                "total": total,
                "counts": counts,
                "verbose": verbose,
                "format": "json",
            },
            parse_json=True,
            vault=vault,
        )

    @reg.tool(
        name="orphans",
        annotations=READ_ONLY,
        description="List orphan notes that have no incoming links from other notes.",
    )
    async def orphans(
        total: bool = Field(
            default=False,
            description="Return orphan file count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "orphans", {"total": total}, vault=vault)

    @reg.tool(
        name="deadends",
        annotations=READ_ONLY,
        description="List dead-end notes that contain no outgoing links to other notes.",
    )
    async def deadends(
        total: bool = Field(
            default=False,
            description="Return dead-end file count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "deadends", {"total": total}, vault=vault)

    @reg.tool(
        name="outline",
        annotations=READ_ONLY,
        description="Get the heading outline hierarchy of a note (returns JSON).",
    )
    async def outline(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        active: bool = Field(
            default=False,
            description="Show outline for active file.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "outline",
            {"file": file, "path": path, "active": active, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @reg.tool(
        name="aliases",
        annotations=READ_ONLY,
        description="List aliases in the vault or for a specified note.",
    )
    async def aliases(
        file: str | None = Field(
            default=None,
            description="Show aliases for file.",
        ),
        path: str | None = Field(
            default=None,
            description="Show aliases for path.",
        ),
        total: bool = Field(
            default=False,
            description="Return alias count.",
        ),
        counts: bool = Field(
            default=False,
            description="Include occurrence counts.",
        ),
        active: bool = Field(
            default=False,
            description="Show aliases for active file.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "aliases",
            {
                "file": file,
                "path": path,
                "total": total,
                "counts": counts,
                "active": active,
            },
            vault=vault,
        )

    @reg.tool(
        name="wordcount",
        annotations=READ_ONLY,
        description="Count words and characters in a note or the active note.",
    )
    async def wordcount(
        file: str | None = Field(
            default=None,
            description="Target file name.",
        ),
        path: str | None = Field(
            default=None,
            description="Target file path.",
        ),
        active: bool = Field(
            default=False,
            description="Count in active file.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "wordcount",
            {"file": file, "path": path, "active": active},
            vault=vault,
        )
