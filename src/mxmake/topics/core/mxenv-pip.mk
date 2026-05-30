#:[mxenv-pip]
#:title = MX Environment (pip)
#:description = Provision the Python environment with pip. Legacy/fallback path.
#:depends = core.mxenv
#:soft-depends =
#:  core.mxenv-uv

##############################################################################
# mxenv-pip
##############################################################################

# Internal: identify the active installer for downstream domains.
PYTHON_PACKAGE_INSTALLER:=pip
PYTHON_PACKAGE_COMMAND=$(MXENV_PYTHON) -m pip

# Tool execution: install into the environment, invoke directly.
INSTALL_TOOL=$(PYTHON_PACKAGE_COMMAND) install $(1)
RUN_TOOL=$(1) $(3)
UNINSTALL_TOOL=test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y $(1) || :

$(MXENV_TARGET): $(SENTINEL)
	# Validation: Python version
	@$(PRIMARY_PYTHON) -c "import sys; vi = sys.version_info; sys.exit(1 if (int(vi[0]), int(vi[1])) >= tuple(map(int, '$(PYTHON_MIN_VERSION)'.split('.'))) else 0)" \
		&& echo "Need Python >= $(PYTHON_MIN_VERSION)" && exit 1 || :
	# Validation: VENV_FOLDER set when venv enabled
	@[[ "$(VENV_ENABLED)" == "true" && "$(VENV_FOLDER)" == "" ]] \
		&& echo "VENV_FOLDER must be configured if VENV_ENABLED is true" && exit 1 || :
ifeq ("$(VENV_ENABLED)", "true")
ifeq ("$(VENV_CREATE)", "true")
	@echo "Setup Python Virtual Environment using module 'venv' at '$(VENV_FOLDER)'"
	@$(PRIMARY_PYTHON) -m venv $(VENV_FOLDER)
	@$(MXENV_PYTHON) -m ensurepip -U
endif
else
	@echo "Using system Python interpreter"
endif
	@$(PYTHON_PACKAGE_COMMAND) install -U pip setuptools wheel
	@echo "Install/Update MXStack Python packages"
	@$(PYTHON_PACKAGE_COMMAND) install -U $(MXDEV) $(MXMAKE)
	@touch $(MXENV_TARGET)
