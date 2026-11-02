from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from .base import IDEMPOTENT_WRITE, READ_ONLY, ToolRegistrar, call_tool


def register_property_tools(
    server: MCPServer,
    client: ObsidianClient,
    lang: SupportedLang | None = None,
) -> None:
    """Register frontmatter property tools (Feature: property)."""
    reg = ToolRegistrar(server, "property", lang)

    @reg.tool(
        name="properties",
        annotations=READ_ONLY,
        description="List all frontmatter properties in the vault or for a specific file (returns JSON).",
    )
    async def properties(
        file: str | None = Field(
            default=None,
            description="Show properties for file.",
        ),
        path: str | None = Field(
            default=None,
            description="Show properties for path.",
        ),
        name: str | None = Field(
            default=None,
            description="Get specific property count.",
        ),
        total: bool = Field(
            default=False,
            description="Return property count.",
        ),
        sort: Literal["name", "count"] | None = Field(
            default=None,
            description="Sort by count (default: name).",
        ),
        counts: bool = Field(
            default=False,
            description="Include occurrence counts.",
        ),
        active: bool = Field(
            default=False,
            description="Show properties for active file.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "properties",
            {
                "file": file,
                "path": path,
                "name": name,
                "total": total,
                "sort": sort,
                "counts": counts,
                "active": active,
                "format": "json",
            },
            parse_json=True,
            vault=vault,
        )

    @reg.tool(
        name="property_read",
        annotations=READ_ONLY,
        description="Read the value of a specific property from a file.",
    )
    async def property_read(
        name: str = Field(
            description="Property name (required).",
        ),
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "property:read",
            {"name": name, "file": file, "path": path},
            vault=vault,
        )

    @reg.tool(
        name="property_set",
        annotations=IDEMPOTENT_WRITE,
        description="Set a property on a file with optional type (text, list, number, checkbox, date, datetime).",
    )
    async def property_set(
        name: str = Field(
            description="Property name (required).",
        ),
        value: str = Field(
            description="Property value (required).",
        ),
        type: (
            Literal["text", "list", "number", "checkbox", "date", "datetime"] | None
        ) = Field(
            default=None,
            description="Property type: text, list, number, checkbox, date, datetime.",
        ),
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "property:set",
            {"name": name, "value": value, "type": type, "file": file, "path": path},
            vault=vault,
        )

    @reg.tool(
        name="property_remove",
        annotations=IDEMPOTENT_WRITE,
        description="Remove a property from a file.",
    )
    async def property_remove(
        name: str = Field(
            description="Property name (required).",
        ),
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "property:remove",
            {"name": name, "file": file, "path": path},
            vault=vault,
        )
