---
description: How to use uv for Python dependency management
---

# uv Package Manager Workflow

uv is a fast Python package manager and project manager. Use this guide for dependency management tasks.

## Quick Reference

| Task                     | Command                  | Notes                                |
| ------------------------ | ------------------------ | ------------------------------------ |
| Install all dependencies | `uv sync`                | Installs exactly what's in uv.lock   |
| Add a package            | `uv add <pkg>`           | Updates pyproject.toml + uv.lock     |
| Add dev dependency       | `uv add --dev <pkg>`     | Adds to dev dependencies             |
| Remove a package         | `uv remove <pkg>`        | Cleans environment, updates lockfile |
| Upgrade a package        | `uv add --upgrade <pkg>` | Updates to latest compatible version |
| Update lockfile          | `uv lock`                | Re-resolves all versions             |
| Run a command            | `uv run <cmd>`           | Run in project environment           |
| Check outdated           | `uv pip list --outdated` | See available updates                |

## Common Workflows

### Installing Project Dependencies

```powershell
# Clone repo and install
uv sync
```

### Adding New Dependencies

```powershell
# Add production dependency
uv add requests

# Add with version constraint
uv add "langchain>=0.1.0"

# Add dev dependency
uv add --dev pytest
```

### Upgrading Dependencies

```powershell
# Upgrade specific package
uv add --upgrade langchain-google-genai

# Upgrade all packages (re-lock)
uv lock --upgrade
uv sync
```

### Running Commands

```powershell
# Run Python script
uv run python script.py

# Run pytest
uv run pytest tests/

# Run uvicorn server
uv run uvicorn backend.main:app --reload
```

### Checking for Updates

```powershell
# List outdated packages
uv pip list --outdated

# Or use PyPI JSON API for specific package
# curl https://pypi.org/pypi/<package>/json | jq '.info.version'
```

## Migration from Poetry

If converting from Poetry:

1. Keep `pyproject.toml` - uv uses the same file format
2. Remove `[tool.poetry]` sections, use standard `[project]` format
3. Run `uv lock` to generate `uv.lock` from dependencies
4. Run `uv sync` to install

## Key Benefits

- **Fast**: 10-100x faster than pip/poetry
- **Deterministic**: `uv.lock` ensures reproducible installs
- **Compatible**: Works with standard `pyproject.toml`
- **CI-safe**: Same lockfile = same environment everywhere
