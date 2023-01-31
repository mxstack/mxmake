#:[black]
#:title = Black
#:description = Code formatting with black.
#:depends = core.packages
#:
#:[target.black]
#:description = Run black.
#:
#:[setting.BLACK_SRC]
#:description = Source folder to scan for Python files to run black on.
#:default = src

##############################################################################
# black
##############################################################################

BLACK_TARGET:=$(SENTINEL_FOLDER)/black.sentinel
$(BLACK_TARGET): $(MXENV_TARGET)
	@echo "Install Black"
	@$(MXENV_PATH)pip install black
	@touch $(BLACK_TARGET)

.PHONY: black-check
black-check: $(PACKAGES_TARGET) $(BLACK_TARGET)
	@echo "Run black checks"
	@$(MXENV_PATH)black --check $(BLACK_SRC)

.PHONY: black-format
black-format: $(PACKAGES_TARGET) $(BLACK_TARGET)
	@echo "Run black format"
	@$(MXENV_PATH)black $(BLACK_SRC)

INSTALL_TARGETS+=$(BLACK_TARGET)
CHECK_TARGETS+=black-check
CHECK_TARGETS+=black-format
