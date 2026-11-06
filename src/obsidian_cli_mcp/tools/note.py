import contextlib
import datetime
import json
import re
from pathlib import Path
from typing import Any, Literal

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


def _parse_daily_date(date_str: str | None) -> datetime.date:
    today = datetime.date.today()
    if not date_str or not date_str.strip():
        return today
    norm = date_str.strip().lower()
    if norm in ("today", "now"):
        return today
    if norm == "yesterday":
        return today - datetime.timedelta(days=1)
    if norm == "tomorrow":
        return today + datetime.timedelta(days=1)
    if norm.startswith(("+", "-")):
        try:
            days = int(norm)
            return today + datetime.timedelta(days=days)
        except ValueError:
            pass
    try:
        return datetime.date.fromisoformat(norm)
    except ValueError:
        pass
    for fmt in ("%Y/%m/%d", "%Y.%m.%d", "%Y%m%d", "%Y年%m月%d日"):
        try:
            return datetime.datetime.strptime(norm, fmt).date()
        except ValueError:
            pass
    raise ValueError(
        f"Cannot parse date '{date_str}'. Expected 'YYYY-MM-DD', 'yesterday', 'today', 'tomorrow', or relative offset like '+1'/'-1'."
    )


def _moment_to_strftime(fmt: str) -> str:
    tokens = [
        ("YYYY", "%Y"),
        ("YY", "%y"),
        ("MMMM", "%B"),
        ("MMM", "%b"),
        ("MM", "%m"),
        ("DD", "%d"),
        ("dddd", "%A"),
        ("ddd", "%a"),
        ("HH", "%H"),
        ("mm", "%M"),
        ("ss", "%S"),
    ]
    res = fmt
    for m_token, s_token in tokens:
        res = res.replace(m_token, s_token)
    return res


async def _resolve_daily_note_info(
    client: ObsidianClient, vault: str | None
) -> tuple[str, str, str | None]:
    """Returns (folder, format_str, template_path) for daily notes in vault."""
    vault_info = await call_tool(client, "vault", {"info": "path"}, vault=vault)
    folder = ""
    date_format = "YYYY-MM-DD"
    template: str | None = None

    if vault_info and not str(vault_info).startswith("Error:"):
        vault_path = Path(str(vault_info).strip()).resolve()
        daily_json = vault_path / ".obsidian" / "daily-notes.json"
        if daily_json.is_file():
            with contextlib.suppress(
                OSError, json.JSONDecodeError, ValueError, KeyError
            ):
                data = json.loads(
                    daily_json.read_text(encoding="utf-8", errors="replace")
                )
                if isinstance(data, dict):
                    folder = data.get("folder", "") or ""
                    date_format = data.get("format", "YYYY-MM-DD") or "YYYY-MM-DD"
                    template = data.get("template") or None
                    return folder, date_format, template

        periodic_json = (
            vault_path / ".obsidian" / "plugins" / "periodic-notes" / "data.json"
        )
        if periodic_json.is_file():
            with contextlib.suppress(
                OSError, json.JSONDecodeError, ValueError, KeyError
            ):
                data = json.loads(
                    periodic_json.read_text(encoding="utf-8", errors="replace")
                )
                if isinstance(data, dict):
                    daily_cfg = data.get("daily", {})
                    if isinstance(daily_cfg, dict) and daily_cfg.get("enabled", True):
                        folder = daily_cfg.get("folder", "") or ""
                        date_format = (
                            daily_cfg.get("format", "YYYY-MM-DD") or "YYYY-MM-DD"
                        )
                        template = daily_cfg.get("template") or None
                        return folder, date_format, template

    return folder, date_format, template


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
        name="diff",
        annotations=READ_ONLY,
        description="List or diff local and sync versions of a file.",
    )
    async def diff(
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        from_version: int | None = Field(
            default=None,
            description="Version number to diff from.",
        ),
        to_version: int | None = Field(
            default=None,
            description="Version number to diff to.",
        ),
        filter: Literal["local", "sync"] | None = Field(
            default=None,
            description="Filter by version source (local or sync).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "diff",
            {
                "file": file,
                "path": path,
                "from": from_version,
                "to": to_version,
                "filter": filter,
            },
            vault=vault,
        )

    @reg.tool(
        name="random",
        annotations=NON_IDEMPOTENT_WRITE,
        description="Open a random note in the Obsidian GUI.",
    )
    async def random(
        folder: str | None = Field(
            default=None,
            description="Limit to folder.",
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
            client, "random", {"folder": folder, "newtab": newtab}, vault=vault
        )

    @reg.tool(
        name="read_section",
        annotations=READ_ONLY,
        description=(
            "Read and extract a specific section or heading block from a markdown note. "
            "Substantially reduces context and token consumption for long documents. "
            "(Extension tool; enabled via OBSIDIAN_EXTENSIONS=true)"
        ),
        extension=True,
    )
    async def read_section(
        file: str | None = Field(
            default=None,
            description="Note name to read (e.g. 'Meeting.md').",
        ),
        path: str | None = Field(
            default=None,
            description="Exact note path in vault.",
        ),
        heading: str = Field(
            description="Target heading title to extract (case-insensitive, with or without leading '#').",
        ),
        include_subheadings: bool = Field(
            default=True,
            description="Whether to include content of child subheadings underneath the target heading (default: True).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> str:
        if not file and not path:
            return "Error: Either 'file' or 'path' must be provided."
        if not heading or not heading.strip():
            return "Error: 'heading' must not be empty."

        target = file or path
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

        norm_target = heading.lstrip("#").strip().lower()
        lines = content.splitlines()
        num_prefix_re = re.compile(r"^(\d+[\.\s、]+|[一二三四五六七八九十]+[、\.\s]+)")

        # 1. 调用 Obsidian 官方原生 outline 命令获取精准结构化 AST 大纲
        outline_res = await call_tool(
            client,
            "outline",
            {"file": file, "path": path, "format": "json"},
            parse_json=True,
            vault=vault,
        )

        if isinstance(outline_res, str) and outline_res.startswith("Error:"):
            return f"Error: Failed to retrieve outline AST for '{target}' ({outline_res}). Please use 'read' to inspect full note content."

        if not isinstance(outline_res, list) or not outline_res:
            return f"Error: Note '{target}' does not contain any parsed outline headings. Please use 'read' to view the entire note."

        # 2. 结构化大纲节点提取: [{"level": 1, "heading": "Title", "line": 26}, ...]
        ast_headings: list[tuple[int, int, str]] = []  # (outline_idx, level, title)
        available_headings: list[str] = []
        for idx, item in enumerate(outline_res):
            if isinstance(item, dict):
                lvl = int(item.get("level", 1))
                title = str(item.get("heading", "")).strip()
                ast_headings.append((idx, lvl, title))
                available_headings.append(title)

        if not ast_headings:
            return f"Error: Note '{target}' does not contain any valid outline headings. Please use 'read' to view the entire note."

        matched_ast_idx = -1
        matched_ast_level = 0

        # 匹配策略：精确匹配 -> 序号剥离匹配 -> 模糊包含匹配
        for idx, lvl, title in ast_headings:
            if title.lower() == norm_target:
                matched_ast_idx = idx
                matched_ast_level = lvl
                break

        if matched_ast_idx == -1:
            for idx, lvl, title in ast_headings:
                cleaned = num_prefix_re.sub("", title).strip()
                if cleaned.lower() == norm_target:
                    matched_ast_idx = idx
                    matched_ast_level = lvl
                    break

        if matched_ast_idx == -1:
            for idx, lvl, title in ast_headings:
                if norm_target in title.lower():
                    matched_ast_idx = idx
                    matched_ast_level = lvl
                    break

        if matched_ast_idx == -1:
            return f"Error: Heading '{heading}' not found in '{target}'. Available headings: {available_headings}"

        # 3. 按官方 AST 大纲返回的绝对 1-based 行号精准截取
        start_line = int(outline_res[matched_ast_idx].get("line", 1))
        next_boundary_line = -1
        for next_i in range(matched_ast_idx + 1, len(outline_res)):
            next_item = outline_res[next_i]
            if isinstance(next_item, dict):
                next_lvl = int(next_item.get("level", 1))
                if include_subheadings:
                    if next_lvl <= matched_ast_level:
                        next_boundary_line = int(next_item.get("line", -1))
                        break
                else:
                    next_boundary_line = int(next_item.get("line", -1))
                    break

        end_line = next_boundary_line - 1 if next_boundary_line != -1 else len(lines)
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        return "\n".join(lines[start_idx:end_idx]).strip()

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

    @reg.tool(
        name="daily",
        annotations=NON_IDEMPOTENT_WRITE,
        description=(
            "Manage daily notes (read, create, append, prepend, or get path). "
            "Automatically resolves vault daily note configuration (folder, format, and template from .obsidian/daily-notes.json). "
            "Supports natural dates like today, yesterday, tomorrow, +1, -1, or ISO YYYY-MM-DD. "
            "(Extension tool; enabled via OBSIDIAN_EXTENSIONS=true)"
        ),
        extension=True,
    )
    async def daily(
        action: Literal["read", "create", "append", "prepend", "get_path"] = Field(
            default="read",
            description="Action to perform: read (default), create, append, prepend, or get_path.",
        ),
        date: str | None = Field(
            default=None,
            description="Target date: today (default), yesterday, tomorrow, +1/-1, or YYYY-MM-DD.",
        ),
        content: str | None = Field(
            default=None,
            description="Content to append, prepend, or initialize with.",
        ),
        heading: str | None = Field(
            default=None,
            description="Target heading section when appending or prepending.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        try:
            dt = _parse_daily_date(date)
        except ValueError as e:
            return f"Error: {e}"

        folder, date_format, template = await _resolve_daily_note_info(client, vault)
        strftime_pat = _moment_to_strftime(date_format)
        file_stem = dt.strftime(strftime_pat)
        filename = f"{file_stem}.md" if not file_stem.endswith(".md") else file_stem
        if folder.strip():
            note_path = f"{folder.strip().strip('/')}/{filename}"
        else:
            note_path = filename

        # 1. get_path: 直接返回计算出的笔记路径
        if action == "get_path":
            return note_path

        # 2. read: 读取日记内容
        if action == "read":
            read_res = await call_tool(client, "read", {"path": note_path}, vault=vault)
            if isinstance(read_res, str) and (
                read_res.startswith("Error:") or "not found" in read_res.lower()
            ):
                return (
                    f"Daily note '{note_path}' (for date {dt.isoformat()}) does not exist yet. "
                    "Use action='create' or action='append' to create it."
                )
            return read_res

        # 3. create: 创建日记（若已存在则由 CLI 报错）
        if action == "create":
            create_args: dict[str, Any] = {
                "path": note_path,
                "content": content if content is not None else "",
                "overwrite": False,
            }
            if template:
                create_args["template"] = template
            create_res = await call_tool(client, "create", create_args, vault=vault)
            return create_res

        # 4. append / prepend: 追加或前置插入内容（如不存在则自动先行创建）
        if action in ("append", "prepend"):
            if content is None or not content.strip():
                return f"Error: 'content' must be provided when action is '{action}'."

            file_check = await call_tool(
                client, "file", {"path": note_path}, vault=vault
            )
            if isinstance(file_check, str) and (
                file_check.startswith("Error:") or "not found" in file_check.lower()
            ):
                init_args: dict[str, Any] = {
                    "path": note_path,
                    "content": "",
                    "overwrite": False,
                }
                if template:
                    init_args["template"] = template
                await call_tool(client, "create", init_args, vault=vault)

            op_args: dict[str, Any] = {
                "path": note_path,
                "content": content,
            }
            if heading and heading.strip():
                op_args["heading"] = heading.strip()

            op_res = await call_tool(client, action, op_args, vault=vault)
            if isinstance(op_res, str) and op_res.startswith("Error:"):
                return op_res

            heading_desc = (
                f" under heading '{heading.strip()}'"
                if heading and heading.strip()
                else ""
            )
            action_past = "appended to" if action == "append" else "prepended to"
            return f"Successfully {action_past} daily note '{note_path}'{heading_desc}."

        return f"Error: Unsupported daily action '{action}'."
