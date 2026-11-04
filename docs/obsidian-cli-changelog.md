# Obsidian CLI 版本演进与变更记录

本文档汇总记录了 Obsidian 官方命令行接口（Obsidian CLI）从诞生至今在各个桌面端版本中的功能演进、命令增删、参数调整与重要修复。由于官方帮助文档仅展示最新版本全貌，本文档旨在为开发人员、Agent 开发者与使用者提供清晰的向后兼容参考。

---

## 📌 版本基准要求速览

- **最低可用版本**：**Obsidian v1.12.0**（首次引入 CLI 功能）。
- **推荐运行基准**：**Obsidian v1.12.7 及以上**（安装包内置独立二进制启动器，响应速度提升 90% 以上，解决了进程通信卡死与 socket 路径问题）。
- **当前最新特性**：**Obsidian v1.15.0**（新增按标题定向追加/前置插入与换行符微调）。

---

## 📅 版本演进时间线

### v1.15.0 (2026-10，Desktop Catalyst / Public)
- **命令与参数增强**：
  - `append` / `prepend` 新增 `heading=<title>` 参数，支持直接定位向指定标题区域下方追加或前置插入文本。
  - 新增控制追加/插入内容前后换行符排版的参数选项。

---

### v1.14.x (2026-09 ~ 2026-10，Desktop v1.14.0 ~ v1.14.5)
- **Bases 表格与看板集成**：
  - 支持对 `.base` 文件的关联 CLI 查询与交互命令：`bases`, `base:views`, `base:create`, `base:query`。
- **单文件与外部文件查看**：
  - 配合桌面端独立 Markdown 外部文件打开特性，增强了 `open` 针对外部路径的解析能力。
- **底层安全与运行时升级**：
  - v1.14.5 更新 Electron 至 43.8.3，修复关键安全缺陷。

---

### v1.13.x (2026-07 ~ 2026-08，Desktop v1.13.0 ~ v1.13.7)
- **跨平台与沙箱修复**：
  - 修复 Linux Flatpak 等沙箱打包环境下 CLI 与桌面主进程通信套接字连接中断的问题。
  - 优化高频调用下的内存回收与进程句柄清理。

---

### v1.12.7 (2026-03-23，Desktop Public) ★ 核心里程碑版本
- **架构革新**：
  - **独立二进制分发**：Obsidian 安装包（Installer）正式内置独立的轻量 CLI 二进制文件，取代早期通过调用 Electron 主二进制转发命令的旧机制，冷启动与执行延迟大幅降低。
  - **TUI 命令补全**：交互式终端（TUI）为 `command id=` 参数添加了 Obsidian 命令 ID 的实时自动补全功能。
- **系统通信修复**：
  - 将 macOS 和 Linux 下的 CLI 进程通信 socket 文件更改为标准隐藏点文件（dotfile），避免污染目录。
  - 修复了 macOS 系统错误检查 Linux 特定路径导致的偶发报错。
  - 增加了运行在旧版安装包（缺少独立 CLI 桥接）时的检测与警告提示。

---

### v1.12.1 ~ v1.12.4 (2026-02-10 ~ 2026-02-27，Desktop Catalyst & Public)
- **命令拆分与新增**：
  - 新增独立的 **`rename`** 命令，将重命名与路径移动（`move`）职责解耦。
  - 将 `search` 拆分为基础文本检索 **`search`** 与附带上下文预览的 **`search:context`**。
  - 新增 **`daily:path`** 子命令，用于直接获取当前/目标日记文件的预期绝对路径。
- **排版与 Frontmatter 保护**：
  - 优化 **`daily:prepend`** 插入位置：自动识别并跳过文件顶部的 YAML Frontmatter，将内容插入在属性区下方，而非文件最开头。
- **参数健壮性**：
  - 修正参数解析规则：支持忽略以 `--` 开头的未知 flags。
  - 修正 Windows 下包含冒号（`:`）的参数传递解析异常。
  - 强化 Unicode 多语言字符与长文本管道传输支持。
  - 确立 `vault=<name>` 规则：若指定目标库，必须作为命令行首个参数传递。

---

### v1.12.0 (2026-02-10，Desktop Early Access) ★ 初始引入
- **首次推出官方命令行工具 (Obsidian CLI)**：
  - 允许在终端通过命令行或交互式 TUI 完整操控 Obsidian 桌面应用，用于脚本化、自动化以及与外部 AI Agent 深度整合。
- **首发核心命令矩阵**：
  - **内容读写**：`read`, `create`, `append`, `prepend`, `delete`, `move`, `open`, `random`
  - **图谱双链**：`backlinks`, `links`, `unresolved`, `orphans`, `deadends`, `outline`, `aliases`, `wordcount`
  - **属性系统**：`properties`, `property:read`, `property:set`, `property:remove`
  - **标签任务**：`tags`, `tag`, `tasks`, `task`
  - **库与环境**：`vault`, `vaults`, `files`, `folders`, `folder`, `recents`, `bookmarks`, `workspace`, `reload`, `restart`, `version`
  - **插件扩展**：`command`, `commands`, `template:read`, `template:insert`, `plugins`, `plugins:enabled`, `plugin:enable`, `plugin:disable`
  - **开发者专用**：`eval`, `devtools`, `dev:screenshot`, `dev:console`, `dev:dom`, `dev:css` 等。

---


---

## ⚙️ obsidian-cli-mcp 的多版本自适应演进机制

本项目通过 `@dataclass Version` 与 `ToolRegistrar` 实现了针对不同 Obsidian 桌面版本的动态自适应模式：

1. **版本自动感知**：服务启动时通过 `obsidian version` 探针（或 `OBSIDIAN_VERSION` 环境变量）自动识别运行中的客户端版本；
2. **命令门禁过滤**：
   - 当 Obsidian 版本 `< 1.12.1` 时，自动跳过 `rename` 命令注册（因该版本尚未拆分 `rename`，引导 Agent 使用 `move`）；
   - 当 Obsidian 版本 `< 1.14.0` 时，自动跳过 `bases`, `base_views`, `base_query`, `base_create` 等 Bases 关联命令；
3. **参数模式演进（Schema Adaptation）**：
   - 对于 `append` 和 `prepend`：
     - 若版本 `< 1.14.0`：对外暴露不包含 `heading` 参数的基础 Schema，防止 Agent 产生参数幻觉；
     - 若版本 `>= 1.14.0`：自动升级为支持 `heading` 定向插入的扩展 Schema；
4. **无缝向前兼容**：未检测到版本（无头环境或 CLI 未运行）时，默认装载最新功能，保障开发者与生产环境的最高可用性。

## 🧭 官方参考来源

- [Obsidian CLI 官方使用指南 (Obsidian Help)](https://obsidian.md/help/cli)
- [Obsidian 官方发布日志 (Changelog)](https://obsidian.md/changelog/)
- [Obsidian 官方路线图 (Roadmap)](https://obsidian.md/roadmap/)
