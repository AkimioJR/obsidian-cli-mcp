import re
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

try:
    __version__ = version("obsidian-cli-mcp")
except PackageNotFoundError:
    try:
        pyproject_path = (
            Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
        )
        if pyproject_path.is_file():
            content = pyproject_path.read_text(encoding="utf-8")
            match = re.search(
                r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE
            )
            __version__ = match.group(1) if match else "0.0.0.dev"
        else:
            __version__ = "0.0.0.dev"
    except (OSError, UnicodeDecodeError):
        __version__ = "0.0.0.dev"

__all__ = ["__version__"]
