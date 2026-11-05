from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import (
    IDEMPOTENT_WRITE,
    READ_ONLY,
    ToolRegistrar,
    call_tool,
)


def register_plugin_tools(
    server: MCPServer,
    client: ObsidianClient,
    *,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register plugin tools (Feature: plugin)."""
    reg = ToolRegistrar(
        server, "plugin", lang, version=version, enable_extensions=enable_extensions
    )

    @reg.tool(
        name="plugins",
        annotations=READ_ONLY,
        description="List installed community or core plugins (returns JSON).",
    )
    async def plugins(
        filter: Literal["core", "community"] | None = Field(
            default=None,
            description="Filter by plugin type (core or community).",
        ),
        versions: bool = Field(
            default=False,
            description="Include version numbers.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "plugins",
            {"filter": filter, "versions": versions, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @reg.tool(
        name="plugins_enabled",
        annotations=READ_ONLY,
        description="List enabled community or core plugins (returns JSON).",
    )
    async def plugins_enabled(
        filter: Literal["core", "community"] | None = Field(
            default=None,
            description="Filter by plugin type (core or community).",
        ),
        versions: bool = Field(
            default=False,
            description="Include version numbers.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "plugins:enabled",
            {"filter": filter, "versions": versions, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @reg.tool(
        name="plugin_enable",
        annotations=IDEMPOTENT_WRITE,
        description="Enable a specified community or core plugin.",
    )
    async def plugin_enable(
        id: str = Field(
            description="Plugin ID (required).",
        ),
        filter: Literal["core", "community"] | None = Field(
            default=None,
            description="Plugin type (core or community).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client, "plugin:enable", {"id": id, "filter": filter}, vault=vault
        )

    @reg.tool(
        name="plugin_disable",
        annotations=IDEMPOTENT_WRITE,
        description="Disable a specified plugin.",
    )
    async def plugin_disable(
        id: str = Field(
            description="Plugin ID (required).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "plugin:disable", {"id": id}, vault=vault)


__all__ = ["register_plugin_tools"]
