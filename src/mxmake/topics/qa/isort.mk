#:[isort]
#:title = isort
#:description = Import sorting with isort.
#:depends = core.packages
#:
#:[target.isort]
#:description = Run isort.
#:
#:[setting.ISORT_SRC]
#:description = Source folder to scan for Python files to run isort on.
#:default = src

##############################################################################
# isort
##############################################################################

ISORT_TARGET:=$(SENTINEL_FOLDER)/isort.sentinel
$(ISORT_TARGET): $(MXENV_TARGET)
	@echo "Install isort"
	@$(MXENV_PATH)pip install isort
	@touch $(ISORT_TARGET)

.PHONY: isort-check
isort-check: $(PACKAGES_TARGET) $(ISORT_TARGET)
	@echo "Run isort check"
	@$(MXENV_PATH)isort --check $(ISORT_SRC)

.PHONY: isort-format
isort-format: $(PACKAGES_TARGET) $(ISORT_TARGET)
	@echo "Run isort format"
	@$(MXENV_PATH)isort $(ISORT_SRC)

INSTALL_TARGETS+=$(ISORT_TARGET)
CHECK_TARGETS+=isort-check
FORMAT_TARGETS+=isort-format
