from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import READ_ONLY, ToolRegistrar, call_tool


def register_tag_tools(
    server: MCPServer,
    client: ObsidianClient,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
) -> None:
    """Register tag management tools (Feature: tag)."""
    reg = ToolRegistrar(server, "tag", lang, version=version)

    @reg.tool(
        name="tags",
        annotations=READ_ONLY,
        description="List all tags and their occurrence counts in the vault or note (returns JSON).",
    )
    async def tags(
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
            description="Return tag count.",
        ),
        counts: bool = Field(
            default=False,
            description="Include tag counts.",
        ),
        sort: Literal["name", "count"] | None = Field(
            default=None,
            description="Sort by count (default: name).",
        ),
        active: bool = Field(
            default=False,
            description="Show tags for active file.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "tags",
            {
                "file": file,
                "path": path,
                "total": total,
                "counts": counts,
                "sort": sort,
                "active": active,
                "format": "json",
            },
            parse_json=True,
            vault=vault,
        )

    @reg.tool(
        name="tag",
        annotations=READ_ONLY,
        description="Get details and file occurrences for a specific tag.",
    )
    async def tag(
        name: str = Field(
            description="Tag name (required).",
        ),
        total: bool = Field(
            default=False,
            description="Return occurrence count.",
        ),
        verbose: bool = Field(
            default=False,
            description="Include file list and count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "tag",
            {"name": name, "total": total, "verbose": verbose},
            vault=vault,
        )
