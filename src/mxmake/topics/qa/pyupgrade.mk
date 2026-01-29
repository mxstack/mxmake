#:[pyupgrade]
#:title = pyupgrade
#:description = Automatically upgrade syntax for newer versions of the language.
#:depends = core.mxenv
#:
#:[target.pyupgrade]
#:description = Run pyupgrade.
#:
#:[setting.PYUPGRADE_SRC]
#:description = Source folder to scan for XML and ZCML files.
#:default = src
#:
#:[setting.PYUPGRADE_PARAMETERS]
#:description = Additional parameters for pyupgrade, see https://github.com/asottile/pyupgrade for details.
#:default = --py38-plus
#:
#:[setting.PYUPGRADE_VERSION]
#:description = pyupgrade version to use with uvx (e.g., 3.17.0).
#:  Leave empty for latest. Only used when TOOL_RUNNER=uvx.
#:default =
#:
#:[target.pyupgrade-dirty]
#:description = Marks pyupgrade dirty
#:
#:[target.pyupgrade-clean]
#:description = Uninstall pyupgrade.

##############################################################################
# pyupgrade
##############################################################################

# Adjust PYUPGRADE_SRC to respect PROJECT_PATH_PYTHON if still at default
ifeq ($(PYUPGRADE_SRC),src)
PYUPGRADE_SRC:=$(PYTHON_PROJECT_PREFIX)src
endif

# Installation target (only in venv mode)
ifneq ("$(SKIP_TOOL_INSTALL)","true")
PYUPGRADE_TARGET:=$(SENTINEL_FOLDER)/pyupgrade.sentinel
$(PYUPGRADE_TARGET): $(MXENV_TARGET)
	@echo "Install pyupgrade"
	@$(PYTHON_PACKAGE_COMMAND) install pyupgrade
	@touch $(PYUPGRADE_TARGET)
INSTALL_TARGETS+=$(PYUPGRADE_TARGET)
endif

# Conditional dependency
PYUPGRADE_DEPENDENCY:=$(if $(filter true,$(SKIP_TOOL_INSTALL)),,$(PYUPGRADE_TARGET))

# Build pyupgrade command based on mode
ifeq ("$(SKIP_TOOL_INSTALL)","true")
PYUPGRADE_CMD:=uvx pyupgrade$(if $(strip $(PYUPGRADE_VERSION)),==$(strip $(PYUPGRADE_VERSION)),)
else
PYUPGRADE_CMD:=pyupgrade
endif

.PHONY: pyupgrade-format
pyupgrade-format: $(PYUPGRADE_DEPENDENCY)
	@echo "Run pyupgrade format in: $(PYUPGRADE_SRC)"
	@find $(PYUPGRADE_SRC) -name '*.py' -exec $(PYUPGRADE_CMD) $(PYUPGRADE_PARAMETERS) {} +

.PHONY: pyupgrade-dirty
pyupgrade-dirty:
	@rm -f $(PYUPGRADE_TARGET)

.PHONY: pyupgrade-clean
pyupgrade-clean: pyupgrade-dirty
ifneq ("$(SKIP_TOOL_INSTALL)","true")
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y pyupgrade || :
endif
FORMAT_TARGETS+=pyupgrade-format
DIRTY_TARGETS+=pyupgrade-dirty
CLEAN_TARGETS+=pyupgrade-clean
