import os
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
