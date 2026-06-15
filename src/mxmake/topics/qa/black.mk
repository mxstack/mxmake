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

BLACK_TARGET:=$(SENTINEL_FOLDER)/black.sentinel
$(BLACK_TARGET): $(MXENV_TARGET)
	@echo "Install Black"
	@$(call INSTALL_TOOL,black)
	@touch $(BLACK_TARGET)

.PHONY: black-check
black-check: $(BLACK_TARGET)
	@echo "Run black checks"
	@$(call RUN_TOOL,black,,--check $(BLACK_SRC))

.PHONY: black-format
black-format: $(BLACK_TARGET)
	@echo "Run black format"
	@$(call RUN_TOOL,black,,$(BLACK_SRC))

.PHONY: black-dirty
black-dirty:
	@rm -f $(BLACK_TARGET)

.PHONY: black-clean
black-clean: black-dirty
	@$(call UNINSTALL_TOOL,black)

INSTALL_TARGETS+=$(BLACK_TARGET)
CHECK_TARGETS+=black-check
FORMAT_TARGETS+=black-format
DIRTY_TARGETS+=black-dirty
CLEAN_TARGETS+=black-clean
