#:[black]
#:title = Black
#:description = Code formatting with black.
#:depends = core.packages
#:
#:[target.black]
#:description = Run black.
#:
#:[setting.BLACK_SRC]
#:description = Source folder for code formatting.
#:default = src

##############################################################################
# black
##############################################################################

BLACK_TARGET:=$(SENTINEL_FOLDER)/black.sentinel
$(BLACK_TARGET): $(MXENV_TARGET)
	@echo "Install Black"
	@$(MXENV_PATH)pip install black
	@touch $(BLACK_TARGET)

.PHONY: black
black: $(PACKAGES_TARGET) $(BLACK_TARGET)
	@echo "Run black"
	@$(MXENV_PATH)black $(BLACK_SRC)

INSTALL_TARGETS+=$(BLACK_TARGET)
