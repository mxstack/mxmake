#:[mxenv]
#:title = MX Environment
#:description = Python environment management.
#:depends = core.base
#:
#:[target.mxenv]
#:description = Setup the Python environment.
#: Creates a Python virtual environment using the built-in `venv` module if
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
#:[setting.PYTHON_BIN]
#:description = Python interpreter to use.
#:default = python3
#:
#:[setting.PYTHON_MIN_VERSION]
#:description = Minimum required Python version.
#:default = 3.7
#:
#:[setting.VENV_ENABLED]
#:description = Flag whether to use virtual environment. If `false`, the
#:  interpreter according to `PYTHON_BIN` found in `PATH` is used.
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
#:default = venv
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

# Check if given Python is installed
ifeq (,$(shell which $(PYTHON_BIN)))
$(error "PYTHON=$(PYTHON_BIN) not found in $(PATH)")
endif

# Check if given Python version is ok
PYTHON_VERSION_OK=$(shell $(PYTHON_BIN) -c "import sys; print((int(sys.version_info[0]), int(sys.version_info[1])) >= tuple(map(int, '$(PYTHON_MIN_VERSION)'.split('.'))))")
ifeq ($(PYTHON_VERSION_OK),0)
$(error "Need Python >= $(PYTHON_MIN_VERSION)")
endif

# Check if venv folder is configured if venv is enabled
ifeq ($(shell [[ "$(VENV_ENABLED)" == "true" && "$(VENV_FOLDER)" == "" ]] && echo "true"),"true")
$(error "VENV_FOLDER must be configured if VENV_ENABLED is true")
endif

# determine the executable path
ifeq ("$(VENV_ENABLED)", "true")
MXENV_PATH=$(VENV_FOLDER)/bin/
else
MXENV_PATH=
endif

MXENV_TARGET:=$(SENTINEL_FOLDER)/mxenv.sentinel
$(MXENV_TARGET): $(SENTINEL)
ifeq ("$(VENV_ENABLED)", "true")
ifeq ("$(VENV_CREATE)", "true")
	@echo "Setup Python Virtual Environment under '$(VENV_FOLDER)'"
	@$(PYTHON_BIN) -m venv $(VENV_FOLDER)
endif
endif
	@$(MXENV_PATH)pip install -U pip setuptools wheel
	@$(MXENV_PATH)pip install -U $(MXDEV)
	@$(MXENV_PATH)pip install -U $(MXMAKE)
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
	@$(MXENV_PATH)pip uninstall -y $(MXDEV)
	@$(MXENV_PATH)pip uninstall -y $(MXMAKE)
endif

INSTALL_TARGETS+=mxenv
DIRTY_TARGETS+=mxenv-dirty
CLEAN_TARGETS+=mxenv-clean
