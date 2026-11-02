from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from .base import IDEMPOTENT_WRITE, READ_ONLY, call_tool


def register_vault_tools(server: MCPServer, client: ObsidianClient) -> None:
    """Register vault status and workspace navigation tools (Feature: vault)."""

    @server.tool(
        name="vault",
        description="Show vault information such as name, path, file count, folder count, or total size.",
        annotations=READ_ONLY,
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
        description="List all known Obsidian vaults and their local absolute paths.",
        annotations=READ_ONLY,
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
        description="List files in the vault, with optional filtering by folder or file extension.",
        annotations=READ_ONLY,
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
        description="List folders in the vault.",
        annotations=READ_ONLY,
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
        description="Show information about a specific folder.",
        annotations=READ_ONLY,
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
        description="List recently opened files in the vault.",
        annotations=READ_ONLY,
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
        description="List all bookmarks in the vault (returns JSON).",
        annotations=READ_ONLY,
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
        description="Get the current workspace window layout tree.",
        annotations=READ_ONLY,
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
        description="Reload the vault interface and re-index notes.",
        annotations=IDEMPOTENT_WRITE,
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
        description="Restart the Obsidian desktop application.",
        annotations=IDEMPOTENT_WRITE,
    )
    async def restart_app() -> Any:
        return await call_tool(client, "restart")

    @server.tool(
        name="version",
        description="Show the installed Obsidian desktop application version.",
        annotations=READ_ONLY,
    )
    async def version() -> Any:
        return await call_tool(client, "version")
