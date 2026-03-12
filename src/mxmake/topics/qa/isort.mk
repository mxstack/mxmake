#:[isort]
#:title = isort
#:description = Import sorting with isort.
#:depends = core.mxenv
#:
#:[target.isort]
#:description = Run isort.
#:
#:[setting.ISORT_SRC]
#:description = Source folder to scan for Python files to run isort on.
#:default = src
#:
#:[setting.ISORT_VERSION]
#:description = isort version to use with uvx (e.g., 5.13.2).
#:  Leave empty for latest. Only used when TOOL_RUNNER=uvx.
#:default =
#:
#:[target.isort-dirty]
#:description = Marks isort dirty
#:
#:[target.isort-clean]
#:description = Uninstall isort.

##############################################################################
# isort
##############################################################################

# Adjust ISORT_SRC to respect PROJECT_PATH_PYTHON if still at default
ifeq ($(ISORT_SRC),src)
ISORT_SRC:=$(PYTHON_PROJECT_PREFIX)src
endif

# Installation target (only in venv mode)
ifneq ("$(SKIP_TOOL_INSTALL)","true")
ISORT_TARGET:=$(SENTINEL_FOLDER)/isort.sentinel
$(ISORT_TARGET): $(MXENV_TARGET)
	@echo "Install isort"
	@$(PYTHON_PACKAGE_COMMAND) install isort
	@touch $(ISORT_TARGET)
INSTALL_TARGETS+=$(ISORT_TARGET)
endif

# Conditional dependency
ISORT_DEPENDENCY:=$(if $(filter true,$(SKIP_TOOL_INSTALL)),,$(ISORT_TARGET))

.PHONY: isort-check
isort-check: $(ISORT_DEPENDENCY)
	@echo "Run isort check"
	@$(call RUN_TOOL,isort,$(ISORT_VERSION),--check $(ISORT_SRC))

.PHONY: isort-format
isort-format: $(ISORT_DEPENDENCY)
	@echo "Run isort format"
	@$(call RUN_TOOL,isort,$(ISORT_VERSION),$(ISORT_SRC))

.PHONY: isort-dirty
isort-dirty:
	@rm -f $(ISORT_TARGET)

.PHONY: isort-clean
isort-clean: isort-dirty
ifneq ("$(SKIP_TOOL_INSTALL)","true")
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y isort || :
endif
CHECK_TARGETS+=isort-check
FORMAT_TARGETS+=isort-format
DIRTY_TARGETS+=isort-dirty
CLEAN_TARGETS+=isort-clean
