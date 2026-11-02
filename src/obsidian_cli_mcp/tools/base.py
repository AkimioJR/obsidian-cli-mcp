from typing import Any

from mcp.types import ToolAnnotations

from ..client import ObsidianClient
from ..exceptions import ObsidianError

# Reusable Tool Annotation Presets conforming to MCP 2.x standard
READ_ONLY = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)

IDEMPOTENT_WRITE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)

NON_IDEMPOTENT_WRITE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=False,
    open_world_hint=False,
)

DESTRUCTIVE_WRITE = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=True,
    idempotent_hint=True,
    open_world_hint=False,
)

DYNAMIC_EVAL = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=True,
    idempotent_hint=False,
    open_world_hint=True,
)


async def call_tool(
    client: ObsidianClient,
    command: str,
    params: dict[str, Any] | None = None,
    *,
    parse_json: bool = False,
    vault: str | None = None,
) -> Any:
    """Execute an Obsidian CLI command and return output or formatted error."""
    try:
        return await client.execute(command, params, parse_json=parse_json, vault=vault)
    except ObsidianError as e:
        return f"Error: {e}"
