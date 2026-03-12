#:[zpretty]
#:title = zpretty
#:description = Format XML and ZCML with zpretty.
#:depends = core.mxenv
#:
#:[target.zpretty]
#:description = Run zpretty.
#:
#:[setting.ZPRETTY_SRC]
#:description = Source folder to scan for XML and ZCML files.
#:default = src
#:
#:[setting.ZPRETTY_VERSION]
#:description = zpretty version to use with uvx (e.g., 3.2.0).
#:  Leave empty for latest. Only used when TOOL_RUNNER=uvx.
#:default =
#:
#:[target.zpretty-dirty]
#:description = Marks zpretty dirty
#:
#:[target.zpretty-clean]
#:description = Uninstall zpretty.

##############################################################################
# zpretty
##############################################################################

# Adjust ZPRETTY_SRC to respect PROJECT_PATH_PYTHON if still at default
ifeq ($(ZPRETTY_SRC),src)
ZPRETTY_SRC:=$(PYTHON_PROJECT_PREFIX)src
endif

# Installation target (only in venv mode)
ifneq ("$(SKIP_TOOL_INSTALL)","true")
ZPRETTY_TARGET:=$(SENTINEL_FOLDER)/zpretty.sentinel
$(ZPRETTY_TARGET): $(MXENV_TARGET)
	@echo "Install zpretty"
	@$(PYTHON_PACKAGE_COMMAND) install zpretty
	@touch $(ZPRETTY_TARGET)
INSTALL_TARGETS+=$(ZPRETTY_TARGET)
endif

# Conditional dependency
ZPRETTY_DEPENDENCY:=$(if $(filter true,$(SKIP_TOOL_INSTALL)),,$(ZPRETTY_TARGET))

# Build zpretty command based on mode
ifeq ("$(SKIP_TOOL_INSTALL)","true")
ZPRETTY_CMD:=uvx zpretty$(if $(strip $(ZPRETTY_VERSION)),==$(strip $(ZPRETTY_VERSION)),)
else
ZPRETTY_CMD:=zpretty
endif

.PHONY: zpretty-check
zpretty-check: $(ZPRETTY_DEPENDENCY)
	@echo "Run zpretty check in: $(ZPRETTY_SRC)"
	@find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec $(ZPRETTY_CMD) --check {} +

.PHONY: zpretty-format
zpretty-format: $(ZPRETTY_DEPENDENCY)
	@echo "Run zpretty format in: $(ZPRETTY_SRC)"
	@find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec $(ZPRETTY_CMD) -i {} +

.PHONY: zpretty-dirty
zpretty-dirty:
	@rm -f $(ZPRETTY_TARGET)

.PHONY: zpretty-clean
zpretty-clean: zpretty-dirty
ifneq ("$(SKIP_TOOL_INSTALL)","true")
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y zpretty || :
endif
CHECK_TARGETS+=zpretty-check
FORMAT_TARGETS+=zpretty-format
DIRTY_TARGETS+=zpretty-dirty
CLEAN_TARGETS+=zpretty-clean
