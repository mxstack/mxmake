#:[mxenv]
#:title = MX Environment
#:description = Python environment management base. Requires exactly one
#:  environment variant: core.mxenv-pip or core.mxenv-uv.
#:depends = core.base
#:
#:[target.mxenv]
#:description = Setup the Python environment.
#:  Creates a Python virtual environment using the selected environment variant
#:  if `VENV_CREATE` is `true`. The following Python packages are installed
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
#:  If the uv variant is used, this value is the default for `UV_PYTHON`.
#:  for more on this feature read the [uv python documentation](https://docs.astral.sh/uv/concepts/python-versions/)
#:default = python3
#:
#:[setting.PYTHON_MIN_VERSION]
#:description = Minimum required Python version.
#:default = 3.10
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

##############################################################################
# Environment provisioning interface
##############################################################################

# The selected environment variant (core.mxenv-pip or core.mxenv-uv) provides:
#   - PYTHON_PACKAGE_INSTALLER  (pip|uv)
#   - PYTHON_PACKAGE_COMMAND    (installer command)
#   - the $(MXENV_TARGET) rule  (creates the environment)
#   - INSTALL_TOOL / RUN_TOOL / UNINSTALL_TOOL macro definitions controlling how
#     QA dev tools (ruff, isort, ...) are installed and invoked:
#       INSTALL_TOOL(name)            -> shell command to make the tool available
#       RUN_TOOL(name,version,args)   -> shell command to invoke the tool
#       UNINSTALL_TOOL(name)          -> shell command to remove the tool
MXENV_TARGET:=$(SENTINEL_FOLDER)/mxenv.sentinel

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
