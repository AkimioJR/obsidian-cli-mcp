import json
from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import (
    DYNAMIC_EVAL,
    IDEMPOTENT_WRITE,
    NON_IDEMPOTENT_WRITE,
    READ_ONLY,
    ToolRegistrar,
    call_tool,
)


def register_developer_tools(
    server: MCPServer,
    client: ObsidianClient,
    *,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register developer tools (Feature: developer)."""
    reg = ToolRegistrar(
        server, "developer", lang, version=version, enable_extensions=enable_extensions
    )

    @reg.tool(
        name="eval",
        annotations=DYNAMIC_EVAL,
        description="Execute JavaScript code inside the Obsidian Electron runtime and return the result.",
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

    @reg.tool(
        name="dev_cdp",
        annotations=DYNAMIC_EVAL,
        description="Execute a Chrome DevTools Protocol (CDP) command.",
    )
    async def dev_cdp(
        method: str = Field(
            description="CDP method name (e.g. 'Page.captureScreenshot', required).",
        ),
        params: str | dict[str, Any] | None = Field(  # noqa: B008
            default=None,
            description="Method parameters as JSON string or object.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        serialized_params = (
            json.dumps(params) if isinstance(params, (dict, list)) else params
        )
        return await call_tool(
            client,
            "dev:cdp",
            {"method": method, "params": serialized_params},
            vault=vault,
        )

    @reg.tool(
        name="dev_console",
        annotations=READ_ONLY,
        description="Read or clear messages from the console buffer.",
    )
    async def dev_console(
        clear: bool = Field(
            default=False,
            description="Clear console buffer.",
        ),
        limit: int | None = Field(
            default=None,
            description="Max messages to show.",
        ),
        level: Literal["log", "warn", "error", "info", "debug"] | None = Field(
            default=None,
            description="Filter messages by log level.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "dev:console",
            {"clear": clear, "limit": limit, "level": level},
            vault=vault,
        )

    @reg.tool(
        name="dev_css",
        annotations=READ_ONLY,
        description="Inspect CSS rules or computed properties of DOM elements.",
    )
    async def dev_css(
        selector: str = Field(
            description="CSS selector to inspect (required).",
        ),
        prop: str | None = Field(
            default=None,
            description="Specific CSS property name to query.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client, "dev:css", {"selector": selector, "prop": prop}, vault=vault
        )

    @reg.tool(
        name="dev_debug",
        annotations=IDEMPOTENT_WRITE,
        description="Attach or detach the CDP debugger.",
    )
    async def dev_debug(
        state: Literal["on", "off"] | None = Field(
            default=None,
            description="Attach ('on') or detach ('off') debugger.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        params: dict[str, Any] = {}
        if state == "on":
            params["on"] = True
        elif state == "off":
            params["off"] = True
        return await call_tool(client, "dev:debug", params, vault=vault)

    @reg.tool(
        name="dev_dom",
        annotations=READ_ONLY,
        description="Query DOM elements using CSS selectors.",
    )
    async def dev_dom(
        selector: str = Field(
            description="CSS selector to query (required).",
        ),
        total: bool = Field(
            default=False,
            description="Return matched element count.",
        ),
        text: bool = Field(
            default=False,
            description="Return text content of matched element.",
        ),
        inner: bool = Field(
            default=False,
            description="Return inner HTML of matched element.",
        ),
        all: bool = Field(
            default=False,
            description="Return all matching elements.",
        ),
        attr: str | None = Field(
            default=None,
            description="Query specific attribute value.",
        ),
        css: str | None = Field(
            default=None,
            description="Query computed CSS property.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "dev:dom",
            {
                "selector": selector,
                "total": total,
                "text": text,
                "inner": inner,
                "all": all,
                "attr": attr,
                "css": css,
            },
            vault=vault,
        )

    @reg.tool(
        name="dev_errors",
        annotations=READ_ONLY,
        description="Get runtime errors captured from the application.",
    )
    async def dev_errors(
        clear: bool = Field(
            default=False,
            description="Clear error buffer.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "dev:errors", {"clear": clear}, vault=vault)

    @reg.tool(
        name="dev_mobile",
        annotations=IDEMPOTENT_WRITE,
        description="Toggle mobile emulation mode in Obsidian.",
    )
    async def dev_mobile(
        state: Literal["on", "off"] | None = Field(
            default=None,
            description="Enable ('on') or disable ('off') mobile emulation.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        params: dict[str, Any] = {}
        if state == "on":
            params["on"] = True
        elif state == "off":
            params["off"] = True
        return await call_tool(client, "dev:mobile", params, vault=vault)

    @reg.tool(
        name="dev_screenshot",
        annotations=NON_IDEMPOTENT_WRITE,
        description="Capture a screenshot of the Obsidian window.",
    )
    async def dev_screenshot(
        path: str | None = Field(
            default=None,
            description="Output file path.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "dev:screenshot", {"path": path}, vault=vault)

    @reg.tool(
        name="dev_startup",
        annotations=READ_ONLY,
        description="Show Obsidian startup performance breakdown and timing.",
    )
    async def dev_startup(
        format: Literal["json", "text"] | None = Field(
            default="json",
            description="Output format (default: json).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "dev:startup",
            {"format": format},
            parse_json=(format == "json"),
            vault=vault,
        )

    @reg.tool(
        name="devtools",
        annotations=NON_IDEMPOTENT_WRITE,
        description="Toggle the Obsidian Electron developer tools window.",
    )
    async def devtools(
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "devtools", vault=vault)


__all__ = [
    "register_developer_tools",
]
