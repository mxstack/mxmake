#:[venv]
#:title = Venv
#:description = Virtual environment management.
#:depends = base
#:
#:target.venv = Create python virtual environment. The following python
#:  packages are installed respective updated:
#:    - pip
#:    - setuptools
#:    - wheel
#:    - mxdev
#:    - mxmake
#:
#:target.venv-dirty = Build :ref:`venv` target on next make run.
#:
#:target.venv-clean = Removes virtual environment.
#:
#:[PYTHON_BIN]
#:description = Python interpreter to use for creating the virtual environment.
#:default = python3
#:
#:[VENV_FOLDER]
#:description = The folder where the virtual environment get created.
#:default = venv
#:
#:[MXDEV]
#:description = mxdev to install in virtual environment
#:default = https://github.com/mxstack/mxdev/archive/remove_libvcs.zip
#:
#:[MXMAKE]
#:description = mxmake to install in virtual environment
#:default = https://github.com/mxstack/mxmake/archive/master.zip

###############################################################################
# venv
###############################################################################

PYTHON_BIN?=python3
VENV_FOLDER?=venv

# This setting is for customizing the installation of mxdev. Normally only
# needed if working on mxdev development.
#MXDEV?=mxdev
MXDEV?=https://github.com/mxstack/mxdev/archive/remove_libvcs.zip

# This setting is for customizing the installation of mxmake. Normally only
# needed if working on mxmake development
#MXMAKE?=mxmake
MXMAKE?=https://github.com/mxstack/mxmake/archive/master.zip

VENV_SENTINEL:=$(SENTINEL_FOLDER)/venv.sentinel
$(VENV_SENTINEL): $(SENTINEL)
	@echo "Setup Python Virtual Environment under '$(VENV_FOLDER)'"
	@$(PYTHON_BIN) -m venv $(VENV_FOLDER)
	@$(VENV_FOLDER)/bin/pip install -U pip setuptools wheel
	@$(VENV_FOLDER)/bin/pip install -U $(MXDEV)
	@$(VENV_FOLDER)/bin/pip install -U $(MXMAKE)
	@touch $(VENV_SENTINEL)

.PHONY: venv
venv: $(VENV_SENTINEL)

.PHONY: venv-dirty
venv-dirty:
	@rm -f $(VENV_SENTINEL)

.PHONY: venv-clean
venv-clean: venv-dirty
	@rm -rf $(VENV_FOLDER)
