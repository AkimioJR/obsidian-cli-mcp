# obsidian-mcp

<p align="left">
  <a href="README.md">简体中文</a> | <b>English</b>
</p>

**An MCP (Model Context Protocol) server to control Obsidian vaults via the native Obsidian CLI.**

> **Why interact via Obsidian CLI instead of directly reading/writing vault files?**
> 1. **Ensure Runtime State & Plugin Synchronization**: Actions executed via CLI immediately update Obsidian's internal graph, Dataview cache, tag indexes, and active editor tabs without requiring app restarts or file system polling.
> 2. **Bypass macOS Privacy Protections (TCC)**: Direct file system operations across user directories often trigger macOS sandbox and Full Disk Access permissions. Interacting with the running Obsidian Electron app via its CLI requires no intrusive permissions.

---

## 🛠️ Prerequisites

1. **Obsidian Desktop App**: Installed and running.
2. **Obsidian CLI**: Available in your system `PATH` (e.g. `/opt/homebrew/bin/obsidian`).
   - Run `obsidian version` in your terminal to verify installation.

---

## ⚙️ Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `OBSIDIAN_VAULT` | Default target vault name (used when tool calls do not specify `vault`) | Binds to currently active vault if unset |
| `OBSIDIAN_CLI_PATH` | Absolute path to the Obsidian CLI executable | Automatically detected in system `PATH` (`which obsidian`) |

---

## 🚀 Quick Setup for MCP Clients

### Method 1: Run directly from GitHub via `uvx` (Recommended, Zero-install)

No need to clone the repository locally. `uvx` automatically pulls the latest code and launches the server in an isolated environment.

Add this to your Claude Desktop (`claude_desktop_config.json`), Cursor, or Codex (`mcp.json`):

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/AkimioJR/obsidian-mcp.git",
        "obsidian-mcp"
      ],
      "env": {
        "OBSIDIAN_VAULT": "MyVault"
      }
    }
  }
}
```

> **Tip**: To lock to a specific branch or version tag, append `@branch` or `@tag`:  
> `git+https://github.com/AkimioJR/obsidian-mcp.git@main`

---

### Method 2: Install as a standalone tool via `uv tool install` (Recommended for daily use)

Install `obsidian-mcp` as a global CLI command in an isolated environment without polluting your system Python:

```bash
uv tool install git+https://github.com/AkimioJR/obsidian-mcp.git
```

Once installed, use the standalone command directly in your MCP client config:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "obsidian-mcp",
      "env": {
        "OBSIDIAN_VAULT": "MyVault"
      }
    }
  }
}
```

> **Upgrade**: Update to the latest code anytime by running:  
> `uv tool upgrade obsidian-mcp`

---

### Method 3: Install via `pip` from GitHub

You can also install it into your active Python environment using `pip`:

```bash
pip install git+https://github.com/AkimioJR/obsidian-mcp.git
```

Then configure your MCP client with the installed binary:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "obsidian-mcp",
      "env": {
        "OBSIDIAN_VAULT": "MyVault"
      }
    }
  }
}
```

---

## 💻 Local Development

If you want to contribute or develop locally:

### 1. Clone Repository & Install Dependencies

```bash
git clone https://github.com/AkimioJR/obsidian-mcp.git
cd obsidian-mcp

# Sync all runtime, test, and dev dependencies using uv
uv sync
```

### 2. Run the MCP Server Locally

```bash
uv run obsidian-mcp
```

### 3. Local Development MCP Configuration

Point your MCP client directly to your local development checkout:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/obsidian-mcp",
        "run",
        "obsidian-mcp"
      ],
      "env": {
        "OBSIDIAN_VAULT": "MyVault"
      }
    }
  }
}
```

### 4. Run Tests & Code Quality Checks

```bash
# Run unit tests
uv run pytest

# Static type checking
uv run ty check src tests

# Formatting and linting
uv run ruff format .
uv run ruff check .
```

---

## 📦 Supported MCP Tools (45 1:1 Mapped CLI Commands)

All tools support an optional `vault` parameter to override the active vault per call. All parameters include full JSON Schema descriptions and type constraints.

### 1. Notes & Content
- `read`: Read the complete content of a note by file name or vault-relative path.
- `create`: Create a new note file with optional content, template, overwriting, and opening in app.
- `append`: Append content to the end of a specified note file.
- `prepend`: Prepend content to the beginning of a specified note file.
- `delete`: Delete a note file (moves to trash by default, or permanently deletes if `permanent=True`).
- `move`: Move or rename a note file to a destination folder or path.
- `rename`: Rename a note file.
- `open`: Open and focus a note file in the Obsidian workspace.
- `random_read`: Read a random note from the entire vault or a specified folder.

### 2. Metadata & Properties (Frontmatter)
- `properties`: List all frontmatter properties in the vault or for a specific file (returns JSON).
- `property_read`: Read the value of a specific property from a file.
- `property_set`: Set a property on a file with optional type (text, list, number, checkbox, date, datetime).
- `property_remove`: Remove a property from a file.

### 3. Graph & Links
- `backlinks`: List backlinks pointing to a specified note (returns JSON).
- `links`: List outgoing links from a specified note.
- `unresolved`: List unresolved links in the vault pointing to non-existent notes (returns JSON).
- `orphans`: List orphan notes that have no incoming links from other notes.
- `deadends`: List dead-end notes that contain no outgoing links to other notes.
- `outline`: Get the heading outline hierarchy of a note (returns JSON).
- `aliases`: List aliases in the vault or for a specified note.
- `wordcount`: Count words and characters in a note or the active note.

### 4. Tags & Tasks
- `tags`: List all tags and their occurrence counts in the vault or note (returns JSON).
- `tag`: Get details and file occurrences for a specific tag.
- `tasks`: List tasks in the vault with optional filters for completion, note, or status (returns JSON).
- `task`: Show or update a specific task status (toggle, mark done, or set status character).

### 5. Vault & Workspace
- `vault`: Show vault information such as name, path, file count, folder count, or total size.
- `vaults`: List all known Obsidian vaults and their local absolute paths.
- `files`: List files in the vault, with optional filtering by folder or file extension.
- `folders` / `obsidian_folder`: Inspect and list folder structures and details.
- `recents`: List recently opened files in the vault.
- `bookmarks`: List all bookmarks in the vault (returns JSON).
- `workspace`: Get the current workspace window layout tree.
- `reload` / `obsidian_restart` / `obsidian_version`: Reload vault, restart desktop app, or query version.

### 6. Commands & Automation
- `command`: Execute an Obsidian internal or plugin command by its command ID.
- `commands`: List all available Obsidian commands and their command IDs.
- `template_read`: Read a template file's content, with optional resolution of template variables.
- `template_insert`: Insert a template into the currently active note.
- `eval`: Execute JavaScript code inside the Obsidian Electron runtime and return the result.

### 7. Plugins
- `plugins` / `obsidian_plugins_enabled`: List installed or enabled plugins.
- `plugin_enable` / `obsidian_plugin_disable`: Enable or disable a specified plugin.
