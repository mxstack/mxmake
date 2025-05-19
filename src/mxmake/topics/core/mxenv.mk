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
#:default = python3
#:
#:[setting.PYTHON_MIN_VERSION]
#:description = Minimum required Python version.
#:default = 3.9
#:
#:[setting.PYTHON_PACKAGE_INSTALLER]
#:description = Install packages using the given package installer method.
#:  Supported are `pip` and `uv`. If uv is used, its global availability is
#:  checked. Otherwise, it is installed, either in the virtual environment or
#:  using the `PRIMARY_PYTHON`, dependent on the `VENV_ENABLED` setting. If
#:  `VENV_ENABLED` and uv is selected, uv is used to create the virtual
#:  environment.
#:default = pip
#:
#:[setting.MXENV_UV_GLOBAL]
#:description = Flag whether to use a global installed 'uv' or install
#:  it in the virtual environment.
#:default = false
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

# Determine the package installer
ifeq ("$(PYTHON_PACKAGE_INSTALLER)","uv")
PYTHON_PACKAGE_COMMAND=uv pip
else
PYTHON_PACKAGE_COMMAND=$(MXENV_PYTHON) -m pip
endif

MXENV_TARGET:=$(SENTINEL_FOLDER)/mxenv.sentinel
$(MXENV_TARGET): $(SENTINEL)
	@$(PRIMARY_PYTHON) -c "import sys; vi = sys.version_info; sys.exit(1 if (int(vi[0]), int(vi[1])) >= tuple(map(int, '$(PYTHON_MIN_VERSION)'.split('.'))) else 0)" \
		&& echo "Need Python >= $(PYTHON_MIN_VERSION)" && exit 1 || :
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
