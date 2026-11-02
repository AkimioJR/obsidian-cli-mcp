from collections.abc import Callable
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from ..client import ObsidianClient
from ..exceptions import ObsidianError
from ..i18n import SupportedLang
from ..version import Version

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


def make_annotations(
    base: ToolAnnotations,
    feature: str,
    tool_name: str,
    lang: SupportedLang | str | None = None,
) -> ToolAnnotations:
    """Clone a base ToolAnnotations preset and attach the localized title."""
    resolved_lang = (
        lang if isinstance(lang, SupportedLang) else SupportedLang.detect(lang)
    )
    title = resolved_lang.tool_title(feature, tool_name)
    return base.model_copy(update={"title": title}) if title else base


class ToolRegistrar:
    """Helper that binds feature context, language, and version to register MCP tools with localized titles."""

    def __init__(
        self,
        server: MCPServer,
        feature: str,
        lang: SupportedLang | str | None = None,
        version: Version | None = None,
    ) -> None:
        self.server = server
        self.feature = feature
        self.lang = (
            lang if isinstance(lang, SupportedLang) else SupportedLang.detect(lang)
        )
        self.version = version

    def tool(
        self,
        name: str,
        annotations: ToolAnnotations,
        description: str | None = None,
        *,
        min_version: Version | str | None = None,
        max_version: Version | str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a tool, checking version compatibility and binding localized title."""
        # 检查版本兼容性：如果指定了 min_version / max_version 且当前已知版本不满足，则跳过注册
        if self.version is not None:
            if min_version is not None and self.version < min_version:
                return lambda fn: fn
            if max_version is not None and self.version > max_version:
                return lambda fn: fn

        title = self.lang.tool_title(self.feature, name)
        ann = annotations.model_copy(update={"title": title}) if title else annotations
        return self.server.tool(
            name=name,
            title=title,
            description=description,
            annotations=ann,
        )


async def call_tool(
    client: ObsidianClient,
    command: str,
    params: dict[str, Any] | None = None,
    *,
    parse_json: bool = False,
    vault: str | None = None,
    timeout: float | None = None,
) -> Any:
    """Execute an Obsidian CLI command and return output or formatted error."""
    try:
        return await client.execute(
            command, params, parse_json=parse_json, vault=vault, timeout=timeout
        )
    except ObsidianError as e:
        return f"Error: {e}"
