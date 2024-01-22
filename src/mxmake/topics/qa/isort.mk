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
#:[target.isort-dirty]
#:description = Marks isort dirty
#:
#:[target.isort-clean]
#:description = Uninstall isort.

##############################################################################
# isort
##############################################################################

ISORT_TARGET:=$(SENTINEL_FOLDER)/isort.sentinel
$(ISORT_TARGET): $(MXENV_TARGET)
	@echo "Install isort"
	@$(MXENV_PATH)pip install isort
	@touch $(ISORT_TARGET)

.PHONY: isort-check
isort-check: $(ISORT_TARGET)
	@echo "Run isort check"
	@$(MXENV_PATH)isort --check $(ISORT_SRC)

.PHONY: isort-format
isort-format: $(ISORT_TARGET)
	@echo "Run isort format"
	@$(MXENV_PATH)isort $(ISORT_SRC)

.PHONY: isort-dirty
isort-dirty:
	@rm -f $(ISORT_TARGET)

.PHONY: isort-clean
isort-clean: isort-dirty
	@test -e $(MXENV_PATH)pip && $(MXENV_PATH)pip uninstall -y isort || :

INSTALL_TARGETS+=$(ISORT_TARGET)
CHECK_TARGETS+=isort-check
FORMAT_TARGETS+=isort-format
DIRTY_TARGETS+=isort-dirty
CLEAN_TARGETS+=isort-clean
