from collections.abc import Callable, Iterable
from enum import Enum

from mcp.server.mcpserver import MCPServer

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import (
    DESTRUCTIVE_WRITE,
    DYNAMIC_EVAL,
    IDEMPOTENT_WRITE,
    NON_IDEMPOTENT_WRITE,
    READ_ONLY,
    ToolRegistrar,
)
from .bases import register_base_tools
from .bookmark import register_bookmark_tools
from .command import register_command_tools
from .core import register_core_tools
from .developer import register_developer_tools
from .explorer import register_explorer_tools
from .graph import register_graph_tools
from .note import register_note_tools
from .plugin import register_plugin_tools
from .property import register_property_tools
from .tag import register_tag_tools
from .task import register_task_tools
from .template import register_template_tools
from .workspace import register_workspace_tools


class Feature(str, Enum):
    """Singular feature group names for Obsidian CLI MCP tools."""

    NOTE = "note"
    PROPERTY = "property"
    TAG = "tag"
    TASK = "task"
    GRAPH = "graph"
    EXPLORER = "explorer"
    WORKSPACE = "workspace"
    BOOKMARK = "bookmark"
    COMMAND = "command"
    TEMPLATE = "template"
    PLUGIN = "plugin"
    BASE = "base"
    DEVELOPER = "developer"

    def register(
        self,
        server: MCPServer,
        client: ObsidianClient,
        *,
        lang: SupportedLang | str | None = None,
        version: Version | None = None,
        enable_extensions: bool = False,
    ) -> None:
        """Register all tools associated with this feature to the server."""
        resolved_lang = (
            lang if isinstance(lang, SupportedLang) else SupportedLang.detect(lang)
        )
        _FEATURE_REGISTRY[self](
            server,
            client,
            lang=resolved_lang,
            version=version,
            enable_extensions=enable_extensions,
        )

    @classmethod
    def presets(cls) -> dict[str, set["Feature"]]:
        """Return preset combinations of features."""
        return {
            "all": set(cls),
            "standard": {
                cls.NOTE,
                cls.PROPERTY,
                cls.TAG,
                cls.TASK,
                cls.GRAPH,
            },
            "minimal": {cls.NOTE},
            "safe": {
                cls.NOTE,
                cls.PROPERTY,
                cls.TAG,
                cls.TASK,
                cls.GRAPH,
                cls.EXPLORER,
                cls.WORKSPACE,
                cls.BOOKMARK,
                cls.COMMAND,
                cls.TEMPLATE,
                cls.PLUGIN,
                cls.BASE,
            },  # All except developer
        }

    @classmethod
    def resolve(cls, val: "Feature | str") -> set["Feature"]:
        """Resolve a Feature enum, preset name, or string name into a set of Features."""
        if isinstance(val, cls):
            return {val}

        s = val.strip().lower()
        presets = cls.presets()
        if s in presets:
            return set(presets[s])

        try:
            return {cls(s)}
        except ValueError:
            return set()

    @classmethod
    def register_tools(
        cls,
        server: MCPServer,
        client: ObsidianClient,
        *,
        features: Iterable["Feature | str"] | None = None,
        lang: SupportedLang | str | None = None,
        version: Version | None = None,
        enable_extensions: bool = False,
    ) -> None:
        """Register tool feature groups to the MCP server.

        If features is None, standard features are registered by default.
        """
        resolved_lang = (
            lang if isinstance(lang, SupportedLang) else SupportedLang.detect(lang)
        )

        if features is None:
            enabled_features = set(cls.presets()["standard"])
        else:
            enabled_features = set()
            for item in features:
                enabled_features.update(cls.resolve(item))

        for feature in cls:
            if feature in enabled_features:
                feature.register(
                    server,
                    client,
                    lang=resolved_lang,
                    version=version,
                    enable_extensions=enable_extensions,
                )


_FEATURE_REGISTRY: dict[
    Feature,
    Callable[..., None],
] = {
    Feature.NOTE: register_note_tools,
    Feature.PROPERTY: register_property_tools,
    Feature.TAG: register_tag_tools,
    Feature.TASK: register_task_tools,
    Feature.GRAPH: register_graph_tools,
    Feature.EXPLORER: register_explorer_tools,
    Feature.WORKSPACE: register_workspace_tools,
    Feature.BOOKMARK: register_bookmark_tools,
    Feature.COMMAND: register_command_tools,
    Feature.TEMPLATE: register_template_tools,
    Feature.PLUGIN: register_plugin_tools,
    Feature.BASE: register_base_tools,
    Feature.DEVELOPER: register_developer_tools,
}

__all__ = [
    "DESTRUCTIVE_WRITE",
    "DYNAMIC_EVAL",
    "IDEMPOTENT_WRITE",
    "NON_IDEMPOTENT_WRITE",
    "READ_ONLY",
    "Feature",
    "ToolRegistrar",
    "register_base_tools",
    "register_bookmark_tools",
    "register_command_tools",
    "register_core_tools",
    "register_developer_tools",
    "register_explorer_tools",
    "register_graph_tools",
    "register_note_tools",
    "register_plugin_tools",
    "register_property_tools",
    "register_tag_tools",
    "register_task_tools",
    "register_template_tools",
    "register_workspace_tools",
]
