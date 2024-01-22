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

ZPRETTY_TARGET:=$(SENTINEL_FOLDER)/zpretty.sentinel
$(ZPRETTY_TARGET): $(MXENV_TARGET)
	@echo "Install zpretty"
	@$(MXENV_PATH)pip install zpretty
	@touch $(ZPRETTY_TARGET)

.PHONY: zpretty-check
zpretty-check: $(ZPRETTY_TARGET)
	@echo "Run zpretty check in: $(ZPRETTY_SRC)"
	@find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec $(MXENV_PATH)zpretty --check {} +

.PHONY: zpretty-format
zpretty-format: $(ZPRETTY_TARGET)
	@echo "Run zpretty format in: $(ZPRETTY_SRC)"
	@find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec $(MXENV_PATH)zpretty -i {} +

.PHONY: zpretty-dirty
zpretty-dirty:
	@rm -f $(ZPRETTY_TARGET)

.PHONY: zpretty-clean
zpretty-clean: zpretty-dirty
	@test -e $(MXENV_PATH)pip && $(MXENV_PATH)pip uninstall -y zpretty || :

INSTALL_TARGETS+=$(ZPRETTY_TARGET)
CHECK_TARGETS+=zpretty-check
FORMAT_TARGETS+=zpretty-format
DIRTY_TARGETS+=zpretty-dirty
CLEAN_TARGETS+=zpretty-clean
