from typing import Any

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang, get_tool_title
from .base import (
    DESTRUCTIVE_WRITE,
    IDEMPOTENT_WRITE,
    NON_IDEMPOTENT_WRITE,
    READ_ONLY,
    call_tool,
    make_annotations,
)


def register_note_tools(
    server: MCPServer,
    client: ObsidianClient,
    lang: SupportedLang | None = None,
) -> None:
    """Register note content & file manipulation tools (Feature: note)."""

    @server.tool(
        name="read",
        title=get_tool_title("note", "read", lang),
        description="Read the complete content of a note by file name or vault-relative path.",
        annotations=make_annotations(READ_ONLY, "note", "read", lang),
    )
    async def read(
        file: str | None = Field(
            default=None,
            description="File name (resolves like wikilinks).",
        ),
        path: str | None = Field(
            default=None,
            description="File path (exact relative path).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client, "read", {"file": file, "path": path}, vault=vault
        )

    @server.tool(
        name="create",
        title=get_tool_title("note", "create", lang),
        description="Create a new note file with optional content, template, overwriting, and opening in app.",
        annotations=make_annotations(NON_IDEMPOTENT_WRITE, "note", "create", lang),
    )
    async def create(
        name: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        content: str | None = Field(
            default=None,
            description="Initial content.",
        ),
        template: str | None = Field(
            default=None,
            description="Template to use.",
        ),
        overwrite: bool = Field(
            default=False,
            description="Overwrite if file exists.",
        ),
        open: bool = Field(
            default=False,
            description="Open file after creating.",
        ),
        newtab: bool = Field(
            default=False,
            description="Open in new tab.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "create",
            {
                "name": name,
                "path": path,
                "content": content,
                "template": template,
                "overwrite": overwrite,
                "open": open,
                "newtab": newtab,
            },
            vault=vault,
        )

    @server.tool(
        name="append",
        title=get_tool_title("note", "append", lang),
        description="Append content to the end of a specified note file.",
        annotations=make_annotations(NON_IDEMPOTENT_WRITE, "note", "append", lang),
    )
    async def append(
        content: str = Field(
            description="Content to append (required).",
        ),
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        inline: bool = Field(
            default=False,
            description="Append without newline.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "append",
            {"content": content, "file": file, "path": path, "inline": inline},
            vault=vault,
        )

    @server.tool(
        name="prepend",
        title=get_tool_title("note", "prepend", lang),
        description="Prepend content to the beginning of a specified note file.",
        annotations=make_annotations(NON_IDEMPOTENT_WRITE, "note", "prepend", lang),
    )
    async def prepend(
        content: str = Field(
            description="Content to prepend (required).",
        ),
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        inline: bool = Field(
            default=False,
            description="Prepend without newline.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "prepend",
            {"content": content, "file": file, "path": path, "inline": inline},
            vault=vault,
        )

    @server.tool(
        name="delete",
        title=get_tool_title("note", "delete", lang),
        description="Delete a note file. Moves to trash by default, or permanently deletes if permanent=True.",
        annotations=make_annotations(DESTRUCTIVE_WRITE, "note", "delete", lang),
    )
    async def delete(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        permanent: bool = Field(
            default=False,
            description="Skip trash, delete permanently.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "delete",
            {"file": file, "path": path, "permanent": permanent},
            vault=vault,
        )

    @server.tool(
        name="move",
        title=get_tool_title("note", "move", lang),
        description="Move or rename a note file to a destination folder or path.",
        annotations=make_annotations(IDEMPOTENT_WRITE, "note", "move", lang),
    )
    async def move(
        to: str = Field(
            description="Destination folder or path (required).",
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
            client, "move", {"to": to, "file": file, "path": path}, vault=vault
        )

    @server.tool(
        name="rename",
        title=get_tool_title("note", "rename", lang),
        description="Rename a note file.",
        annotations=make_annotations(IDEMPOTENT_WRITE, "note", "rename", lang),
    )
    async def rename(
        name: str = Field(
            description="New file name (required).",
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
            client, "rename", {"name": name, "file": file, "path": path}, vault=vault
        )

    @server.tool(
        name="open",
        title=get_tool_title("note", "open", lang),
        description="Open and focus a note file in the Obsidian workspace.",
        annotations=make_annotations(READ_ONLY, "note", "open", lang),
    )
    async def open_file(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        newtab: bool = Field(
            default=False,
            description="Open in new tab.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client, "open", {"file": file, "path": path, "newtab": newtab}, vault=vault
        )

    @server.tool(
        name="random_read",
        title=get_tool_title("note", "random_read", lang),
        description="Read a random note from the vault or a specified folder.",
        annotations=make_annotations(READ_ONLY, "note", "random_read", lang),
    )
    async def random_read(
        folder: str | None = Field(
            default=None,
            description="Limit to folder.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(client, "random:read", {"folder": folder}, vault=vault)
