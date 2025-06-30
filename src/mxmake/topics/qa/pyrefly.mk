#:[pyrefly]
#:title = pyrefly
#:description = Static code analysis with pyrefly https://pyrefly.org/
#:depends = core.packages
#:
#:[target.pyrefly]
#:description = Run pyrefly.
#:
#:[setting.PYREFLY_SRC]
#:description = Source folder for code analysis. Left empty to use value from pyproject.toml
#:default = src
#:
#:[setting.PYREFLY_REQUIREMENTS]
#:description = Python requirements to be installed (via pip).
#:default =
#:
#:[target.pyrefly-dirty]
#:description = Marks pyrefly dirty
#:
#:[target.pyrefly-clean]
#:description = Uninstall pyrefly and removes cached data.

##############################################################################
# pyrefly
##############################################################################

PYREFLY_TARGET:=$(SENTINEL_FOLDER)/pyrefly.sentinel
$(PYREFLY_TARGET): $(MXENV_TARGET)
	@echo "Install pyrefly"
	@$(PYTHON_PACKAGE_COMMAND) install pyrefly $(PYREFLY_REQUIREMENTS)
	@touch $(PYREFLY_TARGET)

.PHONY: pyrefly
pyrefly: $(PACKAGES_TARGET) $(PYREFLY_TARGET)
	@echo "Run pyrefly"
	@pyrefly check $(PYREFLY_SRC)

.PHONY: pyrefly-dirty
pyrefly-dirty:
	@rm -f $(PYREFLY_TARGET)

.PHONY: pyrefly-clean
pyrefly-clean: pyrefly-dirty
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y pyrefly || :

INSTALL_TARGETS+=$(PYREFLY_TARGET)
CHECK_TARGETS+=pyrefly
CLEAN_TARGETS+=pyrefly-clean
DIRTY_TARGETS+=pyrefly-dirty
