# Migration Guide

This guide documents breaking changes between mxmake versions and how to migrate your projects.

## Version 1.3.1 (unreleased)

### Removed: MXENV_UV_GLOBAL setting

**Breaking Change**: The `MXENV_UV_GLOBAL` setting has been removed. UV is now automatically detected.

**Before (1.3.0 and earlier)**:
```makefile
PYTHON_PACKAGE_INSTALLER?=uv
MXENV_UV_GLOBAL?=true
```

**After (1.3.1+)**:
```makefile
PYTHON_PACKAGE_INSTALLER?=uv
UV_PYTHON?=3.14  # Optional: specify Python version for UV
```

**Migration**:
- Remove the `MXENV_UV_GLOBAL` setting from your Makefile
- If you need a specific Python version with UV, add the `UV_PYTHON` setting
- UV will be auto-detected if installed globally, or installed locally in the virtual environment

## Version 1.0a7

### Renamed: npm domain to nodejs

**Breaking Change**: The `npm` domain was renamed to `nodejs`.

**Before**:
```yaml
topics:
  js:
    npm:
```

**After**:
```yaml
topics:
  js:
    nodejs:
```

**Migration**: Update your `mx.ini` or preseed files to use `nodejs` instead of `npm`.

## Version 1.0a6

### Dropped: Python 3.8 and 3.9 support

**Breaking Change**: Minimum Python version changed from 3.8 to 3.10.

**Migration**:
- Ensure your project uses Python 3.10 or later
- Update `PYTHON_MIN_VERSION` setting if needed:
  ```makefile
  PYTHON_MIN_VERSION?=3.10
  ```

## Version 1.0a4

### Changed: Default venv folder

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
- If you want to keep using `venv`, explicitly set `VENV_FOLDER=venv` in your Makefile
- Or switch to `.venv` and update your `.gitignore` if needed

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

**Migration**: Update your Makefile to use `PRIMARY_PYTHON` instead of `PYTHON_BIN`.

### Removed: MXENV_PATH

**Breaking Change**: `MXENV_PATH` has been removed. Use `$(MXENV_PYTHON)` directly.

**Migration**: If you have custom targets using `MXENV_PATH`, replace:
- `$(MXENV_PATH)pip` → `$(MXENV_PYTHON) -m pip`
- `$(MXENV_PATH)pytest` → `$(MXENV_PYTHON) -m pytest`

## Version 1.0a1

### Changed: Terminology (Semantic overhaul)

**Breaking Change**: Terminology changes in custom domain development:
- "Domains" are now called "Topics"
- "Makefile" is now called "Domain"

**Migration**:
- This only affects custom domain development and plugin authoring
- Update your documentation and code comments accordingly
- The user-facing API remains the same

### Renamed: _SENTINEL to _TARGET in domains

**Breaking Change**: Internal variable naming in custom domains.

**Migration**:
- This only affects custom domain development
- If you wrote custom domains, rename `*_SENTINEL` variables to `*_TARGET`
- Example: `MYDOM_SENTINEL` → `MYDOM_TARGET`
