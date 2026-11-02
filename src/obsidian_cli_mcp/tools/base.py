from typing import Any

from ..client import ObsidianClient
from ..exceptions import ObsidianError


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
