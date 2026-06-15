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

ZPRETTY_TARGET:=$(SENTINEL_FOLDER)/zpretty.sentinel
$(ZPRETTY_TARGET): $(MXENV_TARGET)
	@echo "Install zpretty"
	@$(call INSTALL_TOOL,zpretty)
	@touch $(ZPRETTY_TARGET)

.PHONY: zpretty-check
zpretty-check: $(ZPRETTY_TARGET)
	@echo "Run zpretty check in: $(ZPRETTY_SRC)"
	@find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec $(call RUN_TOOL,zpretty,,--check {}) +

.PHONY: zpretty-format
zpretty-format: $(ZPRETTY_TARGET)
	@echo "Run zpretty format in: $(ZPRETTY_SRC)"
	@find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec $(call RUN_TOOL,zpretty,,-i {}) +

.PHONY: zpretty-dirty
zpretty-dirty:
	@rm -f $(ZPRETTY_TARGET)

.PHONY: zpretty-clean
zpretty-clean: zpretty-dirty
	@$(call UNINSTALL_TOOL,zpretty)

INSTALL_TARGETS+=$(ZPRETTY_TARGET)
CHECK_TARGETS+=zpretty-check
FORMAT_TARGETS+=zpretty-format
DIRTY_TARGETS+=zpretty-dirty
CLEAN_TARGETS+=zpretty-clean
