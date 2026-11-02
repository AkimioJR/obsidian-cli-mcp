from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from .base import IDEMPOTENT_WRITE, READ_ONLY, ToolRegistrar, call_tool


def register_vault_tools(
    server: MCPServer,
    client: ObsidianClient,
    lang: SupportedLang | None = None,
) -> None:
    """Register vault status and workspace navigation tools (Feature: vault)."""
    reg = ToolRegistrar(server, "vault", lang)

    @reg.tool(
        name="vault",
        annotations=READ_ONLY,
        description="Show vault information such as name, path, file count, folder count, or total size.",
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

    @reg.tool(
        name="vaults",
        annotations=READ_ONLY,
        description="List all known Obsidian vaults and their local absolute paths.",
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

    @reg.tool(
        name="files",
        annotations=READ_ONLY,
        description="List files in the vault, with optional filtering by folder or file extension.",
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

    @reg.tool(
        name="folders",
        annotations=READ_ONLY,
        description="List folders in the vault.",
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

    @reg.tool(
        name="folder",
        annotations=READ_ONLY,
        description="Show information about a specific folder.",
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

    @reg.tool(
        name="recents",
        annotations=READ_ONLY,
        description="List recently opened files in the vault.",
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
        name="reload",
        annotations=IDEMPOTENT_WRITE,
        description="Reload the vault interface and re-index notes.",
    )
    async def reload_vault(
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "reload", vault=vault)

    @reg.tool(
        name="restart",
        annotations=IDEMPOTENT_WRITE,
        description="Restart the Obsidian desktop application.",
    )
    async def restart_app() -> Any:
        return await call_tool(client, "restart")

    @reg.tool(
        name="version",
        annotations=READ_ONLY,
        description="Show the installed Obsidian desktop application version.",
    )
    async def version() -> Any:
        return await call_tool(client, "version")
