from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import NON_IDEMPOTENT_WRITE, READ_ONLY, ToolRegistrar, call_tool


def register_base_tools(
    server: MCPServer,
    client: ObsidianClient,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
) -> None:
    """Register Obsidian Bases database views tools (Feature: base, requires Obsidian 1.14+)."""
    reg = ToolRegistrar(server, "base", lang, version=version)

    @reg.tool(
        name="bases",
        annotations=READ_ONLY,
        description="List all .base database view files in the vault.",
        min_version="1.14.0",
    )
    async def list_bases(
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "bases", vault=vault)

    @reg.tool(
        name="base_views",
        annotations=READ_ONLY,
        description="List all views in the current or specified base file.",
        min_version="1.14.0",
    )
    async def base_views(
        file: str | None = Field(
            default=None,
            description="Base file name.",
        ),
        path: str | None = Field(
            default=None,
            description="Base file path.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client, "base:views", {"file": file, "path": path}, vault=vault
        )

    @reg.tool(
        name="base_query",
        annotations=READ_ONLY,
        description="Query an Obsidian Base and return structured results (JSON/CSV/TSV/Markdown).",
        min_version="1.14.0",
    )
    async def base_query(
        file: str | None = Field(
            default=None,
            description="Base file name.",
        ),
        path: str | None = Field(
            default=None,
            description="Base file path.",
        ),
        view: str | None = Field(
            default=None,
            description="View name to query.",
        ),
        format: Literal["json", "csv", "tsv", "md", "paths"] | None = Field(
            default="json",
            description="Output format (default: json).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "base:query",
            {"file": file, "path": path, "view": view, "format": format},
            parse_json=(format == "json" or format is None),
            vault=vault,
        )

    @reg.tool(
        name="base_create",
        annotations=NON_IDEMPOTENT_WRITE,
        description="Create a new entry/item in an Obsidian Base.",
        min_version="1.14.0",
    )
    async def base_create(
        file: str | None = Field(
            default=None,
            description="Base file name.",
        ),
        path: str | None = Field(
            default=None,
            description="Base file path.",
        ),
        view: str | None = Field(
            default=None,
            description="View name in the base.",
        ),
        name: str | None = Field(
            default=None,
            description="New item file name.",
        ),
        content: str | None = Field(
            default=None,
            description="Initial content.",
        ),
        open: bool = Field(
            default=False,
            description="Open file after creating.",
        ),
        newtab: bool = Field(
            default=False,
            description="Open in new tab.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "base:create",
            {
                "file": file,
                "path": path,
                "view": view,
                "name": name,
                "content": content,
                "open": open,
                "newtab": newtab,
            },
            vault=vault,
        )


__all__ = ["register_base_tools"]
