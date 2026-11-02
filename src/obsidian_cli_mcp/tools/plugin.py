from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang, get_tool_title
from .base import (
    IDEMPOTENT_WRITE,
    NON_IDEMPOTENT_WRITE,
    READ_ONLY,
    call_tool,
    make_annotations,
)


def register_plugin_tools(
    server: MCPServer,
    client: ObsidianClient,
    lang: SupportedLang | None = None,
) -> None:
    """Register plugin, command palette, and template tools (Feature: plugin)."""

    @server.tool(
        name="command",
        title=get_tool_title("plugin", "command", lang),
        description="Execute an Obsidian internal or plugin command by its command ID.",
        annotations=make_annotations(NON_IDEMPOTENT_WRITE, "plugin", "command", lang),
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
        title=get_tool_title("plugin", "commands", lang),
        description="List all available Obsidian commands and their command IDs.",
        annotations=make_annotations(READ_ONLY, "plugin", "commands", lang),
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
        title=get_tool_title("plugin", "template_read", lang),
        description="Read a template file's content, with optional resolution of template variables.",
        annotations=make_annotations(READ_ONLY, "plugin", "template_read", lang),
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
        title=get_tool_title("plugin", "template_insert", lang),
        description="Insert a template into the currently active note.",
        annotations=make_annotations(
            NON_IDEMPOTENT_WRITE, "plugin", "template_insert", lang
        ),
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
        title=get_tool_title("plugin", "plugins", lang),
        description="List installed community or core plugins (returns JSON).",
        annotations=make_annotations(READ_ONLY, "plugin", "plugins", lang),
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
        title=get_tool_title("plugin", "plugins_enabled", lang),
        description="List enabled community or core plugins (returns JSON).",
        annotations=make_annotations(READ_ONLY, "plugin", "plugins_enabled", lang),
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
        title=get_tool_title("plugin", "plugin_enable", lang),
        description="Enable a specified community or core plugin.",
        annotations=make_annotations(IDEMPOTENT_WRITE, "plugin", "plugin_enable", lang),
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
        title=get_tool_title("plugin", "plugin_disable", lang),
        description="Disable a specified plugin.",
        annotations=make_annotations(
            IDEMPOTENT_WRITE, "plugin", "plugin_disable", lang
        ),
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
