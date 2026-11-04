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
    """Helper that binds feature context, language, version and extension flag to register MCP tools with localized titles."""

    def __init__(
        self,
        server: MCPServer,
        feature: str,
        lang: SupportedLang | str | None = None,
        version: Version | None = None,
        enable_extensions: bool = False,
    ) -> None:
        self.server = server
        self.feature = feature
        self.lang = (
            lang if isinstance(lang, SupportedLang) else SupportedLang.detect(lang)
        )
        self.version = version
        self.enable_extensions = enable_extensions

    def tool(
        self,
        name: str,
        annotations: ToolAnnotations,
        description: str | None = None,
        *,
        min_version: Version | str | None = None,
        max_version: Version | str | None = None,
        extension: bool = False,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a tool, checking extension flag, version compatibility and binding localized title."""
        # 1. 检查扩展功能开关：若工具标记为扩展工具但未开启扩展功能，直接跳过注册
        if extension and not self.enable_extensions:
            return lambda fn: fn

        # 2. 检查版本兼容性：未指定版本时假定最新版本 (Version(999, 999, 999))，过滤掉历史遗留版本
        check_version = (
            self.version if self.version is not None else Version(999, 999, 999)
        )
        if min_version is not None and check_version < min_version:
            return lambda fn: fn
        if max_version is not None and check_version > max_version:
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
