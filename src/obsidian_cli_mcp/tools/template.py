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


def register_template_tools(
    server: MCPServer,
    client: ObsidianClient,
    *,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register template tools (Feature: template)."""
    reg = ToolRegistrar(
        server, "template", lang, version=version, enable_extensions=enable_extensions
    )

    @reg.tool(
        name="templates",
        annotations=READ_ONLY,
        description="List templates in the vault.",
    )
    async def templates(
        total: bool = Field(
            default=False,
            description="Return template count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "templates", {"total": total}, vault=vault)

    @reg.tool(
        name="template_read",
        annotations=READ_ONLY,
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

    @reg.tool(
        name="template_insert",
        annotations=NON_IDEMPOTENT_WRITE,
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


__all__ = ["register_template_tools"]
