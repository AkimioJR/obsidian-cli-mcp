from collections.abc import Callable, Iterable
from enum import Enum

from mcp.server.mcpserver import MCPServer

from ..client import ObsidianClient
from ..i18n import SupportedLang, detect_language
from .base import (
    DESTRUCTIVE_WRITE,
    DYNAMIC_EVAL,
    IDEMPOTENT_WRITE,
    NON_IDEMPOTENT_WRITE,
    READ_ONLY,
    ToolRegistrar,
)
from .eval import register_eval_tools
from .graph import register_graph_tools
from .note import register_note_tools
from .plugin import register_plugin_tools
from .property import register_property_tools
from .tag import register_tag_tools
from .task import register_task_tools
from .vault import register_vault_tools


class Feature(str, Enum):
    """Singular feature group names for Obsidian CLI MCP tools."""

    NOTE = "note"
    PROPERTY = "property"
    TAG = "tag"
    TASK = "task"
    GRAPH = "graph"
    VAULT = "vault"
    PLUGIN = "plugin"
    EVAL = "eval"


FEATURE_REGISTRY: dict[
    Feature, Callable[[MCPServer, ObsidianClient, SupportedLang | None], None]
] = {
    Feature.NOTE: register_note_tools,
    Feature.PROPERTY: register_property_tools,
    Feature.TAG: register_tag_tools,
    Feature.TASK: register_task_tools,
    Feature.GRAPH: register_graph_tools,
    Feature.VAULT: register_vault_tools,
    Feature.PLUGIN: register_plugin_tools,
    Feature.EVAL: register_eval_tools,
}

PRESETS: dict[str, set[Feature]] = {
    "all": set(Feature),
    "standard": {
        Feature.NOTE,
        Feature.PROPERTY,
        Feature.TAG,
        Feature.TASK,
        Feature.GRAPH,
    },
    "minimal": {Feature.NOTE},
    "safe": {
        Feature.NOTE,
        Feature.PROPERTY,
        Feature.TAG,
        Feature.TASK,
        Feature.GRAPH,
        Feature.VAULT,
        Feature.PLUGIN,
    },  # All except eval
}


def _resolve_feature(val: Feature | str) -> set[Feature]:
    if isinstance(val, Feature):
        return {val}

    s = val.strip().lower()
    if s in PRESETS:
        return set(PRESETS[s])

    try:
        return {Feature(s)}
    except ValueError:
        return set()


def register_tools(
    server: MCPServer,
    client: ObsidianClient,
    features: Iterable[Feature | str] | None = None,
    lang: SupportedLang | str | None = None,
) -> None:
    """Register tool feature groups to the MCP server.

    If features is None, all tools (all features) are registered by default.
    """
    resolved_lang = detect_language(lang)

    if features is None:
        enabled_features = set(Feature)
    else:
        enabled_features = set()
        for item in features:
            enabled_features.update(_resolve_feature(item))

    for feature in Feature:
        if feature in enabled_features:
            FEATURE_REGISTRY[feature](server, client, resolved_lang)


__all__ = [
    "DESTRUCTIVE_WRITE",
    "DYNAMIC_EVAL",
    "IDEMPOTENT_WRITE",
    "NON_IDEMPOTENT_WRITE",
    "PRESETS",
    "READ_ONLY",
    "Feature",
    "ToolRegistrar",
    "register_eval_tools",
    "register_graph_tools",
    "register_note_tools",
    "register_plugin_tools",
    "register_property_tools",
    "register_tag_tools",
    "register_task_tools",
    "register_tools",
    "register_vault_tools",
]
