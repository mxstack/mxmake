#:[mxenv]
#:title = MX Environment
#:description = Python environment management.
#:depends = core.base
#:
#:[target.mxenv]
#:description = Setup the Python environment.
#:  Creates a Python virtual environment using the built-in `venv` module if
#:  `VENV_CREATE` is `true`. The following Python packages are installed
#:  respective updated:
#:    - pip
#:    - setuptools
#:    - wheel
#:    - mxdev
#:    - mxmake
#:
#:[target.mxenv-dirty]
#:description = Build `mxenv` target on next make run.
#:
#:[target.mxenv-clean]
#:description = Removes virtual environment if `VENV_CREATE` is `true`,
#:  otherwise uninstall environment related python packages.
#:
#:[setting.PRIMARY_PYTHON]
#:description = Primary Python interpreter to use. It is used to create the
#:  virtual environment if `VENV_ENABLED` and `VENV_CREATE` are set to `true`.
#:  If global `uv` is used, this value is passed as `--python VALUE` to the venv creation.
#:  uv then downloads the Python interpreter if it is not available.
#:  for more on this feature read the [uv python documentation](https://docs.astral.sh/uv/concepts/python-versions/)
#:default = python3
#:
#:[setting.PYTHON_MIN_VERSION]
#:description = Minimum required Python version.
#:default = 3.9
#:
#:[setting.PYTHON_PACKAGE_INSTALLER]
#:description = Install packages using the given package installer method.
#:  Supported are `pip` and `uv`. When `uv` is selected, a global installation
#:  is auto-detected and used if available. Otherwise, uv is installed in the
#:  virtual environment or using `PRIMARY_PYTHON`, depending on the
#:  `VENV_ENABLED` setting.
#:default = pip
#:
#:[setting.UV_PYTHON]
#:description = Python version for UV to install/use when creating virtual
#:  environments with global UV. Passed to `uv venv -p VALUE`. Supports version
#:  specs like `3.11`, `3.14`, `cpython@3.14`. Defaults to PRIMARY_PYTHON value
#:  for backward compatibility.
#:default = $(PRIMARY_PYTHON)
#:
#:[setting.VENV_ENABLED]
#:description = Flag whether to use virtual environment. If `false`, the
#: interpreter according to `PRIMARY_PYTHON` found in `PATH` is used.
#:default = true
#:
#:[setting.VENV_CREATE]
#:description = Flag whether to create a virtual environment. If set to `false`
#:  and `VENV_ENABLED` is `true`, `VENV_FOLDER` is expected to point to an
#:  existing virtual environment.
#:default = true
#:
#:[setting.VENV_FOLDER]
#:description = The folder of the virtual environment.
#:  If `VENV_ENABLED` is `true` and `VENV_CREATE` is true it is used as the
#:  target folder for the virtual environment. If `VENV_ENABLED` is `true` and
#:  `VENV_CREATE` is false it is expected to point to an existing virtual
#:  environment. If `VENV_ENABLED` is `false` it is ignored.
#:default = .venv
#:
#:[setting.MXDEV]
#:description = mxdev to install in virtual environment.
#:default = mxdev
#:
#:[setting.MXMAKE]
#:description = mxmake to install in virtual environment.
#:default = mxmake

##############################################################################
# mxenv
##############################################################################

OS?=

# Determine the executable path
ifeq ("$(VENV_ENABLED)", "true")
export VIRTUAL_ENV=$(abspath $(VENV_FOLDER))
ifeq ("$(OS)", "Windows_NT")
VENV_EXECUTABLE_FOLDER=$(VIRTUAL_ENV)/Scripts
else
VENV_EXECUTABLE_FOLDER=$(VIRTUAL_ENV)/bin
endif
export PATH:=$(VENV_EXECUTABLE_FOLDER):$(PATH)
MXENV_PYTHON=python
else
MXENV_PYTHON=$(PRIMARY_PYTHON)
endif

# Determine the package installer with non-interactive flags
ifeq ("$(PYTHON_PACKAGE_INSTALLER)","uv")
PYTHON_PACKAGE_COMMAND=uv pip --no-progress
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
# depending on the PYTHON_PACKAGE_INSTALLER and UV_AVAILABLE
# - both vars can be false or
# - one of them can be true,
# - but never boths.
USE_GLOBAL_UV:=$(shell [[ "$(PYTHON_PACKAGE_INSTALLER)" == "uv" && "$(UV_AVAILABLE)" == "true" ]] && echo "true" || echo "false")
USE_LOCAL_UV:=$(shell [[ "$(PYTHON_PACKAGE_INSTALLER)" == "uv" && "$(UV_AVAILABLE)" == "false" ]] && echo "true" || echo "false")

# Check if global UV is outdated (non-blocking warning)
ifeq ("$(USE_GLOBAL_UV)","true")
UV_OUTDATED:=$(shell uv self update --dry-run 2>&1 | grep -q "Would update" && echo "true" || echo "false")
else
UV_OUTDATED:=false
endif

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
	@uv venv --allow-existing --no-progress -p $(UV_PYTHON) --seed $(VENV_FOLDER)
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

.PHONY: mxenv
mxenv: $(MXENV_TARGET)

.PHONY: mxenv-dirty
mxenv-dirty:
	@rm -f $(MXENV_TARGET)

.PHONY: mxenv-clean
mxenv-clean: mxenv-dirty
ifeq ("$(VENV_ENABLED)", "true")
ifeq ("$(VENV_CREATE)", "true")
	@rm -rf $(VENV_FOLDER)
endif
else
	@$(PYTHON_PACKAGE_COMMAND) uninstall -y $(MXDEV)
	@$(PYTHON_PACKAGE_COMMAND) uninstall -y $(MXMAKE)
endif

INSTALL_TARGETS+=mxenv
DIRTY_TARGETS+=mxenv-dirty
CLEAN_TARGETS+=mxenv-clean
