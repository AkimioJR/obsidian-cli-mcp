import json
from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import IDEMPOTENT_WRITE, READ_ONLY, ToolRegistrar, call_tool


def register_property_tools(
    server: MCPServer,
    client: ObsidianClient,
    *,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register frontmatter property tools (Feature: property)."""
    reg = ToolRegistrar(
        server, "property", lang, version=version, enable_extensions=enable_extensions
    )

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

    @reg.tool(
        name="update_frontmatter",
        annotations=IDEMPOTENT_WRITE,
        description=(
            "Batch update, merge, or replace YAML frontmatter properties for a note in a single operation. "
            "Automatically infers property types (text, list, number, checkbox). "
            "In merge mode (default), existing properties are preserved and setting a key to null removes it. "
            "In replace mode, properties not in the new dictionary are removed. "
            "(Extension tool; enabled via OBSIDIAN_EXTENSIONS=true)"
        ),
        extension=True,
    )
    async def update_frontmatter(
        properties: dict[str, Any] = Field(  # noqa: B008
            description="Dictionary of properties (or JSON object string) to update on the file (required).",
        ),
        file: str | None = Field(
            default=None,
            description="File name to update.",
        ),
        path: str | None = Field(
            default=None,
            description="File path to update.",
        ),
        mode: Literal["merge", "replace"] = Field(
            default="merge",
            description="Update mode: merge (default) preserves existing properties; replace clears omitted properties.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        if not file and not path:
            return "Error: Either 'file' or 'path' must be provided."

        target = file or path
        target_args = {"file": file, "path": path} if path or file else {}

        if isinstance(properties, str):
            try:
                parsed_props = json.loads(properties)
            except json.JSONDecodeError as e:
                return f"Error: Failed to parse properties JSON string: {e}"
        elif isinstance(properties, dict):
            parsed_props = properties
        else:
            return (
                "Error: properties must be a dictionary or a valid JSON object string."
            )

        if not isinstance(parsed_props, dict):
            return "Error: properties must be a dictionary / JSON object."

        updated_keys: list[str] = []
        removed_keys: list[str] = []

        # 在 replace 模式下，获取现有属性并移除未包含在新属性集中的字段
        if mode == "replace":
            existing = await call_tool(
                client,
                "properties",
                {**target_args, "format": "json"},
                parse_json=True,
                vault=vault,
            )
            if isinstance(existing, str) and existing.startswith("Error:"):
                return existing

            if isinstance(existing, dict):
                for old_key in existing:
                    if old_key not in parsed_props or parsed_props[old_key] is None:
                        res = await call_tool(
                            client,
                            "property:remove",
                            {"name": old_key, **target_args},
                            vault=vault,
                        )
                        if isinstance(res, str) and res.startswith("Error:"):
                            return res
                        removed_keys.append(old_key)

        # 依次设置/更新属性
        for key, val in parsed_props.items():
            if val is None:
                if mode == "merge":
                    res = await call_tool(
                        client,
                        "property:remove",
                        {"name": key, **target_args},
                        vault=vault,
                    )
                    if isinstance(res, str) and res.startswith("Error:"):
                        return res
                    removed_keys.append(key)
                continue

            val_type: str | None = None
            if isinstance(val, bool):
                val_type = "checkbox"
                val_str = str(val).lower()
            elif isinstance(val, (int, float)):
                val_type = "number"
                val_str = str(val)
            elif isinstance(val, (list, tuple, set)):
                val_type = "list"
                val_str = ",".join(str(item) for item in val)
            else:
                val_type = "text"
                val_str = str(val)

            res = await call_tool(
                client,
                "property:set",
                {"name": key, "value": val_str, "type": val_type, **target_args},
                vault=vault,
            )
            if isinstance(res, str) and res.startswith("Error:"):
                return res
            updated_keys.append(key)

        parts = []
        if updated_keys:
            joined_up = ", ".join(repr(k) for k in updated_keys)
            parts.append(
                f"updated {len(updated_keys)} property/properties ({joined_up})"
            )
        if removed_keys:
            joined_rm = ", ".join(repr(k) for k in removed_keys)
            parts.append(
                f"removed {len(removed_keys)} property/properties ({joined_rm})"
            )

        details = "; ".join(parts) if parts else "no property changes applied"
        return f"Successfully updated frontmatter for '{target}': {details}."


__all__ = ["register_property_tools"]
