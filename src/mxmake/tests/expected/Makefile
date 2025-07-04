##############################################################################
# THIS FILE IS GENERATED BY MXMAKE
#
# DOMAINS:
#: core.base
#: core.mxenv
#
# SETTINGS (ALL CHANGES MADE BELOW SETTINGS WILL BE LOST)
##############################################################################

## core.base

# `deploy` target dependencies.
# No default value.
DEPLOY_TARGETS?=

# target to be executed when calling `make run`
# No default value.
RUN_TARGET?=

# Additional files and folders to remove when running clean target
# No default value.
CLEAN_FS?=

# Optional makefile to include before default targets. This can
# be used to provide custom targets or hook up to existing targets.
# Default: include.mk
INCLUDE_MAKEFILE?=include.mk

# Optional additional directories to be added to PATH in format
# `/path/to/dir/:/path/to/other/dir`. Gets inserted first, thus gets searched
# first.
# No default value.
EXTRA_PATH?=

## core.mxenv

# Primary Python interpreter to use. It is used to create the
# virtual environment if `VENV_ENABLED` and `VENV_CREATE` are set to `true`.
# If global `uv` is used, this value is passed as `--python VALUE` to the venv creation.
# uv then downloads the Python interpreter if it is not available.
# for more on this feature read the [uv python documentation](https://docs.astral.sh/uv/concepts/python-versions/)
# Default: python3
PRIMARY_PYTHON?=python3

# Minimum required Python version.
# Default: 3.9
PYTHON_MIN_VERSION?=3.9

# Install packages using the given package installer method.
# Supported are `pip` and `uv`. If uv is used, its global availability is
# checked. Otherwise, it is installed, either in the virtual environment or
# using the `PRIMARY_PYTHON`, dependent on the `VENV_ENABLED` setting. If
# `VENV_ENABLED` and uv is selected, uv is used to create the virtual
# environment.
# Default: pip
PYTHON_PACKAGE_INSTALLER?=pip

# Flag whether to use a global installed 'uv' or install
# it in the virtual environment.
# Default: false
MXENV_UV_GLOBAL?=false

# Flag whether to use virtual environment. If `false`, the
# interpreter according to `PRIMARY_PYTHON` found in `PATH` is used.
# Default: true
VENV_ENABLED?=true

# Flag whether to create a virtual environment. If set to `false`
# and `VENV_ENABLED` is `true`, `VENV_FOLDER` is expected to point to an
# existing virtual environment.
# Default: true
VENV_CREATE?=true

# The folder of the virtual environment.
# If `VENV_ENABLED` is `true` and `VENV_CREATE` is true it is used as the
# target folder for the virtual environment. If `VENV_ENABLED` is `true` and
# `VENV_CREATE` is false it is expected to point to an existing virtual
# environment. If `VENV_ENABLED` is `false` it is ignored.
# Default: .venv
VENV_FOLDER?=.venv

# mxdev to install in virtual environment.
# Default: mxdev
MXDEV?=mxdev

# mxmake to install in virtual environment.
# Default: mxmake
MXMAKE?=mxmake

##############################################################################
# END SETTINGS - DO NOT EDIT BELOW THIS LINE
##############################################################################

INSTALL_TARGETS?=
DIRTY_TARGETS?=
CLEAN_TARGETS?=
PURGE_TARGETS?=

export PATH:=$(if $(EXTRA_PATH),$(EXTRA_PATH):,)$(PATH)

# Defensive settings for make: https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
# for Makefile debugging purposes add -x to the .SHELLFLAGS
.SHELLFLAGS:=-eu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# mxmake folder
MXMAKE_FOLDER?=.mxmake

# Sentinel files
SENTINEL_FOLDER?=$(MXMAKE_FOLDER)/sentinels
SENTINEL?=$(SENTINEL_FOLDER)/about.txt
$(SENTINEL): $(firstword $(MAKEFILE_LIST))
	@mkdir -p $(SENTINEL_FOLDER)
	@echo "Sentinels for the Makefile process." > $(SENTINEL)

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

# Determine the package installer
ifeq ("$(PYTHON_PACKAGE_INSTALLER)","uv")
PYTHON_PACKAGE_COMMAND=uv pip
else
PYTHON_PACKAGE_COMMAND=$(MXENV_PYTHON) -m pip
endif

MXENV_TARGET:=$(SENTINEL_FOLDER)/mxenv.sentinel
$(MXENV_TARGET): $(SENTINEL)
ifneq ("$(PYTHON_PACKAGE_INSTALLER)$(MXENV_UV_GLOBAL)","uvfalse")
	@$(PRIMARY_PYTHON) -c "import sys; vi = sys.version_info; sys.exit(1 if (int(vi[0]), int(vi[1])) >= tuple(map(int, '$(PYTHON_MIN_VERSION)'.split('.'))) else 0)" \
		&& echo "Need Python >= $(PYTHON_MIN_VERSION)" && exit 1 || :
else
	@echo "Use Python $(PYTHON_MIN_VERSION) over uv"
endif
	@[[ "$(VENV_ENABLED)" == "true" && "$(VENV_FOLDER)" == "" ]] \
		&& echo "VENV_FOLDER must be configured if VENV_ENABLED is true" && exit 1 || :
	@[[ "$(VENV_ENABLED)$(PYTHON_PACKAGE_INSTALLER)" == "falseuv" ]] \
		&& echo "Package installer uv does not work with a global Python interpreter." && exit 1 || :
ifeq ("$(VENV_ENABLED)", "true")
ifeq ("$(VENV_CREATE)", "true")
ifeq ("$(PYTHON_PACKAGE_INSTALLER)$(MXENV_UV_GLOBAL)","uvtrue")
	@echo "Setup Python Virtual Environment using package 'uv' at '$(VENV_FOLDER)'"
	@uv venv -p $(PRIMARY_PYTHON) --seed $(VENV_FOLDER)
else
	@echo "Setup Python Virtual Environment using module 'venv' at '$(VENV_FOLDER)'"
	@$(PRIMARY_PYTHON) -m venv $(VENV_FOLDER)
	@$(MXENV_PYTHON) -m ensurepip -U
endif
endif
else
	@echo "Using system Python interpreter"
endif
ifeq ("$(PYTHON_PACKAGE_INSTALLER)$(MXENV_UV_GLOBAL)","uvfalse")
	@echo "Install uv"
	@$(MXENV_PYTHON) -m pip install uv
endif
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

##############################################################################
# Custom includes
##############################################################################

-include $(INCLUDE_MAKEFILE)

##############################################################################
# Default targets
##############################################################################

INSTALL_TARGET:=$(SENTINEL_FOLDER)/install.sentinel
$(INSTALL_TARGET): $(INSTALL_TARGETS)
	@touch $(INSTALL_TARGET)

.PHONY: install
install: $(INSTALL_TARGET)
	@touch $(INSTALL_TARGET)

.PHONY: run
run: $(RUN_TARGET)

.PHONY: deploy
deploy: $(DEPLOY_TARGETS)

.PHONY: dirty
dirty: $(DIRTY_TARGETS)
	@rm -f $(INSTALL_TARGET)

.PHONY: clean
clean: dirty $(CLEAN_TARGETS)
	@rm -rf $(CLEAN_TARGETS) $(MXMAKE_FOLDER) $(CLEAN_FS)

.PHONY: purge
purge: clean $(PURGE_TARGETS)

.PHONY: runtime-clean
runtime-clean:
	@echo "Remove runtime artifacts, like byte-code and caches."
	@find . -name '*.py[c|o]' -delete
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

