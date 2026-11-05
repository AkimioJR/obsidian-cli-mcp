import locale
import os
from enum import Enum


class SupportedLang(str, Enum):
    """Supported localization languages for Obsidian CLI MCP."""

    EN_US = "en_US"
    ZH_CN = "zh_CN"

    @property
    def titles(self) -> dict[str, dict[str, str]]:
        """Get the dictionary of tool titles for this language."""
        return _TOOL_TITLES.get(self, _TOOL_TITLES[SupportedLang.EN_US])

    @classmethod
    def all_titles(cls) -> dict["SupportedLang", dict[str, dict[str, str]]]:
        """Get the full dictionary of all tool titles across all supported languages."""
        return _TOOL_TITLES

    @classmethod
    def normalize(cls, raw: str | None) -> "SupportedLang | None":
        """Normalize raw language string (e.g. 'zh', 'zh_CN', 'zh-CN', 'en', 'en-US') to SupportedLang."""
        if not raw:
            return None
        cleaned = raw.strip().lower().replace("-", "_")
        if cleaned.startswith("zh"):
            return cls.ZH_CN
        if cleaned.startswith("en"):
            return cls.EN_US
        return None

    @classmethod
    def detect(cls, preferred: str | None = None) -> "SupportedLang":
        """Detect language with priority:

        1. Explicit preferred parameter
        2. OBSIDIAN_LANG environment variable
        3. Standard env vars (LC_ALL, LC_MESSAGES, LANG)
        4. System locale via locale.getlocale()
        5. Fallback to EN_US
        """
        # 1. Explicit parameter
        detected = cls.normalize(preferred)
        if detected:
            return detected

        # 2. OBSIDIAN_LANG
        detected = cls.normalize(os.getenv("OBSIDIAN_LANG"))
        if detected:
            return detected

        # 3. System environment variables
        for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
            val = os.getenv(var)
            detected = cls.normalize(val)
            if detected:
                return detected

        # 4. Safe locale.getlocale()
        try:
            sys_loc, _ = locale.getlocale()
            detected = cls.normalize(sys_loc)
            if detected:
                return detected
        except (locale.Error, ValueError):
            pass

        # 5. Default fallback
        return cls.EN_US

    def tool_title(self, feature: str, tool_name: str) -> str | None:
        """Get localized tool title under this language.

        Fallback to en_US if not found in current language.
        Return None if not found in en_US either.
        """
        # 1. Check current language
        feat_dict = self.titles.get(feature)
        if feat_dict and tool_name in feat_dict:
            return feat_dict[tool_name]

        # 2. Fallback to en_US if current language is not en_US
        if self != SupportedLang.EN_US:
            en_feat_dict = SupportedLang.EN_US.titles.get(feature, {})
            if tool_name in en_feat_dict:
                return en_feat_dict[tool_name]

        # 3. Not found in en_US either
        return None


# 按 [语言][Feature][工具名] 三层结构组织的私有本地化标题存储
_TOOL_TITLES: dict[SupportedLang, dict[str, dict[str, str]]] = {
    SupportedLang.ZH_CN: {
        "core": {
            "version": "查看 Obsidian 版本",
            "vaults": "列出已知所有库",
            "vault": "查询当前库信息",
            "set_default_vault": "切换默认笔记库",
        },
        "note": {
            "read": "读取笔记",
            "create": "创建笔记",
            "append": "追加笔记内容",
            "prepend": "前置插入笔记",
            "delete": "删除笔记",
            "move": "移动笔记",
            "rename": "重命名笔记",
            "open": "聚焦打开笔记",
            "random_read": "随机漫游笔记",
            "edit": "编辑修改笔记",
            "import_file": "导入外部文件",
        },
        "property": {
            "properties": "查看属性概览",
            "property_read": "读取属性值",
            "property_set": "设置属性值",
            "property_remove": "移除属性字段",
        },
        "tag": {
            "tags": "列出所有标签",
            "tag": "检索特定标签",
        },
        "task": {
            "tasks": "多维筛选任务",
            "task": "切换任务状态",
        },
        "graph": {
            "backlinks": "获取反向链接",
            "links": "获取外向链接",
            "unresolved": "列出未创建双链",
            "orphans": "列出孤立文件",
            "deadends": "列出末端文件",
            "outline": "获取大纲标题",
            "aliases": "查看笔记别名",
            "wordcount": "统计字数字符",
        },
        "vault": {
            "files": "检索库内文件",
            "folders": "列出文件夹目录",
            "folder": "查询文件夹详情",
            "recents": "列出最近访问文件",
            "bookmarks": "查看书签星标",
            "workspace": "查询工作区布局",
            "reload": "重新加载笔记库",
            "restart": "重启 Obsidian",
        },
        "plugin": {
            "command": "执行命令",
            "commands": "列出可用命令",
            "template_read": "读取模板内容",
            "template_insert": "插入模板到当前笔记",
            "plugins": "列出已安装插件",
            "plugins_enabled": "列出已启用插件",
            "plugin_enable": "启用插件",
            "plugin_disable": "禁用插件",
        },
        "base": {
            "bases": "列出所有Bases文件",
            "base_views": "获取Bases视图列表",
            "base_query": "查询Bases表格数据",
            "base_create": "新建Bases条目",
        },
        "developer": {
            "eval": "执行 JavaScript 代码",
        },
        "other": {
            "bookmark": "添加书签",
            "templates": "列出模板清单",
            "file": "查询文件信息",
            "diff": "对比版本差异",
            "tabs": "列出打开的标签页",
            "tab_open": "打开新标签页",
            "random": "界面随机漫游笔记",
        },
    },
    SupportedLang.EN_US: {
        "core": {
            "version": "Show Obsidian Version",
            "vaults": "List All Vaults",
            "vault": "Show Vault Info",
            "set_default_vault": "Set Default Vault",
        },
        "note": {
            "read": "Read Note",
            "create": "Create Note",
            "append": "Append Note Content",
            "prepend": "Prepend Note Content",
            "delete": "Delete Note",
            "move": "Move Note",
            "rename": "Rename Note",
            "open": "Open & Focus Note",
            "random_read": "Read Random Note",
            "edit": "Edit Note Content",
            "import_file": "Import External File",
        },
        "property": {
            "properties": "List Properties",
            "property_read": "Read Property",
            "property_set": "Set Property",
            "property_remove": "Remove Property",
        },
        "tag": {
            "tags": "List All Tags",
            "tag": "Search by Tag",
        },
        "task": {
            "tasks": "Filter Tasks",
            "task": "Toggle Task Status",
        },
        "graph": {
            "backlinks": "Get Backlinks",
            "links": "Get Outgoing Links",
            "unresolved": "List Unresolved Links",
            "orphans": "List Orphan Notes",
            "deadends": "List Dead-end Notes",
            "outline": "Get Note Outline",
            "aliases": "List Aliases",
            "wordcount": "Count Words & Characters",
        },
        "vault": {
            "files": "List Files in Vault",
            "folders": "List Folders",
            "folder": "Show Folder Details",
            "recents": "List Recent Files",
            "bookmarks": "List Bookmarks",
            "workspace": "Get Workspace Layout",
            "reload": "Reload Vault",
            "restart": "Restart Obsidian",
        },
        "plugin": {
            "command": "Execute Command",
            "commands": "List Commands",
            "template_read": "Read Template",
            "template_insert": "Insert Template to Note",
            "plugins": "List Installed Plugins",
            "plugins_enabled": "List Enabled Plugins",
            "plugin_enable": "Enable Plugin",
            "plugin_disable": "Disable Plugin",
        },
        "base": {
            "bases": "List Base Files",
            "base_views": "List Base Views",
            "base_query": "Query Base Records",
            "base_create": "Create Base Item",
        },
        "developer": {
            "eval": "Execute JavaScript",
        },
        "other": {
            "bookmark": "Add Bookmark",
            "templates": "List Templates",
            "file": "Show File Details",
            "diff": "Compare Versions",
            "tabs": "List Open Tabs",
            "tab_open": "Open New Tab",
            "random": "Open Random Note in GUI",
        },
    },
}

__all__ = ["SupportedLang"]
