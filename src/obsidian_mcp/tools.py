from typing import Any
from mcp.server.mcpserver import MCPServer
from .client import ObsidianClient
from .exceptions import ObsidianError


def register_tools(server: MCPServer, client: ObsidianClient) -> None:
    """注册所有 Obsidian CLI 1:1 对应的 MCP 工具。"""

    async def _call(
        command: str,
        params: dict[str, Any] | None = None,
        *,
        parse_json: bool = False,
        vault: str | None = None,
    ) -> Any:
        try:
            return await client.execute(command, params, parse_json=parse_json, vault=vault)
        except ObsidianError as e:
            return f"Error: {e}"

    # ==========================================
    # 1. 笔记与内容 (Notes & Content)
    # ==========================================

    @server.tool(name="obsidian_read", description="读取笔记文件完整内容。可按名称(file)或相对路径(path)查找。")
    async def read(file: str | None = None, path: str | None = None, vault: str | None = None) -> Any:
        return await _call("read", {"file": file, "path": path}, vault=vault)

    @server.tool(
        name="obsidian_create",
        description="创建新笔记文件。支持指定初始内容、模板、是否覆盖及是否在应用中打开。",
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

    @server.tool(name="obsidian_append", description="向指定笔记文件末尾追加内容。")
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

    @server.tool(name="obsidian_prepend", description="向指定笔记文件开头前置插入内容。")
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

    @server.tool(name="obsidian_delete", description="删除指定笔记文件。默认移至废纸篓，设置 permanent=True 可永久删除。")
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

    @server.tool(name="obsidian_move", description="移动或重命名笔记文件到目标文件夹或目标路径。")
    async def move(
        to: str,
        file: str | None = None,
        path: str | None = None,
        vault: str | None = None,
    ) -> Any:
        return await _call("move", {"to": to, "file": file, "path": path}, vault=vault)

    @server.tool(name="obsidian_rename", description="重命名笔记文件名。")
    async def rename(
        name: str,
        file: str | None = None,
        path: str | None = None,
        vault: str | None = None,
    ) -> Any:
        return await _call("rename", {"name": name, "file": file, "path": path}, vault=vault)

    @server.tool(name="obsidian_open", description="在 Obsidian 图形窗口中打开指定文件。")
    async def open_file(
        file: str | None = None,
        path: str | None = None,
        newtab: bool = False,
        vault: str | None = None,
    ) -> Any:
        return await _call("open", {"file": file, "path": path, "newtab": newtab}, vault=vault)

    @server.tool(name="obsidian_random_read", description="随机读取库或指定文件夹中的一篇笔记。")
    async def random_read(folder: str | None = None, vault: str | None = None) -> Any:
        return await _call("random:read", {"folder": folder}, vault=vault)

    # ==========================================
    # 2. 元数据与属性 (Properties & Frontmatter)
    # ==========================================

    @server.tool(name="obsidian_properties", description="列出库或指定文件中的所有属性 (Frontmatter/Properties)。")
    async def properties(
        file: str | None = None,
        path: str | None = None,
        name: str | None = None,
        total: bool = False,
        sort: str | None = None,
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

    @server.tool(name="obsidian_property_read", description="读取指定文件上某个属性的值。")
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
        description="设置指定文件上的某个属性值。支持 text/list/number/checkbox/date/datetime 等类型。",
    )
    async def property_set(
        name: str,
        value: str,
        type: str | None = None,
        file: str | None = None,
        path: str | None = None,
        vault: str | None = None,
    ) -> Any:
        return await _call(
            "property:set",
            {"name": name, "value": value, "type": type, "file": file, "path": path},
            vault=vault,
        )

    @server.tool(name="obsidian_property_remove", description="从指定文件中移除某个属性。")
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
    # 3. 图谱与双链 (Graph & Links)
    # ==========================================

    @server.tool(name="obsidian_backlinks", description="获取指向指定笔记的反向链接列表（返回 JSON 结构）。")
    async def backlinks(
        file: str | None = None,
        path: str | None = None,
        counts: bool = False,
        total: bool = False,
        vault: str | None = None,
    ) -> Any:
        return await _call(
            "backlinks",
            {"file": file, "path": path, "counts": counts, "total": total, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @server.tool(name="obsidian_links", description="获取指定笔记中的所有外向链接列表。")
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

    @server.tool(name="obsidian_unresolved", description="列出库中所有未解析的双链（即尚未创建的笔记链接）。")
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

    @server.tool(name="obsidian_orphans", description="列出库中没有被任何其他笔记反向链接的孤立笔记文件。")
    async def orphans(total: bool = False, vault: str | None = None) -> Any:
        return await _call("orphans", {"total": total}, vault=vault)

    @server.tool(name="obsidian_deadends", description="列出库中没有指向任何其他笔记的末端笔记文件。")
    async def deadends(
        total: bool = False,
        all: bool = False,
        vault: str | None = None,
    ) -> Any:
        return await _call("deadends", {"total": total, "all": all}, vault=vault)

    @server.tool(name="obsidian_outline", description="获取指定笔记文件的大纲标题层级结构（返回 JSON）。")
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

    @server.tool(name="obsidian_aliases", description="获取库中或指定文件的别名 (aliases) 列表。")
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
            {"file": file, "path": path, "total": total, "verbose": verbose, "active": active},
            vault=vault,
        )

    @server.tool(name="obsidian_wordcount", description="统计指定笔记或当前笔记的字数与字符数。")
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
    # 4. 标签与任务 (Tags & Tasks)
    # ==========================================

    @server.tool(name="obsidian_tags", description="获取库中或指定笔记中的所有标签 (tags) 列表及出现频次。")
    async def tags(
        file: str | None = None,
        path: str | None = None,
        total: bool = False,
        counts: bool = False,
        sort: str | None = None,
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

    @server.tool(name="obsidian_tag", description="获取特定标签的详细出现信息与文件列表。")
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

    @server.tool(name="obsidian_tasks", description="获取库中或指定笔记中的任务 (tasks) 待办事项列表。")
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

    @server.tool(name="obsidian_task", description="查看或更新特定任务的状态（勾选、取消、标记完成等）。")
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
    # 5. 库与工作区 (Vault & Workspace)
    # ==========================================

    @server.tool(name="obsidian_vault", description="查看指定或当前 Vault 的基本信息（名称、路径、文件数、体积等）。")
    async def vault_info(info: str | None = None, vault: str | None = None) -> Any:
        return await _call("vault", {"info": info}, vault=vault)

    @server.tool(name="obsidian_vaults", description="列出本机已知的所有 Obsidian Vault 列表及绝对路径。")
    async def vaults(total: bool = False, verbose: bool = True) -> Any:
        return await _call("vaults", {"total": total, "verbose": verbose})

    @server.tool(name="obsidian_files", description="列出库内所有文件，可按目录或扩展名筛选。")
    async def files(
        folder: str | None = None,
        ext: str | None = None,
        total: bool = False,
        vault: str | None = None,
    ) -> Any:
        return await _call("files", {"folder": folder, "ext": ext, "total": total}, vault=vault)

    @server.tool(name="obsidian_folders", description="列出库中的文件夹列表。")
    async def folders(
        folder: str | None = None,
        total: bool = False,
        vault: str | None = None,
    ) -> Any:
        return await _call("folders", {"folder": folder, "total": total}, vault=vault)

    @server.tool(name="obsidian_folder", description="查看指定文件夹的详情信息。")
    async def folder_info(
        path: str,
        info: str | None = None,
        vault: str | None = None,
    ) -> Any:
        return await _call("folder", {"path": path, "info": info}, vault=vault)

    @server.tool(name="obsidian_recents", description="列出最近打开过的文件列表。")
    async def recents(total: bool = False, vault: str | None = None) -> Any:
        return await _call("recents", {"total": total}, vault=vault)

    @server.tool(name="obsidian_bookmarks", description="获取库中所有的书签 (bookmarks) 列表。")
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

    @server.tool(name="obsidian_workspace", description="获取当前工作区窗口布局树结构。")
    async def workspace(ids: bool = False, vault: str | None = None) -> Any:
        return await _call("workspace", {"ids": ids}, vault=vault)

    @server.tool(name="obsidian_reload", description="重新加载当前 Vault 界面与索引。")
    async def reload_vault(vault: str | None = None) -> Any:
        return await _call("reload", vault=vault)

    @server.tool(name="obsidian_restart", description="重启整个 Obsidian 桌面应用程序。")
    async def restart_app() -> Any:
        return await _call("restart")

    @server.tool(name="obsidian_version", description="获取当前安装的 Obsidian 客户端版本号。")
    async def version() -> Any:
        return await _call("version")

    # ==========================================
    # 6. 命令、模板与扩展 (Commands & Ext)
    # ==========================================

    @server.tool(name="obsidian_command", description="通过命令 ID 直接触发执行 Obsidian 的内置或插件命令。")
    async def execute_command(id: str, vault: str | None = None) -> Any:
        return await _call("command", {"id": id}, vault=vault)

    @server.tool(name="obsidian_commands", description="列出 Obsidian 当前所有可用的命令及其 ID。")
    async def list_commands(filter: str | None = None, vault: str | None = None) -> Any:
        return await _call("commands", {"filter": filter}, vault=vault)

    @server.tool(name="obsidian_template_read", description="读取模板文件的内容，可选择解析内置模板变量。")
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

    @server.tool(name="obsidian_template_insert", description="将指定模板插入到当前活跃的笔记中。")
    async def template_insert(name: str, vault: str | None = None) -> Any:
        return await _call("template:insert", {"name": name}, vault=vault)

    @server.tool(name="obsidian_eval", description="在 Obsidian Electron 运行时环境中执行 JavaScript 代码并返回执行结果。")
    async def eval_js(code: str, vault: str | None = None) -> Any:
        return await _call("eval", {"code": code}, vault=vault)

    # ==========================================
    # 7. 插件管理 (Plugins)
    # ==========================================

    @server.tool(name="obsidian_plugins", description="列出已安装的插件列表（支持区分 core/community）。")
    async def plugins(
        filter: str | None = None,
        versions: bool = False,
        vault: str | None = None,
    ) -> Any:
        return await _call(
            "plugins",
            {"filter": filter, "versions": versions, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @server.tool(name="obsidian_plugins_enabled", description="列出当前已启用的插件列表。")
    async def plugins_enabled(
        filter: str | None = None,
        versions: bool = False,
        vault: str | None = None,
    ) -> Any:
        return await _call(
            "plugins:enabled",
            {"filter": filter, "versions": versions, "format": "json"},
            parse_json=True,
            vault=vault,
        )

    @server.tool(name="obsidian_plugin_enable", description="启用指定的社区或核心插件。")
    async def plugin_enable(
        id: str,
        filter: str | None = None,
        vault: str | None = None,
    ) -> Any:
        return await _call("plugin:enable", {"id": id, "filter": filter}, vault=vault)

    @server.tool(name="obsidian_plugin_disable", description="禁用指定的插件。")
    async def plugin_disable(id: str, vault: str | None = None) -> Any:
        return await _call("plugin:disable", {"id": id}, vault=vault)
