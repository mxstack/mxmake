#:[black]
#:title = black
#:description = Code formatting with black.
#:depends = core.mxenv
#:
#:[target.black]
#:description = Run black.
#:
#:[setting.BLACK_SRC]
#:description = Source folder to scan for Python files to run black on.
#:default = src
#:
#:[setting.BLACK_VERSION]
#:description = black version to use with uvx (e.g., 24.8.0).
#:  Leave empty for latest. Only used when TOOL_RUNNER=uvx.
#:default =
#:
#:[target.black-dirty]
#:description = Marks black dirty
#:
#:[target.black-clean]
#:description = Uninstall black.

##############################################################################
# black
##############################################################################

# Adjust BLACK_SRC to respect PROJECT_PATH_PYTHON if still at default
ifeq ($(BLACK_SRC),src)
BLACK_SRC:=$(PYTHON_PROJECT_PREFIX)src
endif

# Installation target (only in venv mode)
ifneq ("$(SKIP_TOOL_INSTALL)","true")
BLACK_TARGET:=$(SENTINEL_FOLDER)/black.sentinel
$(BLACK_TARGET): $(MXENV_TARGET)
	@echo "Install Black"
	@$(PYTHON_PACKAGE_COMMAND) install black
	@touch $(BLACK_TARGET)
INSTALL_TARGETS+=$(BLACK_TARGET)
endif

# Conditional dependency
BLACK_DEPENDENCY:=$(if $(filter true,$(SKIP_TOOL_INSTALL)),,$(BLACK_TARGET))

.PHONY: black-check
black-check: $(BLACK_DEPENDENCY)
	@echo "Run black checks"
	@$(call RUN_TOOL,black,$(BLACK_VERSION),--check $(BLACK_SRC))

.PHONY: black-format
black-format: $(BLACK_DEPENDENCY)
	@echo "Run black format"
	@$(call RUN_TOOL,black,$(BLACK_VERSION),$(BLACK_SRC))

.PHONY: black-dirty
black-dirty:
	@rm -f $(BLACK_TARGET)

.PHONY: black-clean
black-clean: black-dirty
ifneq ("$(SKIP_TOOL_INSTALL)","true")
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y black || :
endif
CHECK_TARGETS+=black-check
FORMAT_TARGETS+=black-format
DIRTY_TARGETS+=black-dirty
CLEAN_TARGETS+=black-clean
