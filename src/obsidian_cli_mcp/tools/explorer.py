import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from ..i18n import SupportedLang
from ..version import Version
from .base import NON_IDEMPOTENT_WRITE, READ_ONLY, ToolRegistrar, call_tool


def register_explorer_tools(
    server: MCPServer,
    client: ObsidianClient,
    *,
    lang: SupportedLang | str | None = None,
    version: Version | None = None,
    enable_extensions: bool = False,
) -> None:
    """Register file and directory explorer tools (Feature: explorer)."""
    reg = ToolRegistrar(
        server, "explorer", lang, version=version, enable_extensions=enable_extensions
    )

    @reg.tool(
        name="files",
        annotations=READ_ONLY,
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
        return await call_tool(
            client, "files", {"folder": folder, "ext": ext, "total": total}, vault=vault
        )

    @reg.tool(
        name="file",
        annotations=READ_ONLY,
        description="Show information about a specific file.",
    )
    async def file_info(
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
            client, "file", {"file": file, "path": path}, vault=vault
        )

    @reg.tool(
        name="folders",
        annotations=READ_ONLY,
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
        return await call_tool(
            client, "folders", {"folder": folder, "total": total}, vault=vault
        )

    @reg.tool(
        name="folder",
        annotations=READ_ONLY,
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
        return await call_tool(
            client, "folder", {"path": path, "info": info}, vault=vault
        )

    @reg.tool(
        name="recents",
        annotations=READ_ONLY,
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
        return await call_tool(client, "recents", {"total": total}, vault=vault)

    @reg.tool(
        name="search_content",
        annotations=READ_ONLY,
        description=(
            "Search for text or regular expressions across note contents in the Obsidian vault. "
            "Returns matching files, line numbers, and matching text snippets with context lines. "
            "(Extension tool; enabled via OBSIDIAN_EXTENSIONS=true)"
        ),
        extension=True,
    )
    async def search_content(
        query: str = Field(
            description="Search keyword or regular expression pattern to match across note contents (required).",
        ),
        folder: str | None = Field(
            default=None,
            description="Optional vault-relative subfolder to limit the search scope.",
        ),
        ext: str = Field(
            default="md",
            description="File extension to filter (default: 'md' for markdown notes). Use '*' to search all text files.",
        ),
        max_results: int = Field(
            default=20,
            description="Maximum number of matched occurrences to return (default: 20).",
        ),
        context_lines: int = Field(
            default=1,
            description="Number of context lines before and after each matching line (default: 1).",
        ),
        case_sensitive: bool = Field(
            default=False,
            description="Whether the search query should be case-sensitive (default: False).",
        ),
        regex: bool = Field(
            default=False,
            description="Whether to treat query as a regular expression (default: False, treats query as literal text).",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        if not query or not query.strip():
            return "Error: 'query' must not be empty."

        clean_query = query.strip()
        flags = 0 if case_sensitive else re.IGNORECASE
        if regex:
            try:
                pattern = re.compile(clean_query, flags)
            except re.error as e:
                return f"Error: Invalid regular expression: {e}"
        else:
            pattern = re.compile(re.escape(clean_query), flags)

        # 1. 尝试获取 Vault 路径进行本地高性能文件系统扫描
        vault_info = await call_tool(client, "vault", {"info": "path"}, vault=vault)
        vault_path_str = (
            str(vault_info).strip()
            if vault_info and not str(vault_info).startswith("Error:")
            else ""
        )

        matches: list[dict[str, Any]] = []
        fs_search_success = False

        if vault_path_str:
            vault_dir = Path(vault_path_str).resolve()
            if vault_dir.exists() and vault_dir.is_dir():
                if folder and folder.strip():
                    search_dir = (vault_dir / folder.strip().lstrip("/")).resolve()
                else:
                    search_dir = vault_dir

                try:
                    search_dir.relative_to(vault_dir)
                    if search_dir.exists() and search_dir.is_dir():
                        glob_pat = f"*.{ext.lstrip('.')}" if ext != "*" else "*"
                        for file_path in search_dir.rglob(glob_pat):
                            if not file_path.is_file():
                                continue
                            rel_to_vault = file_path.relative_to(vault_dir)
                            if any(part.startswith(".") for part in rel_to_vault.parts):
                                continue

                            try:
                                text = file_path.read_text(
                                    encoding="utf-8", errors="replace"
                                )
                            except OSError:
                                continue

                            lines = text.splitlines()
                            for i, line in enumerate(lines):
                                if pattern.search(line):
                                    start_idx = max(0, i - context_lines)
                                    end_idx = min(len(lines), i + context_lines + 1)
                                    ctx = "\n".join(
                                        f"{idx + 1}: {lines[idx]}"
                                        for idx in range(start_idx, end_idx)
                                    )
                                    matches.append(
                                        {
                                            "file": str(rel_to_vault),
                                            "line": i + 1,
                                            "match": line.strip(),
                                            "context": ctx,
                                        }
                                    )
                                    if len(matches) >= max_results:
                                        break
                            if len(matches) >= max_results:
                                break
                        fs_search_success = True
                except (ValueError, OSError):
                    # 触发目录越界或文件系统权限限制，转入通道 2
                    pass

        # 2. 如果文件系统直读不可用（如 macOS TCC 权限保护目录），回退至 Obsidian 运行时 in-memory 搜索
        if not fs_search_success:
            js_query = json.dumps(clean_query)
            js_folder = json.dumps(
                folder.strip().lstrip("/") if folder and folder.strip() else ""
            )
            js_ext = json.dumps(ext.lstrip(".") if ext != "*" else "*")
            js_max = max_results
            js_ctx = context_lines
            js_case = "true" if case_sensitive else "false"
            js_regex = "true" if regex else "false"

            js_code = f"""
(async () => {{{{
    const query = {js_query};
    const isRegex = {js_regex};
    const caseSensitive = {js_case};
    const folder = {js_folder};
    const ext = {js_ext};
    const maxResults = {js_max};
    const contextLines = {js_ctx};

    let re;
    try {{{{
        re = isRegex
            ? new RegExp(query, caseSensitive ? "g" : "gi")
            : new RegExp(query.replace(/[.*+?^${{{{}}}}|[\\]\\]/g, "\\$&"), caseSensitive ? "g" : "gi");
    }}}} catch(e) {{{{
        return {{{{ error: "Invalid regular expression: " + e.message }}}};
    }}}}

    const files = app.vault.getFiles().filter(f => {{{{
        if (ext !== "*" && f.extension !== ext) return false;
        if (folder && !f.path.startsWith(folder)) return false;
        return true;
    }}}});

    const matches = [];
    for (const f of files) {{{{
        const content = await app.vault.cachedRead(f);
        const lines = content.split("\\n");
        for (let i = 0; i < lines.length; i++) {{{{
            re.lastIndex = 0;
            if (re.test(lines[i])) {{{{
                const start = Math.max(0, i - contextLines);
                const end = Math.min(lines.length, i + contextLines + 1);
                const ctx = lines.slice(start, end).map((l, idx) => `${{{{start + idx + 1}}}}: ${{l}}`).join("\\n");
                matches.push({{{{
                    file: f.path,
                    line: i + 1,
                    match: lines[i].trim(),
                    context: ctx
                }}}});
                if (matches.length >= maxResults) break;
            }}}}
        }}}}
        if (matches.length >= maxResults) break;
    }}}}
    return {{{{ matches }}}};
}}}})()
"""
            eval_res = await call_tool(client, "eval", {"code": js_code}, vault=vault)
            if isinstance(eval_res, str) and eval_res.startswith("Error:"):
                return eval_res
            if isinstance(eval_res, dict):
                if "error" in eval_res:
                    return f"Error: {eval_res['error']}"
                matches = eval_res.get("matches", [])
            elif isinstance(eval_res, str) and eval_res.startswith("=>"):
                try:
                    parsed = json.loads(eval_res[2:].strip())
                    if isinstance(parsed, dict):
                        if "error" in parsed:
                            return f"Error: {parsed['error']}"
                        matches = parsed.get("matches", [])
                except json.JSONDecodeError:
                    pass

        if not matches:
            scope_desc = f" in folder '{folder}'" if folder else ""
            return f"No matches found for '{clean_query}'{scope_desc} in vault."

        header = f"Found {len(matches)} match(es) for '{clean_query}' in vault:\n"
        snippets = []
        for m in matches:
            snippets.append(f"--- {m['file']}:{m['line']} ---\n{m['context']}")
        return header + "\n\n" + "\n\n".join(snippets)

    @reg.tool(
        name="import_file",
        annotations=NON_IDEMPOTENT_WRITE,
        description=(
            "Import an external local file (from workspace or host) directly into the Obsidian vault. "
            "Performs fast, safe direct filesystem copy/move without passing content through JSON arguments. "
            "Supports markdown notes as well as binary attachments (images, PDFs, audio, etc.). "
            "(Extension tool; enabled via OBSIDIAN_EXTENSIONS=true)"
        ),
        extension=True,
    )
    async def import_file(
        source_path: str = Field(
            description="Absolute or relative path to the local source file on host (required).",
        ),
        path: str | None = Field(
            default=None,
            description="Destination relative path in vault (e.g. 'Reports/doc.md'). If omitted, imports to vault root using source filename.",
        ),
        overwrite: bool = Field(
            default=False,
            description="Whether to overwrite if destination file already exists in vault.",
        ),
        move: bool = Field(
            default=False,
            description="If True, moves (cuts) the source file into the vault instead of copying.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        if not source_path or not source_path.strip():
            return "Error: 'source_path' must be provided."

        src = Path(os.path.expanduser(source_path.strip())).resolve()
        if not src.exists():
            return f"Error: Source file '{source_path}' does not exist."
        if not src.is_file():
            return f"Error: Source path '{source_path}' is not a regular file."

        # 获取目标 Vault 的物理根目录路径
        vault_info = await call_tool(client, "vault", {"info": "path"}, vault=vault)
        if isinstance(vault_info, str) and vault_info.startswith("Error:"):
            return vault_info

        vault_path_str = str(vault_info).strip()
        if not vault_path_str:
            target_vault = vault or "current vault"
            return (
                f"Error: Could not determine vault directory path for '{target_vault}'."
            )

        vault_dir = Path(vault_path_str).resolve()
        if not vault_dir.exists() or not vault_dir.is_dir():
            return f"Error: Vault directory '{vault_dir}' does not exist or is not a directory."

        # 确定目标文件路径并做 Path Traversal 防御
        if path and path.strip():
            dest_rel = Path(path.strip().lstrip("/"))
            dest = (vault_dir / dest_rel).resolve()
        else:
            dest_rel = Path(src.name)
            dest = (vault_dir / dest_rel).resolve()

        try:
            dest.relative_to(vault_dir)
        except ValueError:
            return f"Error: Destination path '{path}' resolves outside the vault directory."

        if dest.exists() and not overwrite:
            return (
                f"Error: Destination file '{dest_rel}' already exists in vault. "
                "Set overwrite=True to replace it."
            )

        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if move:
                shutil.move(str(src), str(dest))
                action_verb = "moved"
            else:
                shutil.copy2(str(src), str(dest))
                action_verb = "copied"
        except OSError as e:
            action_name = "move" if move else "copy"
            return f"Error during file {action_name}: {e}"

        return (
            f"The file '{dest_rel}' has been successfully {action_verb} into the vault."
        )


__all__ = ["register_explorer_tools"]
