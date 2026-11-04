from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import READ_ONLY, ToolRegistrar, call_tool


def register_core_tools(
    server: MCPServer,
    client: ObsidianClient,
    *,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register essential runtime discovery and preflight tools.

    Core tools (version, vaults, vault) are always registered by default,
    providing fundamental environment introspection and context building.
    """
    reg = ToolRegistrar(
        server, "core", lang, version=version, enable_extensions=enable_extensions
    )

    @reg.tool(
        name="version",
        annotations=READ_ONLY,
        description="Show the installed Obsidian desktop application version.",
    )
    async def version() -> Any:
        return await call_tool(client, "version")

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


__all__ = ["register_core_tools"]
