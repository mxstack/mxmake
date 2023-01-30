#:[isort]
#:title = isort
#:description = Import sorting with isort.
#:depends = core.packages
#:
#:[target.isort]
#:description = Run isort.
#:
#:[setting.ISORT_SRC]
#:description = Source folder for import sorting.
#:default = src

##############################################################################
# isort
##############################################################################

ISORT_TARGET:=$(SENTINEL_FOLDER)/isort.sentinel
$(ISORT_TARGET): $(MXENV_TARGET)
	@echo "Install isort"
	@$(MXENV_PATH)pip install isort
	@touch $(ISORT_TARGET)

.PHONY: isort
isort: $(PACKAGES_TARGET) $(ISORT_TARGET)
	@echo "Run isort"
	@$(MXENV_PATH)isort $(ISORT_SRC)

INSTALL_TARGETS+=$(ISORT_TARGET)
QA_TARGETS+=isort
