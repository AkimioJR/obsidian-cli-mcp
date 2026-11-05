from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import IDEMPOTENT_WRITE, READ_ONLY, ToolRegistrar, call_tool


def register_core_tools(
    server: MCPServer,
    client: ObsidianClient,
    *,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register essential runtime discovery and preflight tools.

    Core tools (version, vaults, vault, reload, restart) are always registered by default,
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
        name="set_default_vault",
        annotations=IDEMPOTENT_WRITE,
        description=(
            "Dynamically set or switch the default target Obsidian vault for subsequent tool calls in this session. "
            "Pass an empty string or null to reset and let CLI default to the active vault. "
            "(Extension tool; enabled via OBSIDIAN_EXTENSIONS=true)"
        ),
        extension=True,
    )
    async def set_default_vault(
        vault: str | None = Field(
            default=None,
            description="Vault name to set as default. If omitted, empty, or null, clears default vault.",
        ),
    ) -> str:
        vault_name = vault.strip() if vault and vault.strip() else None

        if vault_name:
            # 校验指定的目标库是否存在于已知库列表中
            known_vaults_raw = await call_tool(client, "vaults")
            if isinstance(known_vaults_raw, str) and not known_vaults_raw.startswith(
                "Error:"
            ):
                known_names = [
                    line.strip().split("\t")[0]
                    for line in known_vaults_raw.splitlines()
                    if line.strip()
                ]
                if known_names and vault_name not in known_names:
                    return (
                        f"Error: Vault '{vault_name}' not found among known vaults: {known_names}. "
                        "Default vault remains unchanged."
                    )

        old_vault = client.vault
        client.set_vault(vault_name)

        if client.vault:
            return (
                f"Default vault successfully switched from '{old_vault or '(none)'}' "
                f"to '{client.vault}' for subsequent tool calls."
            )
        else:
            return (
                f"Default vault cleared (previously '{old_vault or '(none)'}'). "
                "Subsequent tool calls will target Obsidian's active vault."
            )


__all__ = ["register_core_tools"]
