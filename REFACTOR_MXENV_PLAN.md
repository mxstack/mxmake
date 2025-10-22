# Refactor mxenv.mk: Auto-Detect UV and Simplify Logic

**Issue**: https://github.com/mxstack/mxmake/issues/43
**Current File**: [src/mxmake/topics/core/mxenv.mk](src/mxmake/topics/core/mxenv.mk)

## Problem Statement

The current `mxenv.mk` implementation has become overly complex:

1. **Deeply nested conditionals** (3+ levels in places)
2. **Hard-to-read string concatenation checks** like `"$(PYTHON_PACKAGE_INSTALLER)$(MXENV_UV_GLOBAL)","uvtrue"`
3. **Scattered logic** mixing validation, venv creation, and package installation
4. **Manual `MXENV_UV_GLOBAL` setting** instead of auto-detection

This makes it difficult to understand, maintain, and extend with new features like UV auto-detection.

## Goals

1. **Auto-detect** global `uv` availability instead of requiring manual `MXENV_UV_GLOBAL` setting
2. **Reduce complexity** and nesting of conditionals
3. **Maintain all existing functionality** without breaking changes to behavior
4. **Make future changes easier** by establishing clearer patterns

## Proposed Changes

### 1. Replace `MXENV_UV_GLOBAL` Setting with Auto-Detection

**Location**: Lines 45-48 (domain metadata)

**Remove**:
```makefile
#:[setting.MXENV_UV_GLOBAL]
#:description = Flag whether to use a global installed 'uv' or install
#:  it in the virtual environment.
#:default = false
```

**Add**:
```makefile
#:[setting.UV_PYTHON]
#:description = Python version for UV to install/use when creating virtual
#:  environments with global UV. Passed to `uv venv -p VALUE`. Supports version
#:  specs like `3.11`, `3.14`, `cpython@3.14`. Defaults to PRIMARY_PYTHON value
#:  for backward compatibility.
#:default =
```

**Rationale for UV_PYTHON**:
- Provides semantic clarity: `PRIMARY_PYTHON` = system interpreter path, `UV_PYTHON` = UV version spec
- Backward compatible: defaults to `PRIMARY_PYTHON` if not set
- Supports UV's Python management features properly

**Update** `PYTHON_PACKAGE_INSTALLER` description to mention auto-detection:
```makefile
#:[setting.PYTHON_PACKAGE_INSTALLER]
#:description = Install packages using the given package installer method.
#:  Supported are `pip` and `uv`. When `uv` is selected, a global installation
#:  is auto-detected and used if available and meets the minimum version
#:  requirement. Otherwise, uv is installed in the virtual environment or
#:  using `PRIMARY_PYTHON`, depending on the `VENV_ENABLED` setting.
#:default = pip
```

### 2. Add UV Detection and Configuration Logic

**Location**: After line 102 (after PYTHON_PACKAGE_COMMAND determination)

**Add new section**:
```makefile
# Determine the package installer with non-interactive flags
ifeq ("$(PYTHON_PACKAGE_INSTALLER)","uv")
PYTHON_PACKAGE_COMMAND=uv pip --quiet --no-progress
else
PYTHON_PACKAGE_COMMAND=$(MXENV_PYTHON) -m pip
endif

# Auto-detect global uv availability (simple existence check)
ifeq ("$(PYTHON_PACKAGE_INSTALLER)","uv")
UV_AVAILABLE:=$(shell command -v uv >/dev/null 2>&1 && echo "true" || echo "false")
else
UV_AVAILABLE:=false
endif

# Determine installation strategy
USE_GLOBAL_UV:=$(shell [[ "$(PYTHON_PACKAGE_INSTALLER)" == "uv" && "$(UV_AVAILABLE)" == "true" ]] && echo "true" || echo "false")
USE_LOCAL_UV:=$(shell [[ "$(PYTHON_PACKAGE_INSTALLER)" == "uv" && "$(UV_AVAILABLE)" == "false" ]] && echo "true" || echo "false")

# UV Python version (defaults to PRIMARY_PYTHON for backward compatibility)
UV_PYTHON?=$(PRIMARY_PYTHON)

# Check if global UV is outdated (non-blocking warning)
ifeq ("$(USE_GLOBAL_UV)","true")
UV_OUTDATED:=$(shell uv self update --dry-run 2>&1 | grep -q "Would update" && echo "true" || echo "false")
else
UV_OUTDATED:=false
endif
```

**Rationale**:
- **Pure shell detection**: No Python dependency during Python setup
- **Non-interactive UV**: `--quiet --no-progress` flags ensure CI/CD compatibility
- **Semantic clarity**: `UV_PYTHON` separates system Python path from UV version spec
- **Simple and reliable**: Just checks if `uv` command exists in PATH
- **Backward compatible**: `UV_PYTHON` defaults to `PRIMARY_PYTHON`
- **Update awareness**: Warns if global UV is outdated using `uv self update --dry-run`

**Note on UV updates**: Instead of checking minimum versions, we use `uv self update --dry-run`
to detect if updates are available. This leverages UV's built-in update mechanism and provides
helpful warnings without blocking execution.

### 3. Simplify Main Target Logic

**Location**: Lines 104-137 ($(MXENV_TARGET) recipe)

**Current structure** (complex):
- Multiple nested `ifeq` statements
- Validation mixed with execution
- Hard to follow control flow

**New structure** (simplified):

```makefile
MXENV_TARGET:=$(SENTINEL_FOLDER)/mxenv.sentinel
$(MXENV_TARGET): $(SENTINEL)
	# Validation: Check Python version if not using global uv
ifneq ("$(USE_GLOBAL_UV)","true")
	@$(PRIMARY_PYTHON) -c "import sys; vi = sys.version_info; sys.exit(1 if (int(vi[0]), int(vi[1])) >= tuple(map(int, '$(PYTHON_MIN_VERSION)'.split('.'))) else 0)" \
		&& echo "Need Python >= $(PYTHON_MIN_VERSION)" && exit 1 || :
else
	@echo "Using global uv for Python $(UV_PYTHON)"
endif
	# Validation: Check VENV_FOLDER is set if venv enabled
	@[[ "$(VENV_ENABLED)" == "true" && "$(VENV_FOLDER)" == "" ]] \
		&& echo "VENV_FOLDER must be configured if VENV_ENABLED is true" && exit 1 || :
	# Validation: Check uv not used with system Python
	@[[ "$(VENV_ENABLED)" == "false" && "$(PYTHON_PACKAGE_INSTALLER)" == "uv" ]] \
		&& echo "Package installer uv does not work with a global Python interpreter." && exit 1 || :
	# Warning: Notify if global UV is outdated
ifeq ("$(UV_OUTDATED)","true")
	@echo "WARNING: A newer version of uv is available. Run 'uv self update' to upgrade."
endif

	# Create virtual environment
ifeq ("$(VENV_ENABLED)", "true")
ifeq ("$(VENV_CREATE)", "true")
ifeq ("$(USE_GLOBAL_UV)","true")
	@echo "Setup Python Virtual Environment using global uv at '$(VENV_FOLDER)'"
	@uv venv --quiet --no-progress -p $(UV_PYTHON) --seed $(VENV_FOLDER)
else
	@echo "Setup Python Virtual Environment using module 'venv' at '$(VENV_FOLDER)'"
	@$(PRIMARY_PYTHON) -m venv $(VENV_FOLDER)
	@$(MXENV_PYTHON) -m ensurepip -U
endif
endif
else
	@echo "Using system Python interpreter"
endif

	# Install uv locally if needed
ifeq ("$(USE_LOCAL_UV)","true")
	@echo "Install uv in virtual environment"
	@$(MXENV_PYTHON) -m pip install uv
endif

	# Install/upgrade core packages
	@$(PYTHON_PACKAGE_COMMAND) install -U pip setuptools wheel
	@echo "Install/Update MXStack Python packages"
	@$(PYTHON_PACKAGE_COMMAND) install -U $(MXDEV) $(MXMAKE)
	@touch $(MXENV_TARGET)
```

**Key improvements**:
- **All validation at the top** (easier to see preconditions)
- **Single-level conditionals** using computed variables (`USE_GLOBAL_UV`, `USE_LOCAL_UV`)
- **Clear sections**: validation → warnings → venv creation → uv installation → package installation
- **Semantic clarity**: `PRIMARY_PYTHON` (system) vs `UV_PYTHON` (UV version spec)
- **Non-interactive UV**: All UV commands use `--quiet --no-progress` for CI/CD compatibility
- **Update awareness**: Warns users if global UV is outdated (using `uv self update --dry-run`)
- **Removed complex string concatenation checks** like `"$(PYTHON_PACKAGE_INSTALLER)$(MXENV_UV_GLOBAL)","uvtrue"`

### 4. Update Tests and Documentation

**Files to update**:

1. **[src/mxmake/tests/expected/Makefile](src/mxmake/tests/expected/Makefile)**:
   - Remove `MXENV_UV_GLOBAL` setting (lines 58-61)
   - Add `UV_PYTHON` setting if tests need to verify it

2. **[src/mxmake/tests/test_parser.py](src/mxmake/tests/test_parser.py)**:
   - Check if any tests reference `MXENV_UV_GLOBAL` and update them
   - Add tests for `UV_PYTHON` if needed

3. **[src/mxmake/tests/test_templates.py](src/mxmake/tests/test_templates.py)**:
   - Check if any tests set `MXENV_UV_GLOBAL` and update them
   - Add tests for non-interactive UV flags if needed

4. **[CLAUDE.md](CLAUDE.md)**:
   - Update if it mentions `MXENV_UV_GLOBAL`

### 5. Handle Backwards Compatibility

**Parser changes** ([src/mxmake/parser.py](src/mxmake/parser.py)):
- When parsing old Makefiles with `MXENV_UV_GLOBAL`, silently ignore it
- Don't include it in the settings to preserve

**Migration note in CHANGES.md**:
```markdown
### Breaking Changes

- **mxenv domain**: Removed `MXENV_UV_GLOBAL` setting in favor of automatic
  UV detection. When `PYTHON_PACKAGE_INSTALLER=uv`, mxmake now automatically
  detects and uses a globally installed `uv` if available. To force local
  installation of uv, simply don't install it globally or remove it from PATH.

### New Features

- **mxenv domain**: Added `UV_PYTHON` setting to specify Python version for
  UV-managed virtual environments. Defaults to `PRIMARY_PYTHON` for backward
  compatibility. This provides semantic clarity: `PRIMARY_PYTHON` is the system
  interpreter path (e.g., `python3.11`), while `UV_PYTHON` is the version spec
  for UV (e.g., `3.14`, `cpython@3.14`).

- **mxenv domain**: All UV commands now run with `--quiet --no-progress` flags
  for better CI/CD compatibility and cleaner log output.

- **mxenv domain**: When using global UV, mxmake now checks if updates are
  available using `uv self update --dry-run` and displays a helpful warning
  if a newer version is available. This is non-blocking and helps keep UV current.
```

## Implementation Order

1. **Update mxenv.mk** with new logic
2. **Update test fixtures** (expected/Makefile)
3. **Run tests** to verify no breakage
4. **Update documentation** (CHANGES.md, CLAUDE.md if needed)
5. **Test manually** with both global and local uv scenarios
6. **Create PR** with clear migration notes

## Testing Strategy

Test the following scenarios:

1. **Global uv available** (`PYTHON_PACKAGE_INSTALLER=uv`)
   - Should use global uv for venv creation
   - Should not install uv locally

2. **No global uv** (`PYTHON_PACKAGE_INSTALLER=uv`)
   - Should create venv with Python's venv module
   - Should install uv in the virtual environment

3. **Using pip** (`PYTHON_PACKAGE_INSTALLER=pip`)
   - Should work exactly as before
   - Should not check for uv

4. **Force local uv** (`PYTHON_PACKAGE_INSTALLER=uv`)
   - Remove global `uv` from PATH temporarily
   - Should install uv locally in virtual environment

5. **Old Makefile migration**
   - Makefile with `MXENV_UV_GLOBAL=true` should work after `mxmake update`
   - Setting should be removed from updated Makefile

6. **UV_PYTHON with different value than PRIMARY_PYTHON**
   - Set `PRIMARY_PYTHON=python3.11` and `UV_PYTHON=3.14`
   - Should use system Python 3.11 for non-UV venv creation
   - Should use UV to install Python 3.14 when global UV available

7. **CI/Non-TTY environment**
   - Run in non-interactive shell or CI environment
   - UV commands should not output progress bars
   - Logs should be clean without ANSI escape codes

8. **UV update check**
   - With outdated global UV: Should display warning message
   - With current global UV: Should not display warning
   - With local UV: Should not check for updates

## Benefits

### Simplification
- **Reduces nesting**: From 3+ levels to 1-2 levels maximum
- **Clearer flow**: Validation → Creation → Installation is explicit
- **Self-documenting**: Variables like `USE_GLOBAL_UV` explain intent

### Auto-detection
- **No manual configuration**: Users don't need to know about `MXENV_UV_GLOBAL`
- **Smart defaults**: Uses global uv when available
- **Override capability**: Can force local uv by not installing globally
- **Update awareness**: Helpful warnings when global UV is outdated (non-blocking)

### Semantic Clarity
- **UV_PYTHON setting**: Separates system Python path from UV version spec
- **Backward compatible**: Defaults to `PRIMARY_PYTHON` if not set
- **Explicit intent**: Makes it clear when using UV's Python management vs system Python

### CI/CD Friendly
- **Non-interactive**: All UV commands use `--quiet --no-progress`
- **Clean logs**: No progress bars or unnecessary output
- **Reliable**: Works in any environment (TTY or non-TTY)

### Maintainability
- **Easy to extend**: Adding new installers is straightforward
- **Easier debugging**: Clear sections make issues easier to locate
- **Better testing**: Computed variables are easier to test

### Future-proof
- **Plugin architecture ready**: Clear pattern for adding installers
- **Version checking ready**: Framework exists for version requirements
- **Migration path**: Pattern for removing deprecated settings

## Risks and Mitigations

### Risk: Breaking existing workflows
**Mitigation**:
- Thorough testing with various configurations
- Clear migration documentation
- Parser silently handles old settings

### Risk: UV detection false positives/negatives
**Mitigation**:
- Simple, reliable detection (just check if `uv` command exists)
- Override by controlling UV availability in PATH
- Clear error messages when UV is required but unavailable

### Risk: Performance impact of shell commands and network checks
**Mitigation**:
- Detection runs once per make invocation
- Uses efficient shell builtins (`command -v`)
- Cached in Make variables
- UV update check is fast (just metadata check, no download)
- Acceptable trade-off: ~100-200ms for helpful update notifications

**Note**: The `uv self update --dry-run` check makes a network request. In restricted
network environments or offline scenarios, this may add slight delay or fail silently.
This is acceptable as it's a non-blocking warning only.

**Future enhancement**: Cache update check results:
```makefile
# Only check for updates once per day
UV_UPDATE_CHECK_FILE:=$(MXMAKE_FOLDER)/.uv-update-check
UV_OUTDATED:=$(shell \
	if [[ ! -f "$(UV_UPDATE_CHECK_FILE)" ]] || \
	   [[ $$(find "$(UV_UPDATE_CHECK_FILE)" -mtime +1 2>/dev/null) ]]; then \
		uv self update --dry-run 2>&1 | grep -q "Would update" && echo "true" || echo "false"; \
		touch "$(UV_UPDATE_CHECK_FILE)"; \
	else \
		echo "false"; \
	fi)
```

## Decisions Made

1. **Version checking**: ✅ Just check availability, not version
   - Simple and reliable
   - UV is stable enough that version checking is not critical
   - Can be added later if needed

2. **Non-interactive flags**: ✅ Always apply `--quiet --no-progress`
   - Ensures CI/CD compatibility
   - Clean log output
   - No configuration needed

3. **UV_PYTHON setting**: ✅ Add new setting with default to PRIMARY_PYTHON
   - Provides semantic clarity
   - Backward compatible
   - Supports UV's Python management features

4. **Deprecation period**: ✅ Silent removal of `MXENV_UV_GLOBAL`
   - Parser ignores it if found
   - Clear migration notes in CHANGES.md
   - No warning needed

5. **UV update check**: ✅ Warn if global UV is outdated
   - Use `uv self update --dry-run` to detect available updates
   - Non-blocking warning message
   - Only checks when using global UV
   - Helps users keep UV current without enforcing it
   - Future: Can add caching to reduce network calls
