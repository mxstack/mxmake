#:[zpretty]
#:title = zpretty
#:description = Format XML and ZCML with zpretty.
#:depends = core.packages
#:
#:[target.zpretty]
#:description = Run zpretty.
#:
#:[setting.ZPRETTY_SRC]
#:description = Source folder to scan for XML and ZCML files.
#:default = src

##############################################################################
# zpretty
##############################################################################

ZPRETTY_TARGET:=$(SENTINEL_FOLDER)/zpretty.sentinel
$(ZPRETTY_TARGET): $(MXENV_TARGET)
	@echo "Install zpretty"
	@$(MXENV_PATH)pip install zpretty
	@touch $(ZPRETTY_TARGET)

.PHONY: zpretty-check
zpretty-check: $(PACKAGES_TARGET) $(ZPRETTY_TARGET)
	@echo "Run zpretty check"
	@echo "find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec $(MXENV_PATH)zpretty -i {} +""
	@find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec $(MXENV_PATH)zpretty -i {} +
	@$(MXENV_PATH)zpretty --check $(ZPRETTY_SRC)

.PHONY: zpretty-format
zpretty-format: $(PACKAGES_TARGET) $(ZPRETTY_TARGET)
	@echo "Run zpretty format"
	@find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec $(MXENV_PATH)zpretty --check {} +
	@$(MXENV_PATH)zpretty $(ZPRETTY_SRC)

INSTALL_TARGETS+=$(ZPRETTY_TARGET)
CHECK_TARGETS+=zpretty-check
FORMAT_TARGETS+=zpretty-format
