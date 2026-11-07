import asyncio
from dataclasses import dataclass


@dataclass
class CommandExecutionResult:
    returncode: int | None
    stdout: str
    stderr: str


async def run_cli_command(
    program: str, args: list[str], *, timeout: float | None = 30.0
) -> CommandExecutionResult:
    """运行 CLI 子进程命令并等待输出。"""
    try:
        process = await asyncio.create_subprocess_exec(
            program,
            *args,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

        return CommandExecutionResult(
            returncode=process.returncode,
            stdout=stdout.decode("utf-8", errors="replace").strip(),
            stderr=stderr.decode("utf-8", errors="replace").strip(),
        )
    except TimeoutError:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        await process.wait()
        timeout_msg = f" after {timeout} seconds" if timeout is not None else ""
        return CommandExecutionResult(
            returncode=-1,
            stdout="",
            stderr=f"Command timed out{timeout_msg}",
        )
