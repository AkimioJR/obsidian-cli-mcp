from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang, get_tool_title
from .base import IDEMPOTENT_WRITE, READ_ONLY, call_tool, make_annotations


def register_vault_tools(
    server: MCPServer,
    client: ObsidianClient,
    lang: SupportedLang | None = None,
) -> None:
    """Register vault status and workspace navigation tools (Feature: vault)."""

    @server.tool(
        name="vault",
        title=get_tool_title("vault", "vault", lang),
        description="Show vault information such as name, path, file count, folder count, or total size.",
        annotations=make_annotations(READ_ONLY, "vault", "vault", lang),
    )
    async def vault_info(
        info: Literal["name", "path", "files", "folders", "size"] | None = Field(
            default=None,
            description="Return specific info only (name, path, files, folders, size).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "vault", {"info": info}, vault=vault)

    @server.tool(
        name="vaults",
        title=get_tool_title("vault", "vaults", lang),
        description="List all known Obsidian vaults and their local absolute paths.",
        annotations=make_annotations(READ_ONLY, "vault", "vaults", lang),
    )
    async def vaults(
        total: bool = Field(
            default=False,
            description="Return vault count.",
        ),
        verbose: bool = Field(
            default=True,
            description="Include vault paths.",
        ),
    ) -> Any:
        return await call_tool(client, "vaults", {"total": total, "verbose": verbose})

    @server.tool(
        name="files",
        title=get_tool_title("vault", "files", lang),
        description="List files in the vault, with optional filtering by folder or file extension.",
        annotations=make_annotations(READ_ONLY, "vault", "files", lang),
    )
    async def files(
        folder: str | None = Field(
            default=None,
            description="Filter by folder.",
        ),
        ext: str | None = Field(
            default=None,
            description="Filter by extension.",
        ),
        total: bool = Field(
            default=False,
            description="Return file count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client, "files", {"folder": folder, "ext": ext, "total": total}, vault=vault
        )

    @server.tool(
        name="folders",
        title=get_tool_title("vault", "folders", lang),
        description="List folders in the vault.",
        annotations=make_annotations(READ_ONLY, "vault", "folders", lang),
    )
    async def folders(
        folder: str | None = Field(
            default=None,
            description="Filter by parent folder.",
        ),
        total: bool = Field(
            default=False,
            description="Return folder count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client, "folders", {"folder": folder, "total": total}, vault=vault
        )

    @server.tool(
        name="folder",
        title=get_tool_title("vault", "folder", lang),
        description="Show information about a specific folder.",
        annotations=make_annotations(READ_ONLY, "vault", "folder", lang),
    )
    async def folder_info(
        path: str = Field(
            description="Folder path (required).",
        ),
        info: Literal["files", "folders", "size"] | None = Field(
            default=None,
            description="Return specific info only (files, folders, size).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client, "folder", {"path": path, "info": info}, vault=vault
        )

    @server.tool(
        name="recents",
        title=get_tool_title("vault", "recents", lang),
        description="List recently opened files in the vault.",
        annotations=make_annotations(READ_ONLY, "vault", "recents", lang),
    )
    async def recents(
        total: bool = Field(
            default=False,
            description="Return recent file count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "recents", {"total": total}, vault=vault)

    @server.tool(
        name="bookmarks",
        title=get_tool_title("vault", "bookmarks", lang),
        description="List all bookmarks in the vault (returns JSON).",
        annotations=make_annotations(READ_ONLY, "vault", "bookmarks", lang),
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

    @server.tool(
        name="workspace",
        title=get_tool_title("vault", "workspace", lang),
        description="Get the current workspace window layout tree.",
        annotations=make_annotations(READ_ONLY, "vault", "workspace", lang),
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

    @server.tool(
        name="reload",
        title=get_tool_title("vault", "reload", lang),
        description="Reload the vault interface and re-index notes.",
        annotations=make_annotations(IDEMPOTENT_WRITE, "vault", "reload", lang),
    )
    async def reload_vault(
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "reload", vault=vault)

    @server.tool(
        name="restart",
        title=get_tool_title("vault", "restart", lang),
        description="Restart the Obsidian desktop application.",
        annotations=make_annotations(IDEMPOTENT_WRITE, "vault", "restart", lang),
    )
    async def restart_app() -> Any:
        return await call_tool(client, "restart")

    @server.tool(
        name="version",
        title=get_tool_title("vault", "version", lang),
        description="Show the installed Obsidian desktop application version.",
        annotations=make_annotations(READ_ONLY, "vault", "version", lang),
    )
    async def version() -> Any:
        return await call_tool(client, "version")
