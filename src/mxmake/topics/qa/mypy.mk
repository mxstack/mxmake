#:[mypy]
#:title = mypy
#:description = Static code analysis with mypy.
#:depends = core.packages
#:
#:[target.mypy]
#:description = Run mypy.
#:
#:[setting.MYPY_SRC]
#:description = Source folder for code analysis.
#:default = src
#:
#:[setting.MYPY_REQUIREMENTS]
#:description = Mypy Python requirements to be installed (via pip).
#:  Note: In uvx mode (TOOL_RUNNER=uvx), these are NOT installed.
#:  Set TOOL_RUNNER=venv if you need type stubs.
#:default = types-setuptools
#:
#:[setting.MYPY_VERSION]
#:description = mypy version to use with uvx (e.g., 1.11.0).
#:  Leave empty for latest. Only used when TOOL_RUNNER=uvx.
#:default =
#:
#:[target.mypy-dirty]
#:description = Marks mypy dirty
#:
#:[target.mypy-clean]
#:description = Uninstall mypy and removes cached data.

##############################################################################
# mypy
##############################################################################

# Adjust MYPY_SRC to respect PROJECT_PATH_PYTHON if still at default
ifeq ($(MYPY_SRC),src)
MYPY_SRC:=$(PYTHON_PROJECT_PREFIX)src
endif

# Installation target (only in venv mode)
ifneq ("$(SKIP_TOOL_INSTALL)","true")
MYPY_TARGET:=$(SENTINEL_FOLDER)/mypy.sentinel
$(MYPY_TARGET): $(MXENV_TARGET)
	@echo "Install mypy"
	@$(PYTHON_PACKAGE_COMMAND) install mypy $(MYPY_REQUIREMENTS)
	@touch $(MYPY_TARGET)
INSTALL_TARGETS+=$(MYPY_TARGET)
endif

# Conditional dependency
MYPY_DEPENDENCY:=$(if $(filter true,$(SKIP_TOOL_INSTALL)),,$(MYPY_TARGET))

.PHONY: mypy
mypy: $(PACKAGES_TARGET) $(MYPY_DEPENDENCY)
	@echo "Run mypy"
	@$(call RUN_TOOL,mypy,$(MYPY_VERSION),$(MYPY_SRC))

.PHONY: mypy-dirty
mypy-dirty:
	@rm -f $(MYPY_TARGET)

.PHONY: mypy-clean
mypy-clean: mypy-dirty
ifneq ("$(SKIP_TOOL_INSTALL)","true")
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y mypy || :
endif
	@rm -rf .mypy_cache
TYPECHECK_TARGETS+=mypy
CLEAN_TARGETS+=mypy-clean
DIRTY_TARGETS+=mypy-dirty
