import contextlib
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

        # 获取 Vault 路径进行文件系统安全扫描
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

        if folder and folder.strip():
            search_dir = (vault_dir / folder.strip().lstrip("/")).resolve()
            try:
                search_dir.relative_to(vault_dir)
            except ValueError:
                return f"Error: Folder path '{folder}' resolves outside the vault directory."
            if not search_dir.exists() or not search_dir.is_dir():
                return f"No matches found for '{clean_query}' in folder '{folder}' in vault."
        else:
            search_dir = vault_dir

        matches: list[dict[str, Any]] = []
        glob_pat = f"*.{ext.lstrip('.')}" if ext != "*" else "*"

        for file_path in search_dir.rglob(glob_pat):
            if not file_path.is_file():
                continue
            rel_to_vault = file_path.relative_to(vault_dir)
            if any(part.startswith(".") for part in rel_to_vault.parts):
                continue

            try:
                text = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            lines_in_file = text.splitlines()
            for i, line_text in enumerate(lines_in_file):
                if pattern.search(line_text):
                    start_idx = max(0, i - context_lines)
                    end_idx = min(len(lines_in_file), i + context_lines + 1)
                    ctx = "\n".join(
                        f"{idx + 1}: {lines_in_file[idx]}"
                        for idx in range(start_idx, end_idx)
                    )
                    matches.append(
                        {
                            "file": rel_to_vault.as_posix(),
                            "line": i + 1,
                            "match": line_text.strip(),
                            "context": ctx,
                        }
                    )
                    if len(matches) >= max_results:
                        break
            if len(matches) >= max_results:
                break

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
                f"Error: Destination file '{dest_rel.as_posix()}' already exists in vault. "
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

        return f"The file '{dest_rel.as_posix()}' has been successfully {action_verb} into the vault."

    @reg.tool(
        name="attach_media",
        annotations=NON_IDEMPOTENT_WRITE,
        description=(
            "Copy a local media file (image, PDF, audio, video, etc.) into the vault\x27s configured attachment folder "
            "and optionally embed it into a target note in one step. Resolves the attachment directory from "
            ".obsidian/app.json (attachmentFolderPath). "
            "(Extension tool; enabled via OBSIDIAN_EXTENSIONS=true)"
        ),
        extension=True,
    )
    async def attach_media(
        source_path: str = Field(
            description="Absolute or relative path to the local media file on host (required).",
        ),
        note: str | None = Field(
            default=None,
            description="Target note (name or vault-relative path) to embed the media into. If omitted, only copies the file.",
        ),
        filename: str | None = Field(
            default=None,
            description="Custom vault filename for the media (defaults to source filename).",
        ),
        heading: str | None = Field(
            default=None,
            description="Target heading under which to insert the embed (appends at end if omitted).",
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

        # 读取附件目录配置 (attachmentFolderPath)
        attach_dir = ""
        app_json = vault_dir / ".obsidian" / "app.json"
        if app_json.is_file():
            with contextlib.suppress(OSError, json.JSONDecodeError):
                data = json.loads(
                    app_json.read_text(encoding="utf-8", errors="replace")
                )
                if isinstance(data, dict):
                    raw = data.get("attachmentFolderPath", "")
                    attach_dir = str(raw) if isinstance(raw, str) else ""

        # Obsidian 约定: "./xxx" 表示当前笔记同目录, "/" 或空 表示库根目录
        if attach_dir.startswith("./"):
            # 相对于目标笔记所在目录（若有 note）或库根目录
            base = vault_dir
            if note and note.strip():
                parent_res = await call_tool(
                    client, "file", {"path": note.strip()}, vault=vault
                )
                if (
                    (
                        (not isinstance(parent_res, str))
                        or (
                            not parent_res.startswith("Error:")
                            and "not found" not in parent_res.lower()
                        )
                    )
                    and isinstance(parent_res, dict)
                    and "path" in parent_res
                ):
                    # 尝试解析出笔记路径
                    base = (vault_dir / str(parent_res["path"])).parent
            attach_dir = (
                str(base.relative_to(vault_dir) / attach_dir[2:])
                if str(base.relative_to(vault_dir)) != "."
                else attach_dir[2:]
            )

        dest_dir = (
            vault_dir / attach_dir.lstrip("/") if attach_dir.strip() else vault_dir
        )

        vault_filename = filename.strip() if filename and filename.strip() else src.name
        dest = (dest_dir / vault_filename).resolve()
        try:
            dest.relative_to(vault_dir)
        except ValueError:
            return "Error: Destination path resolves outside the vault directory."

        if dest.exists():
            return (
                f"Error: File '{vault_filename}' already exists in attachment folder. "
                "Set a different 'filename'."
            )

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), str(dest))
        except OSError as e:
            return f"Error during file copy: {e}"

        vault_rel = dest.relative_to(vault_dir).as_posix()
        stem = dest.stem
        embed = f"![[{stem}]]"

        # 2. 嵌入到目标笔记
        if note and note.strip():
            note_ref = note.strip()
            read_res = await call_tool(client, "read", {"path": note_ref}, vault=vault)
            if isinstance(read_res, str) and read_res.startswith("Error:"):
                read_res = await call_tool(
                    client, "read", {"file": note_ref}, vault=vault
                )
                if isinstance(read_res, str) and read_res.startswith("Error:"):
                    return (
                        f"Error: Target note '{note_ref}' not found. "
                        f"Media file was still copied to '{vault_rel}'."
                    )

            content = str(read_res)
            if heading and heading.strip():
                content = content.rstrip() + f"\n\n## {heading.strip()}\n\n{embed}\n"
            else:
                content = content.rstrip() + f"\n\n{embed}\n"

            write_args: dict[str, Any] = {"content": content, "overwrite": True}
            if "/" in note_ref and note_ref.endswith(".md"):
                write_args["path"] = note_ref
            else:
                write_args["name"] = note_ref

            write_res = await call_tool(client, "create", write_args, vault=vault)
            if isinstance(write_res, str) and write_res.startswith("Error:"):
                return write_res

            heading_desc = (
                f" under heading '{heading.strip()}'"
                if heading and heading.strip()
                else ""
            )
            return (
                f"Media '{vault_rel}' copied into vault and embedded into '{note_ref}'"
                f"{heading_desc} as {embed}."
            )

        return f"Media '{vault_rel}' copied into vault (not embedded; no target note provided)."


__all__ = ["register_explorer_tools"]
