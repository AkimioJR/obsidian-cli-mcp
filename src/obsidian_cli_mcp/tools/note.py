from typing import Any

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import (
    DESTRUCTIVE_WRITE,
    IDEMPOTENT_WRITE,
    NON_IDEMPOTENT_WRITE,
    READ_ONLY,
    ToolRegistrar,
    call_tool,
)


def register_note_tools(
    server: MCPServer,
    client: ObsidianClient,
    *,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register note content & file manipulation tools (Feature: note)."""
    reg = ToolRegistrar(
        server, "note", lang, version=version, enable_extensions=enable_extensions
    )

    @reg.tool(
        name="read",
        annotations=READ_ONLY,
        description="Read the complete content of a note by file name or vault-relative path.",
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

    @reg.tool(
        name="create",
        annotations=NON_IDEMPOTENT_WRITE,
        description="Create a new note file with optional content, template, overwriting, and opening in app.",
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

    # Version < 1.14.0: append without heading parameter
    @reg.tool(
        name="append",
        annotations=NON_IDEMPOTENT_WRITE,
        description="Append content to the end of a specified note file.",
        max_version="1.13.99",
    )
    async def append_legacy(
        content: str = Field(
            description="Content to append (required).",
        ),
        file: str | None = Field(
            default=None,
            description="File name (resolves like wikilinks).",
        ),
        path: str | None = Field(
            default=None,
            description="File path (exact relative path).",
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

    # Version >= 1.14.0: append with heading section support
    @reg.tool(
        name="append",
        annotations=NON_IDEMPOTENT_WRITE,
        description="Append content to the end of a note file or under a target heading section.",
        min_version="1.14.0",
    )
    async def append(
        content: str = Field(
            description="Content to append (required).",
        ),
        file: str | None = Field(
            default=None,
            description="File name (resolves like wikilinks).",
        ),
        path: str | None = Field(
            default=None,
            description="File path (exact relative path).",
        ),
        heading: str | None = Field(
            default=None,
            description="Target heading section to append under (Obsidian 1.14+).",
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
            {
                "content": content,
                "file": file,
                "path": path,
                "heading": heading,
                "inline": inline,
            },
            vault=vault,
        )

    # Version < 1.14.0: prepend without heading parameter
    @reg.tool(
        name="prepend",
        annotations=NON_IDEMPOTENT_WRITE,
        description="Prepend content to the beginning of a specified note file.",
        max_version="1.13.99",
    )
    async def prepend_legacy(
        content: str = Field(
            description="Content to prepend (required).",
        ),
        file: str | None = Field(
            default=None,
            description="File name (resolves like wikilinks).",
        ),
        path: str | None = Field(
            default=None,
            description="File path (exact relative path).",
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

    # Version >= 1.14.0: prepend with heading section support
    @reg.tool(
        name="prepend",
        annotations=NON_IDEMPOTENT_WRITE,
        description="Prepend content to the beginning of a note file or under a target heading section.",
        min_version="1.14.0",
    )
    async def prepend(
        content: str = Field(
            description="Content to prepend (required).",
        ),
        file: str | None = Field(
            default=None,
            description="File name (resolves like wikilinks).",
        ),
        path: str | None = Field(
            default=None,
            description="File path (exact relative path).",
        ),
        heading: str | None = Field(
            default=None,
            description="Target heading section to prepend under (Obsidian 1.14+).",
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
            {
                "content": content,
                "file": file,
                "path": path,
                "heading": heading,
                "inline": inline,
            },
            vault=vault,
        )

    @reg.tool(
        name="delete",
        annotations=DESTRUCTIVE_WRITE,
        description="Delete a note file. Moves to trash by default, or permanently deletes if permanent=True.",
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

    @reg.tool(
        name="move",
        annotations=IDEMPOTENT_WRITE,
        description="Move or rename a note file to a destination folder or path.",
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

    @reg.tool(
        name="rename",
        annotations=IDEMPOTENT_WRITE,
        description="Rename a note file.",
        min_version="1.12.1",
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

    @reg.tool(
        name="open",
        annotations=READ_ONLY,
        description="Open and focus a note file in the Obsidian workspace.",
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

    @reg.tool(
        name="random_read",
        annotations=READ_ONLY,
        description="Read a random note from the vault or a specified folder.",
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

    @reg.tool(
        name="edit",
        annotations=NON_IDEMPOTENT_WRITE,
        description=(
            "Edit an existing note by replacing literal text. "
            "When replace_all is false, old_str must match uniquely in the note. "
            "(Extension tool; enabled via OBSIDIAN_EXTENSIONS=true)"
        ),
        extension=True,
    )
    async def edit(
        old_str: str = Field(
            description="Exact literal text snippet to find and replace (required).",
        ),
        new_str: str = Field(
            description="Replacement text (required). Use an empty string to delete old_str.",
        ),
        file: str | None = Field(
            default=None,
            description="Target file name (resolves like wikilinks).",
        ),
        path: str | None = Field(
            default=None,
            description="Target file path (exact relative path in vault).",
        ),
        replace_all: bool = Field(
            default=False,
            description="Whether to replace all occurrences. If false (default), old_str must match exactly once in the file.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        if not file and not path:
            return "Error: Either 'file' or 'path' must be provided to specify the target note."

        if not old_str:
            return "Error: 'old_str' must not be empty. Use 'create' with overwrite=True for full-file replacement."

        target = path or file or "note"
        if old_str == new_str:
            return f"No changes needed: 'old_str' and 'new_str' are identical in '{target}'."

        content = await call_tool(
            client,
            "read",
            {
                "file": file,
                "path": path,
            },
            vault=vault,
        )
        if isinstance(content, str) and content.startswith("Error:"):
            return content

        if not isinstance(content, str):
            content = str(content)

        count = content.count(old_str)
        if count == 0:
            return (
                f"Error: Target string not found in '{target}'. No changes were made."
            )

        if count > 1 and not replace_all:
            return (
                f"Error: Found {count} occurrences of 'old_str' in '{target}', but replace_all is false. "
                "Please provide more surrounding lines to uniquely identify the match, or set replace_all=true."
            )

        new_content = (
            content.replace(old_str, new_str)
            if replace_all
            else content.replace(old_str, new_str, 1)
        )

        write_res = await call_tool(
            client,
            "create",
            {
                "name": file,
                "path": path,
                "content": new_content,
                "overwrite": True,
            },
            vault=vault,
        )
        if isinstance(write_res, str) and write_res.startswith("Error:"):
            return write_res

        replaced_count = count if replace_all else 1
        return f"The file '{target}' has been updated successfully ({replaced_count} occurrence(s) replaced)."
