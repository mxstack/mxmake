#:[mxenv-uv]
#:title = MX Environment (uv)
#:description = Provision the Python environment with uv. Default path.
#:depends = core.mxenv
#:soft-depends =
#:  core.mxenv-pip
#:
#:[setting.UV_PYTHON]
#:description = Python version for uv to install/use when creating the virtual
#:  environment. Passed to `uv venv -p VALUE`. Supports specs like `3.11`,
#:  `3.14`, `cpython@3.14`.
#:default = $(PRIMARY_PYTHON)
#:
#:[setting.UV_PROVISION]
#:description = How uv provisions the environment. `pip` (default) installs
#:  mxdev/mxmake with `uv pip install` (works for existing projects). `sync`
#:  uses `uv sync` against pyproject.toml/uv.lock (project-native, new projects).
#:default = pip
#:
#:[setting.TOOL_EXECUTION]
#:description = How style/format QA tools (ruff, isort, ...) are executed.
#:  `uvx` (default) runs them ephemerally without installing into the venv.
#:  `venv` installs them into the environment with `uv pip install`.
#:default = uvx

##############################################################################
# mxenv-uv
##############################################################################

# Internal: identify the active installer for downstream domains.
PYTHON_PACKAGE_INSTALLER:=uv
PYTHON_PACKAGE_COMMAND=uv pip --no-progress

# Tool execution depends on TOOL_EXECUTION.
ifeq ("$(TOOL_EXECUTION)","uvx")
INSTALL_TOOL=:
RUN_TOOL=uvx $(1)$(if $(strip $(2)),==$(strip $(2)),) $(3)
UNINSTALL_TOOL=:
else
INSTALL_TOOL=$(PYTHON_PACKAGE_COMMAND) install $(1)
RUN_TOOL=$(1) $(3)
UNINSTALL_TOOL=uv pip uninstall $(1) || :
endif

$(MXENV_TARGET): $(SENTINEL)
	# Validation: uv must be available
	@command -v uv >/dev/null 2>&1 \
		|| { echo "uv not found. Install uv or switch to core.mxenv-pip."; exit 1; }
	# Validation: VENV_FOLDER set when venv enabled
	@[[ "$(VENV_ENABLED)" == "true" && "$(VENV_FOLDER)" == "" ]] \
		&& echo "VENV_FOLDER must be configured if VENV_ENABLED is true" && exit 1 || :
ifeq ("$(VENV_ENABLED)", "true")
ifeq ("$(VENV_CREATE)", "true")
	@echo "Setup Python Virtual Environment using uv at '$(VENV_FOLDER)'"
	@uv venv --allow-existing --no-progress -p $(UV_PYTHON) --seed $(VENV_FOLDER)
endif
else
	@echo "Using system Python interpreter"
endif
ifeq ("$(UV_PROVISION)","sync")
	@echo "Provision environment with uv sync"
	@uv sync
else
	@$(PYTHON_PACKAGE_COMMAND) install -U pip setuptools wheel
	@echo "Install/Update MXStack Python packages"
	@$(PYTHON_PACKAGE_COMMAND) install -U $(MXDEV) $(MXMAKE)
endif
	@touch $(MXENV_TARGET)
