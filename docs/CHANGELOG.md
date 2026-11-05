# 更新日志

本项目的所有重大变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
并且本项目遵循 [语义化版本 (Semantic Versioning)](https://semver.org/lang/zh-CN/)。

<!-- 历史版本按时间正序排列（从早到晚，最新版本追加在文末） -->

## [0.1.0] - 2026-11-01

### ✨ 新增
- **[Core]**: `obsidian-cli-mcp` 首次正式发布！基于官方 Obsidian CLI 封装的标准 MCP 2.x 服务，彻底绕过 macOS 自动化文件系统访问触发的 TCC 权限弹窗与系统沙箱限制。
- **[Client]**: 异步子进程客户端，支持键值对序列化、布尔 Flag 开关转换及空字符串防回退保护。
- **[Tools]**: 提供全套 Obsidian 基础操作工具，涵盖笔记增删改查、Frontmatter 属性读写、图谱与双向链接分析、标签管理、待办任务追踪、工作区与插件管理等核心能力。
- **[Tools]**: 所有工具参数采用 `typing.Literal` 精准约束枚举值，参数说明 1:1 对齐 `obsidian help` 官方规范。
- **[Server]**: 基于标准输入输出（Stdio）传输协议，支持零配置无缝接入 Claude Desktop、Cursor、Codex、DeepSeek-Harness 等主流 MCP 宿主环境。
- **[Docs]**: 提供完整的中英文双语使用指引（`README.md` 与 `README_en.md`），覆盖 `uv tool run`、`uvx`、`pip` 及源码安装等多种部署方式。

### 🔧 工程与维护
- **[Packaging]**: 遵循 PEP 561 规范，提供 `py.typed` 类型标记文件，确保使用者的 IDE 与 mypy/ty 工具获得完整的类型提示。
- **[Packaging]**: Python 运行环境要求设置为 `>=3.10`，兼顾现代 Python 特性与环境普及度。
- **[CI]**: 建立基于 GitHub Actions 的自动化工作流，涵盖 Ruff 代码检查、格式化校验、静态类型检查与 Pytest 测试，并支持基于 Git Tag 的自动打包与 PyPI / GitHub Release 发布。

## [0.1.1] - 2026-11-02

### ✨ 新增
- **[Tools]**: 工具集按领域重构为 9 大独立 Feature 模块（`note`, `property`, `tag`, `task`, `graph`, `vault`, `plugin`, `eval` 等），支持按需启用与预设组合 (`standard`, `all`)。
- **[Tools]**: 接入 MCP `ToolAnnotations` 元数据规范，为所有工具打上 `read_only`（只读）、`destructive`（破坏性操作）、`idempotent`（幂等性）等安全标注，提升 Agent 调用决策安全性。
- **[i18n]**: 新增工具展示标题国际化支持（`zh_CN` 与 `en_US`），默认根据系统 Locale 自动识别并优雅回退至英文，同时支持通过 `OBSIDIAN_LANG` 环境变量显式指定。
- **[Core]**: `__version__` 支持从包元数据及 `pyproject.toml` 动态读取，消除版本号重复硬编码。

### ⚡ 优化
- **[Tools]**: 引入 `ToolRegistrar` 注册器统一注入 feature 与 lang 上下文，彻底移除各工具定义中的样板代码。
- **[i18n]**: 将语言枚举封装为 `SupportedLang`，统一收敛语言标准化、自动探测及回退逻辑。
- **[Docs]**: 重构中英文 README 顶部徽标布局，整合 PyPI 状态、Python 版本、许可证与 CI 状态徽章。

### 🔧 工程与维护
- **[CI]**: 搭建跨平台矩阵测试流水线，支持在 Ubuntu (Linux)、macOS 与 Windows 多平台下验证核心功能。
- **[CI]**: 分离静态类型与代码风格检查，优化流水线触发路径，避免无意义的 CI 资源浪费。
- **[Packaging]**: 完善 PyPI 官方 Trove Classifiers，覆盖 Python 3.10 至 3.14 及操作系统环境标记。

## [0.2.0] - 2026-11-04

### ✨ 新增
- **[Core]**: 实现 `@dataclass(frozen=True) Version` 版本号解析器，支持版本号比较魔术方法与富语义校验，启动时自动探测本地 Obsidian 客户端版本。
- **[Core]**: 提取 `version`、`vaults` 与 `vault` 为系统内置的核心基础工具（Core Tools），无论启用何种 Feature 预设均默认无条件加载，便于安全感知与自检运行环境。
- **[Tools]**: 新增 `base`（Bases）Feature 特性组，为 Obsidian v1.14+ 实验性数据库视图提供 `bases`、`base_views`、`base_query`、`base_create` 4 项结构化数据操控工具。
- **[Tools]**: 支持按 Obsidian 运行版本动态自适应工具参数 Schema（例如 `append` 与 `prepend` 在 Obsidian >= 1.14 时自动暴露 `heading` 指定层级追加参数，低版本自动省略以保证向下兼容）。
- **[Client]**: 统一超时参数类型为 `float | None`，并新增 `OBSIDIAN_TIMEOUT` 环境变量支持，允许用户灵活配置子进程执行超时时限（默认 30.0s，设为 `"none"` 或 `"null"` 可禁用超时）。
- **[Docs]**: 在 `docs/obsidian-cli-changelog.md` 中整理 Obsidian 官方 CLI 各版本演进记录与参数变迁。
- **[Docs]**: 规范化 `docs/CHANGELOG.md`，并在发布工作流中集成基于更新日志的自动化 Release 说明提取与注入。

### ⚡ 优化
- **[Tools]**: 将默认加载的 Feature 预设优化为 `standard`（覆盖 NOTE、PROPERTY、TAG、TASK、GRAPH 核心场景，默认加载 28 项常用工具），减少冗余的高级工具对 Agent 上下文的占用。
- **[Docs]**: 澄清 Obsidian CLI 启用前置条件与系统要求（需 Obsidian v1.12.7+ 桌面客户端，并在“设置 -> 关于”中开启命令行界面支持），移除原文档中硬编码的“45项全量”表述。

### 🔧 工程与维护
- **[Packaging]**: 在 `pyproject.toml` 的 Trove Classifiers 中补充 Python 3.15 分类器。
- **[Test]**: 扩充版本解析、比较以及多版本下的工具 Schema 动态过滤单元测试（43/43 测试全量通过）。

## [0.3.0] - 2026-11-05

### ✨ 新增
- **[Developer]**: 全量封装 10 个官方开发者/调试命令（`dev_cdp`、`dev_console`、`dev_css`、`dev_debug`、`dev_dom`、`dev_errors`、`dev_mobile`、`dev_screenshot`、`dev_startup`、`devtools`），结合 `eval` 构成完整的 11 项开发者工具矩阵，支持 DOM/CSS 前端审查、日志与未处理异常捕获、应用冷启动耗时 breakdown（自动解析为结构化 JSON）以及窗口截图。
- **[Extensions]**: 引入复合扩展工具机制（通过 `OBSIDIAN_EXTENSIONS=true` 启用），新增 3 项高效扩展复合工具：
  - `edit`（`note` 域）：支持基于字面搜索匹配的局部精细修改与删除，避免重写整篇笔记带来的幻觉与大文本 Token 消耗。
  - `import_file`（`explorer` 域）：支持将外部本地 Markdown 笔记及各类图片/PDF/音视频附件无损直拷入库，零 Token 消耗并免除 JSON 转义开销。
  - `set_default_vault`（`core` 域）：支持在单会话内动态切换默认目标笔记库并校验库有效性，极大减少多库切换上下文开销。
- **[Tools]**: 补齐官方基础操作命令，新增原生 `bookmark`（新建书签）、`templates`（模板清单）、`file`（单文件系统信息）、`diff`（版本差异对比）、`tabs`（打开标签列表）、`tab_open`（分屏打开标签页）、`random`（界面漫游笔记）等能力。

### 🔄 重构
- **[Architecture]**: 全面重构为 **13 大高度内聚、职责清晰的独立 Feature 领域**，彻底消除原本宽泛的 `vault` 与临时过渡的 `other`：
  - `core`：基础环境探测与系统运维（收纳 `version`、`vaults`、`vault`、`reload`、`restart`）。
  - `note`：纯正文 Markdown 读写与修改（收纳 `diff`、`random`、`edit*`）。
  - `explorer`：文件系统与资产入库闭环（收纳 `files`、`file`、`folders`、`folder`、`recents`、`import_file*`）。
  - `workspace`：工作区窗口布局与标签页操控（收纳 `workspace`、`tabs`、`tab_open`）。
  - `bookmark`：独立书签与星标收藏系统（收纳 `bookmarks`、`bookmark`，与 `tag`、`task` 对称）。
  - `command`：命令面板与快捷指令（收纳 `command`、`commands`）。
  - `template`：模板管理与插入（收纳 `templates`、`template_read`、`template_insert`）。
  - `plugin`：纯粹的插件扩展生命周期管理（收纳 `plugins`、`plugins_enabled`、`plugin_enable`、`plugin_disable`）。
- **[Tools]**: 所有工具注册函数严格强制关键字传参（`*` keyword-only parameters），提升调用安全性与代码健壮性。
- **[i18n]**: 本地化标题字典全面适配 13 大 Feature 领域，支持中英文双语分层自动回退。

### 🎨 视觉与文档
- **[Assets]**: 全面重绘 `assets/readme/` 矢量视觉图（`hero.svg`、`tools-matrix.svg`、`workflow.svg` 及 `social-preview`），移除所有过时的硬编码工具数量与“1:1 映射”字样，同步最新 13 域架构，并将 Python 版本支持标记更新为 `Python 3.10 – 3.15`。
- **[Docs]**: 更新中英文双语 `README.md` 与 `README_en.md`，同步环境变量 `OBSIDIAN_FEATURES` 选项与 13 节详细功能清单。

### 🔧 测试与质量
- **[Test]**: 单元测试套件扩充至 63 项测试，覆盖参数序列化、动态 Schema 过滤、扩展工具门禁、CDP 与 DOM 审查以及所有 13 大功能域，测试通过率 100%。

<!-- ==================== 底部版本比对链接 (Reference Links) ==================== -->
[0.1.0]: https://github.com/AkimioJR/obsidian-cli-mcp/releases/tag/v0.1.0
[0.1.1]: https://github.com/AkimioJR/obsidian-cli-mcp/compare/v0.1.0...v0.1.1
[0.2.0]: https://github.com/AkimioJR/obsidian-cli-mcp/compare/v0.1.1...v0.2.0
[0.3.0]: https://github.com/AkimioJR/obsidian-cli-mcp/compare/v0.2.0...v0.3.0
