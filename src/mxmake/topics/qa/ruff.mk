#:[ruff]
#:title = ruff
#:description = Code formatting with ruff.
#:depends = core.mxenv
#:
#:[target.ruff]
#:description = Run ruff.
#:
#:[setting.RUFF_SRC]
#:description = Source folder to scan for Python files to run ruff on.
#:default = src
#:
#:[target.ruff-dirty]
#:description = Marks ruff dirty
#:
#:[target.ruff-clean]
#:description = Uninstall ruff.

##############################################################################
# ruff
##############################################################################

RUFF_TARGET:=$(SENTINEL_FOLDER)/ruff.sentinel
$(RUFF_TARGET): $(MXENV_TARGET)
	@echo "Install Ruff"
	@$(MXENV_PYTHON) -m pip install ruff
	@touch $(RUFF_TARGET)

.PHONY: ruff-check
ruff-check: $(RUFF_TARGET)
	@echo "Run ruff check"
	@$(MXENV_PATH)ruff check $(RUFF_SRC)

.PHONY: ruff-format
ruff-format: $(RUFF_TARGET)
	@echo "Run ruff format"
	@$(MXENV_PATH)ruff format $(RUFF_SRC)

.PHONY: ruff-dirty
ruff-dirty:
	@rm -f $(RUFF_TARGET)

.PHONY: ruff-clean
ruff-clean: ruff-dirty
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y ruff || :
	@rm -rf .ruff_cache

INSTALL_TARGETS+=$(RUFF_TARGET)
CHECK_TARGETS+=ruff-check
FORMAT_TARGETS+=ruff-format
DIRTY_TARGETS+=ruff-dirty
CLEAN_TARGETS+=ruff-clean
