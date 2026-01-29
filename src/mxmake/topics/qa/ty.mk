#:[ty]
#:title = ty
#:description = Static type checking with ty (Astral's fast type checker).
#:depends = core.packages
#:
#:[target.ty]
#:description = Run ty type checker.
#:
#:[setting.TY_SRC]
#:description = Source folder for type checking.
#:default = src
#:
#:[setting.TY_PYTHON_VERSION]
#:description = Target Python version for type checking (e.g., 3.12).
#:  Leave empty to use default detection.
#:default =
#:
#:[setting.TY_VERSION]
#:description = ty version to use with uvx (e.g., 0.0.1a1).
#:  Leave empty for latest. Only used when TOOL_RUNNER=uvx.
#:default =
#:
#:[target.ty-dirty]
#:description = Marks ty dirty.
#:
#:[target.ty-clean]
#:description = Uninstall ty and removes cached data.

##############################################################################
# ty
##############################################################################

# Adjust TY_SRC to respect PROJECT_PATH_PYTHON if still at default
ifeq ($(TY_SRC),src)
TY_SRC:=$(PYTHON_PROJECT_PREFIX)src
endif

# Build ty flags
TY_FLAGS:=
ifneq ($(TY_PYTHON_VERSION),)
TY_FLAGS+=--python-version $(TY_PYTHON_VERSION)
endif

# Installation target (only in venv mode)
ifneq ("$(SKIP_TOOL_INSTALL)","true")
TY_TARGET:=$(SENTINEL_FOLDER)/ty.sentinel
$(TY_TARGET): $(MXENV_TARGET)
	@echo "Install ty"
	@$(PYTHON_PACKAGE_COMMAND) install ty
	@touch $(TY_TARGET)
INSTALL_TARGETS+=$(TY_TARGET)
endif

# Conditional dependency
TY_DEPENDENCY:=$(if $(filter true,$(SKIP_TOOL_INSTALL)),,$(TY_TARGET))

.PHONY: ty
ty: $(PACKAGES_TARGET) $(TY_DEPENDENCY)
	@echo "Run ty"
	@$(call RUN_TOOL,ty,$(TY_VERSION),check $(TY_FLAGS) $(TY_SRC))

.PHONY: ty-dirty
ty-dirty:
	@rm -f $(TY_TARGET)

.PHONY: ty-clean
ty-clean: ty-dirty
ifneq ("$(SKIP_TOOL_INSTALL)","true")
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y ty || :
endif
	@rm -rf .ty
CHECK_TARGETS+=ty
TYPECHECK_TARGETS+=ty
CLEAN_TARGETS+=ty-clean
DIRTY_TARGETS+=ty-dirty
