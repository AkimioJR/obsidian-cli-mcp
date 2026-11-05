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


def register_command_tools(
    server: MCPServer,
    client: ObsidianClient,
    *,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register command palette tools (Feature: command)."""
    reg = ToolRegistrar(
        server, "command", lang, version=version, enable_extensions=enable_extensions
    )

    @reg.tool(
        name="command",
        annotations=NON_IDEMPOTENT_WRITE,
        description="Execute an Obsidian internal or plugin command by its command ID.",
    )
    async def execute_command(
        id: str = Field(
            description="Command ID to execute (required).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "command", {"id": id}, vault=vault)

    @reg.tool(
        name="commands",
        annotations=READ_ONLY,
        description="List all available Obsidian commands and their command IDs.",
    )
    async def list_commands(
        filter: str | None = Field(
            default=None,
            description="Filter by ID prefix.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "commands", {"filter": filter}, vault=vault)


__all__ = ["register_command_tools"]
