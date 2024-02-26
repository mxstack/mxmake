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
#:[target.pyupgrade-dirty]
#:description = Marks pyupgrade dirty
#:
#:[target.pyupgrade-clean]
#:description = Uninstall pyupgrade.

##############################################################################
# pyupgrade
##############################################################################

PYUPGRADE_TARGET:=$(SENTINEL_FOLDER)/pyupgrade.sentinel
$(PYUPGRADE_TARGET): $(MXENV_TARGET)
	@echo "Install pyupgrade"
	@$(PYTHON_PACKAGE_COMMAND) install pyupgrade
	@touch $(PYUPGRADE_TARGET)

.PHONY: pyupgrade-format
pyupgrade-format: $(PYUPGRADE_TARGET)
	@echo "Run pyupgrade format in: $(PYUPGRADE_SRC)"
	@find $(PYUPGRADE_SRC) -name '*.py' -exec pyupgrade $(PYUPGRADE_PARAMETERS) {} +

.PHONY: pyupgrade-dirty
pyupgrade-dirty:
	@rm -f $(PYUPGRADE_TARGET)

.PHONY: pyupgrade-clean
pyupgrade-clean: pyupgrade-dirty
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y pyupgrade || :

INSTALL_TARGETS+=$(PYUPGRADE_TARGET)
FORMAT_TARGETS+=pyupgrade-format
DIRTY_TARGETS+=pyupgrade-dirty
CLEAN_TARGETS+=pyupgrade-clean
