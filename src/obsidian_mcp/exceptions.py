class ObsidianError(Exception):
    """Base exception for obsidian-mcp."""


class ObsidianNotFoundError(ObsidianError):
    """Raised when obsidian CLI executable is not found."""


class ObsidianCLIError(ObsidianError):
    """Raised when obsidian CLI command execution fails."""

    def __init__(
        self,
        message: str,
        returncode: int | None = None,
        stderr: str = "",
        stdout: str = "",
    ) -> None:
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr
        self.stdout = stdout
