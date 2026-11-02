from typing import Any

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from .base import (
    DESTRUCTIVE_WRITE,
    IDEMPOTENT_WRITE,
    NON_IDEMPOTENT_WRITE,
    READ_ONLY,
    call_tool,
)


def register_note_tools(server: MCPServer, client: ObsidianClient) -> None:
    """Register note content & file manipulation tools (Feature: note)."""

    @server.tool(
        name="read",
        description="Read the complete content of a note by file name or vault-relative path.",
        annotations=READ_ONLY,
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
        description="Create a new note file with optional content, template, overwriting, and opening in app.",
        annotations=NON_IDEMPOTENT_WRITE,
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
        description="Append content to the end of a specified note file.",
        annotations=NON_IDEMPOTENT_WRITE,
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
        description="Prepend content to the beginning of a specified note file.",
        annotations=NON_IDEMPOTENT_WRITE,
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
        description="Delete a note file. Moves to trash by default, or permanently deletes if permanent=True.",
        annotations=DESTRUCTIVE_WRITE,
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
        description="Move or rename a note file to a destination folder or path.",
        annotations=IDEMPOTENT_WRITE,
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
        description="Rename a note file.",
        annotations=IDEMPOTENT_WRITE,
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
        description="Open and focus a note file in the Obsidian workspace.",
        annotations=READ_ONLY,
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
        description="Read a random note from the vault or a specified folder.",
        annotations=READ_ONLY,
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
