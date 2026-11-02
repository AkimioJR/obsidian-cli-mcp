from typing import Any

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from ..client import ObsidianClient
from .base import NON_IDEMPOTENT_WRITE, READ_ONLY, call_tool


def register_task_tools(server: MCPServer, client: ObsidianClient) -> None:
    """Register task management tools (Feature: task)."""

    @server.tool(
        name="tasks",
        description="List tasks in the vault with optional filters for completion, note, or status (returns JSON).",
        annotations=READ_ONLY,
    )
    async def tasks(
        file: str | None = Field(
            default=None,
            description="Filter by file name.",
        ),
        path: str | None = Field(
            default=None,
            description="Filter by file path.",
        ),
        total: bool = Field(
            default=False,
            description="Return task count.",
        ),
        done: bool = Field(
            default=False,
            description="Show completed tasks.",
        ),
        todo: bool = Field(
            default=False,
            description="Show incomplete tasks.",
        ),
        status: str | None = Field(
            default=None,
            description="Filter by status character.",
        ),
        verbose: bool = Field(
            default=False,
            description="Group by file with line numbers.",
        ),
        active: bool = Field(
            default=False,
            description="Show tasks for active file.",
        ),
        daily: bool = Field(
            default=False,
            description="Show tasks from daily note.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "tasks",
            {
                "file": file,
                "path": path,
                "total": total,
                "done": done,
                "todo": todo,
                "status": status,
                "verbose": verbose,
                "active": active,
                "daily": daily,
                "format": "json",
            },
            parse_json=True,
            vault=vault,
        )

    @server.tool(
        name="task",
        description="Show or update a specific task status (toggle, mark done, or set status character).",
        annotations=NON_IDEMPOTENT_WRITE,
    )
    async def task(
        ref: str | None = Field(
            default=None,
            description="Task reference (path:line).",
        ),
        file: str | None = Field(
            default=None,
            description="File name.",
        ),
        path: str | None = Field(
            default=None,
            description="File path.",
        ),
        line: int | None = Field(
            default=None,
            description="Line number.",
        ),
        toggle: bool = Field(
            default=False,
            description="Toggle task status.",
        ),
        done: bool = Field(
            default=False,
            description="Mark as done.",
        ),
        todo: bool = Field(
            default=False,
            description="Mark as todo.",
        ),
        daily: bool = Field(
            default=False,
            description="Use daily note.",
        ),
        status: str | None = Field(
            default=None,
            description="Set status character.",
        ),
        vault: str | None = Field(
            default=None,
            description="Target a specific vault by name.",
        ),
    ) -> Any:
        return await call_tool(
            client,
            "task",
            {
                "ref": ref,
                "file": file,
                "path": path,
                "line": line,
                "toggle": toggle,
                "done": done,
                "todo": todo,
                "daily": daily,
                "status": status,
            },
            vault=vault,
        )
