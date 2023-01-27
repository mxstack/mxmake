#:[venv]
#:title = Venv
#:description = Virtual environment management.
#:depends = core.base
#:
#:[target.venv]
#:description = Create python virtual environment. The following python
#:  packages are installed respective updated:
#:    - pip
#:    - setuptools
#:    - wheel
#:    - mxdev
#:    - mxmake
#:
#:[target.venv-dirty]
#:description = Build :ref:`venv` target on next make run.
#:
#:[target.venv-clean]
#:description = Removes virtual environment.
#:
#:[setting.PYTHON_BIN]
#:description = Python interpreter to use for creating the virtual environment.
#:default = python3
#:
#:[setting.PYTHON_MIN_VERSION]
#:description = Minimum required Python version.
#:default = 3.7
#:
#:[setting.VENV_CREATE]
#:description = Whether to use a VENV or not; "true" or "false".
#:default = true
#:
#:[setting.VENV_FOLDER]
#:description = The folder where the virtual environment get created.
#:default = venv
#:
#:[setting.MXDEV]
#:description = mxdev to install in virtual environment.
#:default = https://github.com/mxstack/mxdev/archive/main.zip
#:
#:[setting.MXMAKE]
#:description = mxmake to install in virtual environment.
#:default = https://github.com/mxstack/mxmake/archive/develop.zip

##############################################################################
# venv
##############################################################################

VENV_SCRIPTS=

# determine the VENV
ifeq ("${VENV_CREATE}", "true")
	VENV_SCRIPTS=${VENV_FOLDER}/bin/
else
# given we have an existing venv folder, we use it, otherwise expect scripts
# in system PATH.
	ifneq ("${VENV_FOLDER}", "")
		VENV_SCRIPTS=${VENV_FOLDER}/bin/
	endif
endif

# Check if given Python is installed?
ifeq (, $(shell which $(PYTHON_BIN) ))
  $(error "PYTHON=$(PYTHON_BIN) not found in $(PATH)")
endif

# Check if given Python version is ok?
PYTHON_VERSION_OK=$(shell $(PYTHON_BIN) -c "import sys; print((int(sys.version_info[0]), int(sys.version_info[1])) >= tuple(map(int, '$(PYTHON_MIN_VERSION)'.split('.'))))")
ifeq ($(PYTHON_VERSION_OK),0)
  $(error "Need Python >= $(PYTHON_MIN_VERSION)")
endif

VENV_SENTINEL:=$(SENTINEL_FOLDER)/venv.sentinel
$(VENV_SENTINEL): $(SENTINEL)
	@echo "Setup Python Virtual Environment under '$(VENV_FOLDER)'"
	@$(PYTHON_BIN) -m venv $(VENV_FOLDER)
	@$(VENV_SCRIPTS)pip install -U pip setuptools wheel
	@$(VENV_SCRIPTS)pip install -U $(MXDEV)
	@$(VENV_SCRIPTS)pip install -U $(MXMAKE)
	@touch $(VENV_SENTINEL)

.PHONY: venv
venv: $(VENV_SENTINEL)

.PHONY: venv-dirty
venv-dirty:
	@rm -f $(VENV_SENTINEL)

.PHONY: venv-clean
venv-clean: venv-dirty
	@rm -rf $(VENV_FOLDER)
