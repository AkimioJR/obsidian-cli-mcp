from typing import Any

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang, get_tool_title
from .base import DYNAMIC_EVAL, call_tool, make_annotations


def register_eval_tools(
    server: MCPServer,
    client: ObsidianClient,
    lang: SupportedLang | None = None,
) -> None:
    """Register JavaScript runtime execution tool (Feature: eval)."""

    @server.tool(
        name="eval",
        title=get_tool_title("eval", "eval", lang),
        description="Execute JavaScript code inside the Obsidian Electron runtime and return the result.",
        annotations=make_annotations(DYNAMIC_EVAL, "eval", "eval", lang),
    )
    async def eval_js(
        code: str = Field(
            description="JavaScript code to execute (required).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "eval", {"code": code}, vault=vault)
