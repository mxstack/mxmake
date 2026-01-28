#:[ruff]
#:title = ruff
#:description = Code formatting with ruff.
#:depends = core.mxenv
#:
#:[target.ruff]
#:description = Run ruff.
#:
#:[target.ruff-format]
#:description = Run ruff format. Optionally apply fixes with RUFF_FIXES=true.
#:
#:[setting.RUFF_SRC]
#:description = Source folder to scan for Python files to run ruff on.
#:default = src
#:
#:[setting.RUFF_FIXES]
#:description = Enable ruff check --fix when running ruff-format.
#:  Set to `true` to enable automatic fixes.
#:default = false
#:
#:[setting.RUFF_UNSAFE_FIXES]
#:description = Enable unsafe fixes when RUFF_FIXES is enabled.
#:  Set to `true` to enable unsafe fixes.
#:default = false
#:
#:[target.ruff-dirty]
#:description = Marks ruff dirty
#:
#:[target.ruff-clean]
#:description = Uninstall ruff.

##############################################################################
# ruff
##############################################################################

# Adjust RUFF_SRC to respect PROJECT_PATH_PYTHON if still at default
ifeq ($(RUFF_SRC),src)
RUFF_SRC:=$(PYTHON_PROJECT_PREFIX)src
endif

# Build ruff check flags based on settings
ifeq ("$(RUFF_FIXES)","true")
ifeq ("$(RUFF_UNSAFE_FIXES)","true")
RUFF_FIX_FLAGS=--fix --unsafe-fixes
else
RUFF_FIX_FLAGS=--fix
endif
endif

RUFF_TARGET:=$(SENTINEL_FOLDER)/ruff.sentinel
$(RUFF_TARGET): $(MXENV_TARGET)
	@echo "Install Ruff"
	@$(PYTHON_PACKAGE_COMMAND) install ruff
	@touch $(RUFF_TARGET)

.PHONY: ruff-check
ruff-check: $(RUFF_TARGET)
	@echo "Run ruff check"
	@ruff check $(RUFF_SRC)

.PHONY: ruff-format
ruff-format: $(RUFF_TARGET)
	@echo "Run ruff format"
	@ruff format $(RUFF_SRC)
ifeq ("$(RUFF_FIXES)","true")
	@echo "Run ruff check $(RUFF_FIX_FLAGS)"
	@ruff check $(RUFF_FIX_FLAGS) $(RUFF_SRC)
endif

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
