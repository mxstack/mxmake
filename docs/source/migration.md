# Migration Guide

This guide documents breaking changes between mxmake versions and how to migrate your projects.

## Version 2.0.1 (unreleased)

**No breaking changes**

## Version 2.0.0 (2025-10-24)

### Dropped: Python 3.9 Support

**Breaking Change**: Minimum Python version increased from 3.9 to 3.10.

**Migration**:
- Ensure your system has Python 3.10 or later installed
- If using UV, specify Python 3.10+ in `UV_PYTHON` setting:
  ```makefile
  UV_PYTHON?=3.10  # or 3.11, 3.12, 3.13, 3.14
  ```
- If using pip, ensure `PRIMARY_PYTHON` points to Python 3.10+:
  ```makefile
  PRIMARY_PYTHON?=python3.10
  ```
- Run `mxmake update` to regenerate Makefile with new `PYTHON_MIN_VERSION` default

### Removed: MXENV_UV_GLOBAL Setting

**Breaking Change**: The `MXENV_UV_GLOBAL` setting has been removed. UV is now automatically detected.

**Before (1.x)**:
```makefile
PYTHON_PACKAGE_INSTALLER?=uv
MXENV_UV_GLOBAL?=true
```

**After (2.0+)**:
```makefile
PYTHON_PACKAGE_INSTALLER?=uv
UV_PYTHON?=3.14  # Optional: specify Python version
```

**Migration**:
- Remove `MXENV_UV_GLOBAL` from your Makefile or preseed configurations
- UV will be automatically detected if installed globally
- To force local UV installation, ensure UV is not in your PATH
- Add `UV_PYTHON` setting if you need a specific Python version
- Run `mxmake update` to apply changes

### Changed: SOURCES_TARGET Implementation

**Critical Fix**: `SOURCES_TARGET` incorrectly used mxdev's `-o` (offline) flag instead of `-f` (no fetch).

**Impact**: This affects projects using mxdev with source checkouts. The `-o` flag had a bug (fixed in mxdev 5.0).

**Migration**:
- Update mxdev to version 5.0 or later: `pip install -U mxdev>=5`
- Run `mxmake update` in your project directory to regenerate the Makefile
- The new Makefile will use the correct `-f` flag

### Added: UV_PYTHON Setting

**New Feature**: Introduced `UV_PYTHON` setting for semantic clarity.

**Purpose**:
- `PRIMARY_PYTHON`: System interpreter path (e.g., `python3`, `/usr/bin/python3.11`)
- `UV_PYTHON`: Python version spec for UV (e.g., `3.14`, `cpython@3.14`)

**Migration** (optional but recommended):
```makefile
# Old approach (still works)
PYTHON_PACKAGE_INSTALLER?=uv
PRIMARY_PYTHON?=3.14

# New approach (clearer semantics)
PYTHON_PACKAGE_INSTALLER?=uv
UV_PYTHON?=3.14
```

## Version 1.3.0 (2025-09-03)

**No breaking changes**

## Version 1.2.2 (2025-06-30)

**No breaking changes**

## Version 1.2.1 (2025-06-23)

**No breaking changes**

## Version 1.2.0 (2025-06-04)

**No breaking changes**

## Version 1.1.0 (2025-03-20)

**No breaking changes**

## Version 1.0 (2025-02-11)

**No breaking changes**

## Version 1.0a8 (2024-10-24)

**No breaking changes**

## Version 1.0a7 (2024-10-24)

### Renamed: npm Domain to nodejs

**Breaking Change**: The `npm` domain was renamed to `nodejs` to better reflect its purpose (Node.js tooling, supporting both npm and pnpm).

**Before**:
```yaml
# preseed.yaml or mx.ini
topics:
  js:
    npm:
```

**After**:
```yaml
# preseed.yaml or mx.ini
topics:
  js:
    nodejs:
```

**Migration**:
- Update your preseed files to use `nodejs` instead of `npm`
- Run `mxmake update` or `mxmake init` to regenerate Makefile
- The domain now supports both npm and pnpm package managers

## Version 1.0a6 (2024-08-02)

### Dropped: Python 3.8 Support

**Breaking Change**: Minimum Python version increased from 3.8 to 3.9.

**Migration**:
- Ensure your project uses Python 3.9 or later
- Update `PYTHON_MIN_VERSION` if you've customized it:
  ```makefile
  PYTHON_MIN_VERSION?=3.9
  ```

**Note**: This change was superseded by version 2.0.0 which requires Python 3.10+.

## Version 1.0a5 (2024-06-07)

**No breaking changes**

## Version 1.0a4 (2024-03-12)

### Changed: Default venv Folder

**Breaking Change**: Default virtual environment folder changed from `venv` to `.venv`.

**Before**:
```makefile
VENV_FOLDER?=venv
```

**After**:
```makefile
VENV_FOLDER?=.venv
```

**Migration**:
- **Option 1** (Use new default): Delete old `venv` folder, run `make install` to create `.venv`
- **Option 2** (Keep old folder): Explicitly set `VENV_FOLDER=venv` in your Makefile

**Update .gitignore**:
```gitignore
# Old
venv/

# New
.venv/
```

### Renamed: PYTHON_BIN to PRIMARY_PYTHON

**Breaking Change**: `PYTHON_BIN` setting renamed to `PRIMARY_PYTHON`.

**Before**:
```makefile
PYTHON_BIN?=python3
```

**After**:
```makefile
PRIMARY_PYTHON?=python3
```

**Migration**:
- Run `mxmake update` to regenerate Makefile with new setting name
- If you have custom scripts referencing `PYTHON_BIN`, update them to use `PRIMARY_PYTHON`

### Removed: MXENV_PATH

**Breaking Change**: `MXENV_PATH` variable has been removed. Use `$(MXENV_PYTHON)` directly.

**Before**:
```makefile
$(MXENV_PATH)pip install something
$(MXENV_PATH)pytest tests/
```

**After**:
```makefile
$(MXENV_PYTHON) -m pip install something
$(MXENV_PYTHON) -m pytest tests/
```

**Migration**:
- Search your custom Makefile targets for `MXENV_PATH`
- Replace with `$(MXENV_PYTHON) -m <command>`
- Common replacements:
  - `$(MXENV_PATH)pip` → `$(MXENV_PYTHON) -m pip`
  - `$(MXENV_PATH)pytest` → `$(MXENV_PYTHON) -m pytest`
  - `$(MXENV_PATH)black` → `$(MXENV_PYTHON) -m black`

## Version 1.0a3 (2024-02-06)

**No breaking changes** (added typecheck target, CI config generation, ruff domain)

## Version 1.0a2 (2023-07-07)

**No breaking changes** (fixes and pip.conf support)

## Version 1.0a1 (2023-05-05)

### Semantic Overhaul: Terminology Changes

**Breaking Change**: Major terminology changes in custom domain development.

**Changes**:
- "Domains" are now called "Topics"
- "Makefile" is now called "Domain"
- `_SENTINEL` variables renamed to `_TARGET`
- `.sentinels` folder renamed to `.mxmake-sentinels`

**Impact**: Only affects custom domain/plugin authors, not regular users.

**Migration** (for plugin developers):
- Update custom domain files to use new terminology
- Rename `*_SENTINEL` variables to `*_TARGET`:
  ```makefile
  # Before
  MYDOM_SENTINEL?=.sentinels/mydom

  # After
  MYDOM_TARGET?=.mxmake-sentinels/mydom
  ```

### Renamed: Multiple Domains

**Breaking Changes**: Several domains renamed for clarity.

| Old Name | New Name |
|----------|----------|
| `install` | `packages` |
| `files` | `mxfiles` |
| `venv` | `mxenv` |
| `docs` | `sphinx` |

**Migration**:
- Run `mxmake init` to regenerate Makefile with new domain names
- Update preseed files if using old domain names

## Version 0.1 (2022-05-19)

Initial release - no migration needed.

---

## General Migration Tips

### Before Upgrading

1. **Read Release Notes**: Check [CHANGES.md](https://github.com/mxstack/mxmake/blob/main/CHANGES.md) for your target version
2. **Backup**: Commit your current Makefile to version control
3. **Test**: If possible, test the upgrade in a separate branch

### Upgrade Process

1. **Upgrade mxmake**:
   ```bash
   pip install -U mxmake
   # or with UV:
   uv pip install -U mxmake
   ```

2. **Update Makefile**:
   ```bash
   mxmake update
   ```

3. **Review Changes**: Check the diff to ensure settings are preserved
4. **Test**: Run `make install` and `make test` to verify functionality

### Rolling Back

If you encounter issues:
```bash
git checkout Makefile  # Restore previous version
pip install mxmake==<previous-version>  # Downgrade mxmake
```

### Getting Help

- **Documentation**: https://mxmake.readthedocs.io
- **Issues**: https://github.com/mxstack/mxmake/issues
- **Changelog**: https://github.com/mxstack/mxmake/blob/main/CHANGES.md
