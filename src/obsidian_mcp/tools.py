from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from .client import ObsidianClient
from .exceptions import ObsidianError


def register_tools(server: MCPServer, client: ObsidianClient) -> None:
    """Register all 1:1 mapped Obsidian CLI tools with the MCP server."""

    async def _call(
        command: str,
        params: dict[str, Any] | None = None,
        *,
        parse_json: bool = False,
        vault: str | None = None,
    ) -> Any:
        try:
            return await client.execute(
                command, params, parse_json=parse_json, vault=vault
            )
        except ObsidianError as e:
            return f"Error: {e}"

    # ==========================================
    # 1. Notes & Content
    # ==========================================

    @server.tool(
        name="obsidian_read",
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
        return await _call("read", {"file": file, "path": path}, vault=vault)

    @server.tool(
        name="obsidian_create",
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
        return await _call(
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
        name="obsidian_append",
        description="Append content to the end of a specified note file.",
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
        return await _call(
            "append",
            {"content": content, "file": file, "path": path, "inline": inline},
            vault=vault,
        )

    @server.tool(
        name="obsidian_prepend",
        description="Prepend content to the beginning of a specified note file.",
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
        return await _call(
            "prepend",
            {"content": content, "file": file, "path": path, "inline": inline},
            vault=vault,
        )

    @server.tool(
        name="obsidian_delete",
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
        return await _call(
            "delete",
            {"file": file, "path": path, "permanent": permanent},
            vault=vault,
        )

    @server.tool(
        name="obsidian_move",
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
        return await _call("move", {"to": to, "file": file, "path": path}, vault=vault)

    @server.tool(
        name="obsidian_rename",
        description="Rename a note file.",
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
        return await _call(
            "rename", {"name": name, "file": file, "path": path}, vault=vault
        )

    @server.tool(
        name="obsidian_open",
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
        return await _call(
            "open", {"file": file, "path": path, "newtab": newtab}, vault=vault
        )

    @server.tool(
        name="obsidian_random_read",
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
        return await _call("random:read", {"folder": folder}, vault=vault)

    # ==========================================
    # 2. Metadata & Properties (Frontmatter)
    # ==========================================

    @server.tool(
        name="obsidian_properties",
        description="List all frontmatter properties in the vault or for a specific file (returns JSON).",
    )
    async def properties(
        file: str | None = Field(
            default=None,
            description="Show properties for file.",
        ),
        path: str | None = Field(
            default=None,
            description="Show properties for path.",
        ),
        name: str | None = Field(
            default=None,
            description="Get specific property count.",
        ),
        total: bool = Field(
            default=False,
            description="Return property count.",
        ),
        sort: Literal["name", "count"] | None = Field(
            default=None,
            description="Sort by count (default: name).",
        ),
        counts: bool = Field(
            default=False,
            description="Include occurrence counts.",
        ),
        active: bool = Field(
            default=False,
            description="Show properties for active file.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "properties",
            {
                "file": file,
                "path": path,
                "name": name,
                "total": total,
                "sort": sort,
                "counts": counts,
                "active": active,
                "format": "json",
            },
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="obsidian_property_read",
        description="Read the value of a specific property from a file.",
    )
    async def property_read(
        name: str = Field(
            description="Property name (required).",
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
        return await _call(
            "property:read",
            {"name": name, "file": file, "path": path},
            vault=vault,
        )

    @server.tool(
        name="obsidian_property_set",
        description="Set a property on a file with optional type (text, list, number, checkbox, date, datetime).",
    )
    async def property_set(
        name: str = Field(
            description="Property name (required).",
        ),
        value: str = Field(
            description="Property value (required).",
        ),
        type: (
            Literal["text", "list", "number", "checkbox", "date", "datetime"] | None
        ) = Field(
            default=None,
            description="Property type: text, list, number, checkbox, date, datetime.",
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
        return await _call(
            "property:set",
            {"name": name, "value": value, "type": type, "file": file, "path": path},
            vault=vault,
        )

    @server.tool(
        name="obsidian_property_remove",
        description="Remove a property from a file.",
    )
    async def property_remove(
        name: str = Field(
            description="Property name (required).",
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
        return await _call(
            "property:remove",
            {"name": name, "file": file, "path": path},
            vault=vault,
        )

    # ==========================================
    # 3. Graph & Links
    # ==========================================

    @server.tool(
        name="obsidian_backlinks",
        description="List backlinks pointing to a specified note (returns JSON).",
    )
    async def backlinks(
        file: str | None = Field(
            default=None,
            description="Target file name.",
        ),
        path: str | None = Field(
            default=None,
            description="Target file path.",
        ),
        counts: bool = Field(
            default=False,
            description="Include link counts.",
        ),
        total: bool = Field(
            default=False,
            description="Return backlink count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "backlinks",
            {
                "file": file,
                "path": path,
                "counts": counts,
                "total": total,
                "format": "json",
            },
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="obsidian_links",
        description="List outgoing links from a specified note.",
    )
    async def links(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        total: bool = Field(
            default=False,
            description="Return link count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "links",
            {"file": file, "path": path, "total": total},
            vault=vault,
        )

    @server.tool(
        name="obsidian_unresolved",
        description="List unresolved links in the vault pointing to non-existent notes (returns JSON).",
    )
    async def unresolved(
        counts: bool = Field(
            default=False,
            description="Include link counts.",
        ),
        verbose: bool = Field(
            default=False,
            description="Include source files.",
        ),
        total: bool = Field(
            default=False,
            description="Return unresolved link count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "unresolved",
            {"counts": counts, "verbose": verbose, "total": total, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="obsidian_orphans",
        description="List orphan notes that have no incoming links from other notes.",
    )
    async def orphans(
        total: bool = Field(
            default=False,
            description="Return orphan file count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("orphans", {"total": total}, vault=vault)

    @server.tool(
        name="obsidian_deadends",
        description="List dead-end notes that contain no outgoing links to other notes.",
    )
    async def deadends(
        total: bool = Field(
            default=False,
            description="Return dead-end count.",
        ),
        all: bool = Field(
            default=False,
            description="Include non-markdown files.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("deadends", {"total": total, "all": all}, vault=vault)

    @server.tool(
        name="obsidian_outline",
        description="Get the heading outline hierarchy of a note (returns JSON).",
    )
    async def outline(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        total: bool = Field(
            default=False,
            description="Return heading count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "outline",
            {"file": file, "path": path, "total": total, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="obsidian_aliases",
        description="List aliases in the vault or for a specified note.",
    )
    async def aliases(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        total: bool = Field(
            default=False,
            description="Return alias count.",
        ),
        verbose: bool = Field(
            default=False,
            description="Include file paths.",
        ),
        active: bool = Field(
            default=False,
            description="Show aliases for active file.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "aliases",
            {
                "file": file,
                "path": path,
                "total": total,
                "verbose": verbose,
                "active": active,
            },
            vault=vault,
        )

    @server.tool(
        name="obsidian_wordcount",
        description="Count words and characters in a note or the active note.",
    )
    async def wordcount(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        words: bool = Field(
            default=False,
            description="Return word count only.",
        ),
        characters: bool = Field(
            default=False,
            description="Return character count only.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "wordcount",
            {"file": file, "path": path, "words": words, "characters": characters},
            vault=vault,
        )

    # ==========================================
    # 4. Tags & Tasks
    # ==========================================

    @server.tool(
        name="obsidian_tags",
        description="List all tags and their occurrence counts in the vault or note (returns JSON).",
    )
    async def tags(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        total: bool = Field(
            default=False,
            description="Return tag count.",
        ),
        counts: bool = Field(
            default=False,
            description="Include tag counts.",
        ),
        sort: Literal["name", "count"] | None = Field(
            default=None,
            description="Sort by count (default: name).",
        ),
        active: bool = Field(
            default=False,
            description="Show tags for active file.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "tags",
            {
                "file": file,
                "path": path,
                "total": total,
                "counts": counts,
                "sort": sort,
                "active": active,
                "format": "json",
            },
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="obsidian_tag",
        description="Get details and file occurrences for a specific tag.",
    )
    async def tag(
        name: str = Field(
            description="Tag name (required).",
        ),
        total: bool = Field(
            default=False,
            description="Return occurrence count.",
        ),
        verbose: bool = Field(
            default=False,
            description="Include file list and count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "tag",
            {"name": name, "total": total, "verbose": verbose},
            vault=vault,
        )

    @server.tool(
        name="obsidian_tasks",
        description="List tasks in the vault with optional filters for completion, note, or status (returns JSON).",
    )
    async def tasks(
        file: str | None = Field(
            default=None,
            description="Filter by file name.",
        ),
        path: str | None = Field(
            default=None,
            description="Filter by file path.",
        ),
        total: bool = Field(
            default=False,
            description="Return task count.",
        ),
        done: bool = Field(
            default=False,
            description="Show completed tasks.",
        ),
        todo: bool = Field(
            default=False,
            description="Show incomplete tasks.",
        ),
        status: str | None = Field(
            default=None,
            description="Filter by status character.",
        ),
        verbose: bool = Field(
            default=False,
            description="Group by file with line numbers.",
        ),
        active: bool = Field(
            default=False,
            description="Show tasks for active file.",
        ),
        daily: bool = Field(
            default=False,
            description="Show tasks from daily note.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "tasks",
            {
                "file": file,
                "path": path,
                "total": total,
                "done": done,
                "todo": todo,
                "status": status,
                "verbose": verbose,
                "active": active,
                "daily": daily,
                "format": "json",
            },
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="obsidian_task",
        description="Show or update a specific task status (toggle, mark done, or set status character).",
    )
    async def task(
        ref: str | None = Field(
            default=None,
            description="Task reference (path:line).",
        ),
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        line: int | None = Field(
            default=None,
            description="Line number.",
        ),
        toggle: bool = Field(
            default=False,
            description="Toggle task status.",
        ),
        done: bool = Field(
            default=False,
            description="Mark as done.",
        ),
        todo: bool = Field(
            default=False,
            description="Mark as todo.",
        ),
        daily: bool = Field(
            default=False,
            description="Use daily note.",
        ),
        status: str | None = Field(
            default=None,
            description="Set status character.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "task",
            {
                "ref": ref,
                "file": file,
                "path": path,
                "line": line,
                "toggle": toggle,
                "done": done,
                "todo": todo,
                "daily": daily,
                "status": status,
            },
            vault=vault,
        )

    # ==========================================
    # 5. Vault & Workspace
    # ==========================================

    @server.tool(
        name="obsidian_vault",
        description="Show vault information such as name, path, file count, folder count, or total size.",
    )
    async def vault_info(
        info: Literal["name", "path", "files", "folders", "size"] | None = Field(
            default=None,
            description="Return specific info only (name, path, files, folders, size).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("vault", {"info": info}, vault=vault)

    @server.tool(
        name="obsidian_vaults",
        description="List all known Obsidian vaults and their local absolute paths.",
    )
    async def vaults(
        total: bool = Field(
            default=False,
            description="Return vault count.",
        ),
        verbose: bool = Field(
            default=True,
            description="Include vault paths.",
        ),
    ) -> Any:
        return await _call("vaults", {"total": total, "verbose": verbose})

    @server.tool(
        name="obsidian_files",
        description="List files in the vault, with optional filtering by folder or file extension.",
    )
    async def files(
        folder: str | None = Field(
            default=None,
            description="Filter by folder.",
        ),
        ext: str | None = Field(
            default=None,
            description="Filter by extension.",
        ),
        total: bool = Field(
            default=False,
            description="Return file count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "files", {"folder": folder, "ext": ext, "total": total}, vault=vault
        )

    @server.tool(
        name="obsidian_folders",
        description="List folders in the vault.",
    )
    async def folders(
        folder: str | None = Field(
            default=None,
            description="Filter by parent folder.",
        ),
        total: bool = Field(
            default=False,
            description="Return folder count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("folders", {"folder": folder, "total": total}, vault=vault)

    @server.tool(
        name="obsidian_folder",
        description="Show information about a specific folder.",
    )
    async def folder_info(
        path: str = Field(
            description="Folder path (required).",
        ),
        info: Literal["files", "folders", "size"] | None = Field(
            default=None,
            description="Return specific info only (files, folders, size).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("folder", {"path": path, "info": info}, vault=vault)

    @server.tool(
        name="obsidian_recents",
        description="List recently opened files in the vault.",
    )
    async def recents(
        total: bool = Field(
            default=False,
            description="Return recent file count.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("recents", {"total": total}, vault=vault)

    @server.tool(
        name="obsidian_bookmarks",
        description="List all bookmarks in the vault (returns JSON).",
    )
    async def bookmarks(
        total: bool = Field(
            default=False,
            description="Return bookmark count.",
        ),
        verbose: bool = Field(
            default=False,
            description="Include bookmark types.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "bookmarks",
            {"total": total, "verbose": verbose, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="obsidian_workspace",
        description="Get the current workspace window layout tree.",
    )
    async def workspace(
        ids: bool = Field(
            default=False,
            description="Include workspace item IDs.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("workspace", {"ids": ids}, vault=vault)

    @server.tool(
        name="obsidian_reload",
        description="Reload the vault interface and re-index notes.",
    )
    async def reload_vault(
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("reload", vault=vault)

    @server.tool(
        name="obsidian_restart",
        description="Restart the Obsidian desktop application.",
    )
    async def restart_app() -> Any:
        return await _call("restart")

    @server.tool(
        name="obsidian_version",
        description="Show the installed Obsidian desktop application version.",
    )
    async def version() -> Any:
        return await _call("version")

    # ==========================================
    # 6. Commands & Automation
    # ==========================================

    @server.tool(
        name="obsidian_command",
        description="Execute an Obsidian internal or plugin command by its command ID.",
    )
    async def execute_command(
        id: str = Field(
            description="Command ID to execute (required).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("command", {"id": id}, vault=vault)

    @server.tool(
        name="obsidian_commands",
        description="List all available Obsidian commands and their command IDs.",
    )
    async def list_commands(
        filter: str | None = Field(
            default=None,
            description="Filter by ID prefix.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("commands", {"filter": filter}, vault=vault)

    @server.tool(
        name="obsidian_template_read",
        description="Read a template file's content, with optional resolution of template variables.",
    )
    async def template_read(
        name: str = Field(
            description="Template name (required).",
        ),
        resolve: bool = Field(
            default=False,
            description="Resolve template variables.",
        ),
        title: str | None = Field(
            default=None,
            description="Title for variable resolution.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "template:read",
            {"name": name, "resolve": resolve, "title": title},
            vault=vault,
        )

    @server.tool(
        name="obsidian_template_insert",
        description="Insert a template into the currently active note.",
    )
    async def template_insert(
        name: str = Field(
            description="Template name (required).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("template:insert", {"name": name}, vault=vault)

    @server.tool(
        name="obsidian_eval",
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
        return await _call("eval", {"code": code}, vault=vault)

    # ==========================================
    # 7. Plugins
    # ==========================================

    @server.tool(
        name="obsidian_plugins",
        description="List installed community or core plugins (returns JSON).",
    )
    async def plugins(
        filter: Literal["core", "community"] | None = Field(
            default=None,
            description="Filter by plugin type (core or community).",
        ),
        versions: bool = Field(
            default=False,
            description="Include version numbers.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "plugins",
            {"filter": filter, "versions": versions, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="obsidian_plugins_enabled",
        description="List enabled community or core plugins (returns JSON).",
    )
    async def plugins_enabled(
        filter: Literal["core", "community"] | None = Field(
            default=None,
            description="Filter by plugin type (core or community).",
        ),
        versions: bool = Field(
            default=False,
            description="Include version numbers.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call(
            "plugins:enabled",
            {"filter": filter, "versions": versions, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="obsidian_plugin_enable",
        description="Enable a specified community or core plugin.",
    )
    async def plugin_enable(
        id: str = Field(
            description="Plugin ID (required).",
        ),
        filter: Literal["core", "community"] | None = Field(
            default=None,
            description="Plugin type (core or community).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("plugin:enable", {"id": id, "filter": filter}, vault=vault)

    @server.tool(
        name="obsidian_plugin_disable",
        description="Disable a specified plugin.",
    )
    async def plugin_disable(
        id: str = Field(
            description="Plugin ID (required).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await _call("plugin:disable", {"id": id}, vault=vault)
