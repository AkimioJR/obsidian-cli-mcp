from typing import Any

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang, get_tool_title
from .base import READ_ONLY, call_tool, make_annotations


def register_graph_tools(
    server: MCPServer,
    client: ObsidianClient,
    lang: SupportedLang | None = None,
) -> None:
    """Register graph, links, and structure tools (Feature: graph)."""

    @server.tool(
        name="backlinks",
        title=get_tool_title("graph", "backlinks", lang),
        annotations=make_annotations(READ_ONLY, "graph", "backlinks", lang),
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
        counts: bool = Field(
            default=False,
            description="Include link counts.",
        ),
        total: bool = Field(
            default=False,
            description="Return backlink count.",
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
                "counts": counts,
                "total": total,
                "format": "json",
            },
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="links",
        title=get_tool_title("graph", "links", lang),
        annotations=make_annotations(READ_ONLY, "graph", "links", lang),
        description="List outgoing links from a specified note.",
    )
    async def links(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        total: bool = Field(
            default=False,
            description="Return link count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "links",
            {"file": file, "path": path, "total": total},
            vault=vault,
        )

    @server.tool(
        name="unresolved",
        title=get_tool_title("graph", "unresolved", lang),
        annotations=make_annotations(READ_ONLY, "graph", "unresolved", lang),
        description="List unresolved links in the vault pointing to non-existent notes (returns JSON).",
    )
    async def unresolved(
        counts: bool = Field(
            default=False,
            description="Include link counts.",
        ),
        verbose: bool = Field(
            default=False,
            description="Include source files.",
        ),
        total: bool = Field(
            default=False,
            description="Return unresolved link count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "unresolved",
            {"counts": counts, "verbose": verbose, "total": total, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="orphans",
        title=get_tool_title("graph", "orphans", lang),
        annotations=make_annotations(READ_ONLY, "graph", "orphans", lang),
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

    @server.tool(
        name="deadends",
        title=get_tool_title("graph", "deadends", lang),
        annotations=make_annotations(READ_ONLY, "graph", "deadends", lang),
        description="List dead-end notes that contain no outgoing links to other notes.",
    )
    async def deadends(
        total: bool = Field(
            default=False,
            description="Return dead-end count.",
        ),
        all: bool = Field(
            default=False,
            description="Include non-markdown files.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client, "deadends", {"total": total, "all": all}, vault=vault
        )

    @server.tool(
        name="outline",
        title=get_tool_title("graph", "outline", lang),
        annotations=make_annotations(READ_ONLY, "graph", "outline", lang),
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
        total: bool = Field(
            default=False,
            description="Return heading count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "outline",
            {"file": file, "path": path, "total": total, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="aliases",
        title=get_tool_title("graph", "aliases", lang),
        annotations=make_annotations(READ_ONLY, "graph", "aliases", lang),
        description="List aliases in the vault or for a specified note.",
    )
    async def aliases(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        total: bool = Field(
            default=False,
            description="Return alias count.",
        ),
        verbose: bool = Field(
            default=False,
            description="Include file paths.",
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
                "verbose": verbose,
                "active": active,
            },
            vault=vault,
        )

    @server.tool(
        name="wordcount",
        title=get_tool_title("graph", "wordcount", lang),
        annotations=make_annotations(READ_ONLY, "graph", "wordcount", lang),
        description="Count words and characters in a note or the active note.",
    )
    async def wordcount(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        words: bool = Field(
            default=False,
            description="Return word count only.",
        ),
        characters: bool = Field(
            default=False,
            description="Return character count only.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "wordcount",
            {"file": file, "path": path, "words": words, "characters": characters},
            vault=vault,
        )
