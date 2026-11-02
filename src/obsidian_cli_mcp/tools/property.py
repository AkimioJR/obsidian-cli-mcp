from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from .base import IDEMPOTENT_WRITE, READ_ONLY, call_tool


def register_property_tools(server: MCPServer, client: ObsidianClient) -> None:
    """Register frontmatter property tools (Feature: property)."""

    @server.tool(
        name="properties",
        description="List all frontmatter properties in the vault or for a specific file (returns JSON).",
        annotations=READ_ONLY,
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

    @server.tool(
        name="property_read",
        description="Read the value of a specific property from a file.",
        annotations=READ_ONLY,
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

    @server.tool(
        name="property_set",
        description="Set a property on a file with optional type (text, list, number, checkbox, date, datetime).",
        annotations=IDEMPOTENT_WRITE,
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

    @server.tool(
        name="property_remove",
        description="Remove a property from a file.",
        annotations=IDEMPOTENT_WRITE,
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
