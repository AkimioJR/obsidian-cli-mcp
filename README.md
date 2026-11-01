# obsidian-mcp

**通过 Obsidian CLI 操控 Obsidian 笔记库的 MCP (Model Context Protocol) 服务器**

> **为什么通过 Obsidian CLI 而不是直接读写本地文件？**
> 1. **保证运行时状态与插件协同**：通过 CLI 触发的操作会即时刷新 Obsidian 的内部图谱、Dataview 缓存、标签索引与活动标签页，无需重启或等待文件系统扫描。
> 2. **绕过 macOS 隐私保护 (TCC)**：直接读写外部目录容易受到 macOS 文件夹权限与全盘访问限制，而通过 Obsidian 原生/官方 CLI（与运行中的 Electron 进程通信）无需额外授权。

---

## 🛠️ 前置条件

1. **Obsidian 桌面端**：已安装并正常运行。
2. **Obsidian CLI**：已在系统 PATH 中（如 `/opt/homebrew/bin/obsidian`）。
   - 可通过运行 `obsidian version` 检查可用性。

---

## ⚙️ 环境变量配置

| 环境变量 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `OBSIDIAN_VAULT` | 默认操控的 Vault 笔记库名称（工具未指定 `vault` 参数时使用） | 未设置时由 Obsidian CLI 自动绑定当前活跃库 |
| `OBSIDIAN_CLI_PATH` | Obsidian CLI 可执行文件的绝对路径 | 自动在 PATH 中探测（如 `which obsidian`） |

---

## 🚀 快速启动与 MCP 客户端配置

### 命令行运行

```bash
uv run obsidian-mcp
```

### 接入 Claude Desktop / Cursor / Codex

在客户端的 `claude_desktop_config.json` 或 `mcp.json` 中添加配置：

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/obsidian-mcp",
        "run",
        "obsidian-mcp"
      ],
      "env": {
        "OBSIDIAN_VAULT": "MyVault"
      }
    }
  }
}
```

---

## 📦 支持的 MCP 工具清单 (45 项全量 1:1 映射)

所有工具均支持可选的 `vault` 参数，用于临时跨库操作。

### 1. 笔记与内容 (Notes)
- `obsidian_read`: 按文件名或相对路径读取笔记内容。
- `obsidian_create`: 创建新笔记，支持指定模板、内容、是否覆盖与打开方式。
- `obsidian_append`: 向笔记末尾追加内容。
- `obsidian_prepend`: 向笔记开头前置插入内容。
- `obsidian_delete`: 删除笔记文件（默认移入回收站，支持永久删除）。
- `obsidian_move`: 移动或重命名笔记路径。
- `obsidian_rename`: 重命名笔记文件。
- `obsidian_open`: 在应用图形界面中聚焦打开笔记。
- `obsidian_random_read`: 随机读取一篇笔记。

### 2. 元数据与属性 (Properties & Frontmatter)
- `obsidian_properties`: 列出库或笔记的全部属性概览。
- `obsidian_property_read`: 读取指定属性值。
- `obsidian_property_set`: 设置属性值（支持 text、list、number、checkbox 等）。
- `obsidian_property_remove`: 移除指定属性。

### 3. 图谱与双链 (Graph & Links)
- `obsidian_backlinks`: 获取笔记的反向链接列表（JSON 格式）。
- `obsidian_links`: 获取笔记的外向链接列表。
- `obsidian_unresolved`: 列出未创建笔记的悬空双链。
- `obsidian_orphans`: 列出无反向链接的孤立文件。
- `obsidian_deadends`: 列出无外向链接的末端文件。
- `obsidian_outline`: 获取笔记的大纲标题层级（JSON 格式）。
- `obsidian_aliases`: 列出库中或指定文件的别名。
- `obsidian_wordcount`: 统计字数与字符数。

### 4. 标签与任务 (Tags & Tasks)
- `obsidian_tags`: 获取所有标签及其统计分布（JSON 格式）。
- `obsidian_tag`: 获取特定标签出现详情。
- `obsidian_tasks`: 按状态（已完成/待办）、标签或文件筛选任务。
- `obsidian_task`: 切换任务勾选状态或标记完成。

### 5. 库与工作区 (Vault & Workspace)
- `obsidian_vault`: 查询 Vault 基本状态（路径、文件数、体积等）。
- `obsidian_vaults`: 列出本机已知的所有 Vault 及绝对路径。
- `obsidian_files`: 列出库内文件（支持按文件夹、后缀筛选）。
- `obsidian_folders` / `obsidian_folder`: 查看文件夹结构与详情。
- `obsidian_recents`: 列出最近访问的文件。
- `obsidian_bookmarks`: 查看书签列表。
- `obsidian_workspace`: 查询工作区布局树。
- `obsidian_reload` / `obsidian_restart` / `obsidian_version`: 重新加载库、重启应用、查询版本。

### 6. 命令、模板与高级扩展 (Commands & Ext)
- `obsidian_command`: 触发执行 Obsidian 内置或插件命令。
- `obsidian_commands`: 列出所有可用的命令 ID 列表。
- `obsidian_template_read`: 读取模板并支持变量解析。
- `obsidian_template_insert`: 将模板插入到当前活跃笔记。
- `obsidian_eval`: 在 Obsidian 运行时中执行 JavaScript 代码（高级逃生通道）。

### 7. 插件管理 (Plugins)
- `obsidian_plugins` / `obsidian_plugins_enabled`: 列出已安装/已启用的插件。
- `obsidian_plugin_enable` / `obsidian_plugin_disable`: 启用或禁用指定插件。

---

## 🧪 运行测试与格式化

```bash
# 运行单元测试
uv run pytest

# 代码格式化与规范检查
uv run ruff format .
uv run ruff check .
```
