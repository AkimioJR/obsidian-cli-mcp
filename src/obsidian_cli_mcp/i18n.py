import locale
import os
from typing import Literal

SupportedLang = Literal["en_US", "zh_CN"]

DEFAULT_LANG: SupportedLang = "en_US"

# 按 [语言][Feature][工具名] 三层结构组织的本地化标题
TOOL_TITLES: dict[SupportedLang, dict[str, dict[str, str]]] = {
    "zh_CN": {
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
            "vault": "查询当前库信息",
            "vaults": "列出已知所有库",
            "files": "检索库内文件",
            "folders": "列出文件夹目录",
            "folder": "查询文件夹详情",
            "recents": "列出最近访问文件",
            "bookmarks": "查看书签星标",
            "workspace": "查询工作区布局",
            "reload": "重新加载笔记库",
            "restart": "重启 Obsidian",
            "version": "查看 Obsidian 版本",
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
        "eval": {
            "eval": "执行 JavaScript 代码",
        },
    },
    "en_US": {
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
            "vault": "Show Vault Info",
            "vaults": "List All Vaults",
            "files": "List Files in Vault",
            "folders": "List Folders",
            "folder": "Show Folder Details",
            "recents": "List Recent Files",
            "bookmarks": "List Bookmarks",
            "workspace": "Get Workspace Layout",
            "reload": "Reload Vault",
            "restart": "Restart Obsidian",
            "version": "Show Obsidian Version",
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
        "eval": {
            "eval": "Execute JavaScript",
        },
    },
}


def normalize_lang(raw: str | None) -> SupportedLang | None:
    """Normalize raw language string (e.g. 'zh', 'zh_CN', 'zh-CN', 'en', 'en-US') to SupportedLang."""
    if not raw:
        return None
    cleaned = raw.strip().lower().replace("-", "_")
    if cleaned.startswith("zh"):
        return "zh_CN"
    if cleaned.startswith("en"):
        return "en_US"
    return None


def detect_language(preferred: str | None = None) -> SupportedLang:
    """Detect language with priority:

    1. Explicit preferred parameter
    2. OBSIDIAN_LANG environment variable
    3. Standard env vars (LC_ALL, LC_MESSAGES, LANG)
    4. System locale via locale.getlocale()
    5. Fallback to DEFAULT_LANG (en_US)
    """
    # 1. Explicit parameter
    detected = normalize_lang(preferred)
    if detected:
        return detected

    # 2. OBSIDIAN_LANG
    detected = normalize_lang(os.getenv("OBSIDIAN_LANG"))
    if detected:
        return detected

    # 3. System environment variables
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.getenv(var)
        detected = normalize_lang(val)
        if detected:
            return detected

    # 4. Safe locale.getlocale()
    try:
        sys_loc, _ = locale.getlocale()
        detected = normalize_lang(sys_loc)
        if detected:
            return detected
    except (locale.Error, ValueError):
        pass

    # 5. Default fallback
    return DEFAULT_LANG


def get_tool_title(
    feature: str, tool_name: str, lang: SupportedLang | None = None
) -> str:
    """Get human-readable title for a tool under a specific feature and resolved language."""
    target_lang = lang or detect_language()
    features = TOOL_TITLES.get(target_lang, TOOL_TITLES[DEFAULT_LANG])
    feature_tools = features.get(feature, {})
    if tool_name in feature_tools:
        return feature_tools[tool_name]
    # Fallback to default lang
    return TOOL_TITLES[DEFAULT_LANG].get(feature, {}).get(tool_name, tool_name)
