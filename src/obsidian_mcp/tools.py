from typing import Any, Literal

from mcp.server.mcpserver import MCPServer

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
        file: str | None = None, path: str | None = None, vault: str | None = None
    ) -> Any:
        return await _call("read", {"file": file, "path": path}, vault=vault)

    @server.tool(
        name="obsidian_create",
        description="Create a new note file with optional content, template, overwriting, and opening in app.",
    )
    async def create(
        name: str | None = None,
        path: str | None = None,
        content: str | None = None,
        template: str | None = None,
        overwrite: bool = False,
        open: bool = False,
        newtab: bool = False,
        vault: str | None = None,
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
        content: str,
        file: str | None = None,
        path: str | None = None,
        inline: bool = False,
        vault: str | None = None,
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
        content: str,
        file: str | None = None,
        path: str | None = None,
        inline: bool = False,
        vault: str | None = None,
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
        file: str | None = None,
        path: str | None = None,
        permanent: bool = False,
        vault: str | None = None,
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
        to: str,
        file: str | None = None,
        path: str | None = None,
        vault: str | None = None,
    ) -> Any:
        return await _call("move", {"to": to, "file": file, "path": path}, vault=vault)

    @server.tool(
        name="obsidian_rename",
        description="Rename a note file.",
    )
    async def rename(
        name: str,
        file: str | None = None,
        path: str | None = None,
        vault: str | None = None,
    ) -> Any:
        return await _call(
            "rename", {"name": name, "file": file, "path": path}, vault=vault
        )

    @server.tool(
        name="obsidian_open",
        description="Open and focus a note file in the Obsidian workspace.",
    )
    async def open_file(
        file: str | None = None,
        path: str | None = None,
        newtab: bool = False,
        vault: str | None = None,
    ) -> Any:
        return await _call(
            "open", {"file": file, "path": path, "newtab": newtab}, vault=vault
        )

    @server.tool(
        name="obsidian_random_read",
        description="Read a random note from the vault or a specified folder.",
    )
    async def random_read(folder: str | None = None, vault: str | None = None) -> Any:
        return await _call("random:read", {"folder": folder}, vault=vault)

    # ==========================================
    # 2. Metadata & Properties (Frontmatter)
    # ==========================================

    @server.tool(
        name="obsidian_properties",
        description="List all frontmatter properties in the vault or for a specific file (returns JSON).",
    )
    async def properties(
        file: str | None = None,
        path: str | None = None,
        name: str | None = None,
        total: bool = False,
        sort: Literal["name", "count"] | None = None,
        counts: bool = False,
        active: bool = False,
        vault: str | None = None,
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
        name: str,
        file: str | None = None,
        path: str | None = None,
        vault: str | None = None,
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
        name: str,
        value: str,
        type: (
            Literal["text", "list", "number", "checkbox", "date", "datetime"] | None
        ) = None,
        file: str | None = None,
        path: str | None = None,
        vault: str | None = None,
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
        name: str,
        file: str | None = None,
        path: str | None = None,
        vault: str | None = None,
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
        file: str | None = None,
        path: str | None = None,
        counts: bool = False,
        total: bool = False,
        vault: str | None = None,
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
        file: str | None = None,
        path: str | None = None,
        total: bool = False,
        vault: str | None = None,
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
        counts: bool = False,
        verbose: bool = False,
        total: bool = False,
        vault: str | None = None,
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
    async def orphans(total: bool = False, vault: str | None = None) -> Any:
        return await _call("orphans", {"total": total}, vault=vault)

    @server.tool(
        name="obsidian_deadends",
        description="List dead-end notes that contain no outgoing links to other notes.",
    )
    async def deadends(
        total: bool = False,
        all: bool = False,
        vault: str | None = None,
    ) -> Any:
        return await _call("deadends", {"total": total, "all": all}, vault=vault)

    @server.tool(
        name="obsidian_outline",
        description="Get the heading outline hierarchy of a note (returns JSON).",
    )
    async def outline(
        file: str | None = None,
        path: str | None = None,
        total: bool = False,
        vault: str | None = None,
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
        file: str | None = None,
        path: str | None = None,
        total: bool = False,
        verbose: bool = False,
        active: bool = False,
        vault: str | None = None,
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
        file: str | None = None,
        path: str | None = None,
        words: bool = False,
        characters: bool = False,
        vault: str | None = None,
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
        file: str | None = None,
        path: str | None = None,
        total: bool = False,
        counts: bool = False,
        sort: Literal["name", "count"] | None = None,
        active: bool = False,
        vault: str | None = None,
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
        name: str,
        total: bool = False,
        verbose: bool = False,
        vault: str | None = None,
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
        file: str | None = None,
        path: str | None = None,
        total: bool = False,
        done: bool = False,
        todo: bool = False,
        status: str | None = None,
        verbose: bool = False,
        active: bool = False,
        daily: bool = False,
        vault: str | None = None,
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
        ref: str | None = None,
        file: str | None = None,
        path: str | None = None,
        line: int | None = None,
        toggle: bool = False,
        done: bool = False,
        todo: bool = False,
        daily: bool = False,
        status: str | None = None,
        vault: str | None = None,
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
        info: Literal["name", "path", "files", "folders", "size"] | None = None,
        vault: str | None = None,
    ) -> Any:
        return await _call("vault", {"info": info}, vault=vault)

    @server.tool(
        name="obsidian_vaults",
        description="List all known Obsidian vaults and their local absolute paths.",
    )
    async def vaults(total: bool = False, verbose: bool = True) -> Any:
        return await _call("vaults", {"total": total, "verbose": verbose})

    @server.tool(
        name="obsidian_files",
        description="List files in the vault, with optional filtering by folder or file extension.",
    )
    async def files(
        folder: str | None = None,
        ext: str | None = None,
        total: bool = False,
        vault: str | None = None,
    ) -> Any:
        return await _call(
            "files", {"folder": folder, "ext": ext, "total": total}, vault=vault
        )

    @server.tool(
        name="obsidian_folders",
        description="List folders in the vault.",
    )
    async def folders(
        folder: str | None = None,
        total: bool = False,
        vault: str | None = None,
    ) -> Any:
        return await _call("folders", {"folder": folder, "total": total}, vault=vault)

    @server.tool(
        name="obsidian_folder",
        description="Show information about a specific folder.",
    )
    async def folder_info(
        path: str,
        info: Literal["files", "folders", "size"] | None = None,
        vault: str | None = None,
    ) -> Any:
        return await _call("folder", {"path": path, "info": info}, vault=vault)

    @server.tool(
        name="obsidian_recents",
        description="List recently opened files in the vault.",
    )
    async def recents(total: bool = False, vault: str | None = None) -> Any:
        return await _call("recents", {"total": total}, vault=vault)

    @server.tool(
        name="obsidian_bookmarks",
        description="List all bookmarks in the vault (returns JSON).",
    )
    async def bookmarks(
        total: bool = False,
        verbose: bool = False,
        vault: str | None = None,
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
    async def workspace(ids: bool = False, vault: str | None = None) -> Any:
        return await _call("workspace", {"ids": ids}, vault=vault)

    @server.tool(
        name="obsidian_reload",
        description="Reload the vault interface and re-index notes.",
    )
    async def reload_vault(vault: str | None = None) -> Any:
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
    async def execute_command(id: str, vault: str | None = None) -> Any:
        return await _call("command", {"id": id}, vault=vault)

    @server.tool(
        name="obsidian_commands",
        description="List all available Obsidian commands and their command IDs.",
    )
    async def list_commands(filter: str | None = None, vault: str | None = None) -> Any:
        return await _call("commands", {"filter": filter}, vault=vault)

    @server.tool(
        name="obsidian_template_read",
        description="Read a template file's content, with optional resolution of template variables.",
    )
    async def template_read(
        name: str,
        resolve: bool = False,
        title: str | None = None,
        vault: str | None = None,
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
    async def template_insert(name: str, vault: str | None = None) -> Any:
        return await _call("template:insert", {"name": name}, vault=vault)

    @server.tool(
        name="obsidian_eval",
        description="Execute JavaScript code inside the Obsidian Electron runtime and return the result.",
    )
    async def eval_js(code: str, vault: str | None = None) -> Any:
        return await _call("eval", {"code": code}, vault=vault)

    # ==========================================
    # 7. Plugins
    # ==========================================

    @server.tool(
        name="obsidian_plugins",
        description="List installed community or core plugins (returns JSON).",
    )
    async def plugins(
        filter: Literal["core", "community"] | None = None,
        versions: bool = False,
        vault: str | None = None,
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
        filter: Literal["core", "community"] | None = None,
        versions: bool = False,
        vault: str | None = None,
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
        id: str,
        filter: Literal["core", "community"] | None = None,
        vault: str | None = None,
    ) -> Any:
        return await _call("plugin:enable", {"id": id, "filter": filter}, vault=vault)

    @server.tool(
        name="obsidian_plugin_disable",
        description="Disable a specified plugin.",
    )
    async def plugin_disable(id: str, vault: str | None = None) -> Any:
        return await _call("plugin:disable", {"id": id}, vault=vault)
