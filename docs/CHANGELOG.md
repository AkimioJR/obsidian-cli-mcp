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

<!-- ==================== 底部版本比对链接 (Reference Links) ==================== -->
[0.1.0]: https://github.com/AkimioJR/obsidian-cli-mcp/releases/tag/v0.1.0
[0.1.1]: https://github.com/AkimioJR/obsidian-cli-mcp/compare/v0.1.0...v0.1.1
