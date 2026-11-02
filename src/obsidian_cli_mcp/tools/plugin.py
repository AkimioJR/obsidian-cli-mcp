from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from .base import call_tool


def register_plugin_tools(server: MCPServer, client: ObsidianClient) -> None:
    """Register plugin, command palette, and template tools (Feature: plugin)."""

    @server.tool(
        name="command",
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

    @server.tool(
        name="commands",
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

    @server.tool(
        name="template_read",
        description="Read a template file's content, with optional resolution of template variables.",
    )
    async def template_read(
        name: str = Field(
            description="Template name (required).",
        ),
        resolve: bool = Field(
            default=False,
            description="Resolve template variables.",
        ),
        title: str | None = Field(
            default=None,
            description="Title for variable resolution.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "template:read",
            {"name": name, "resolve": resolve, "title": title},
            vault=vault,
        )

    @server.tool(
        name="template_insert",
        description="Insert a template into the currently active note.",
    )
    async def template_insert(
        name: str = Field(
            description="Template name (required).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "template:insert", {"name": name}, vault=vault)

    @server.tool(
        name="plugins",
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

    @server.tool(
        name="plugins_enabled",
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

    @server.tool(
        name="plugin_enable",
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

    @server.tool(
        name="plugin_disable",
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
