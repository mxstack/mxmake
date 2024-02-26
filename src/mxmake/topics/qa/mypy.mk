#:[mypy]
#:title = mypy
#:description = Static code analysis with mypy.
#:depends = core.packages
#:
#:[target.mypy]
#:description = Run mypy.
#:
#:[setting.MYPY_SRC]
#:description = Source folder for code analysis.
#:default = src
#:
#:[setting.MYPY_REQUIREMENTS]
#:description = Mypy Python requirements to be installed (via pip).
#:default = types-setuptools
#:
#:[target.mypy-dirty]
#:description = Marks mypy dirty
#:
#:[target.mypy-clean]
#:description = Uninstall mypy and removes cached data.

##############################################################################
# mypy
##############################################################################

MYPY_TARGET:=$(SENTINEL_FOLDER)/mypy.sentinel
$(MYPY_TARGET): $(MXENV_TARGET)
	@echo "Install mypy"
	@$(PYTHON_PACKAGE_COMMAND) install mypy $(MYPY_REQUIREMENTS)
	@touch $(MYPY_TARGET)

.PHONY: mypy
mypy: $(PACKAGES_TARGET) $(MYPY_TARGET)
	@echo "Run mypy"
	@mypy $(MYPY_SRC)

.PHONY: mypy-dirty
mypy-dirty:
	@rm -f $(MYPY_TARGET)

.PHONY: mypy-clean
mypy-clean: mypy-dirty
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y mypy || :
	@rm -rf .mypy_cache

INSTALL_TARGETS+=$(MYPY_TARGET)
TYPECHECK_TARGETS+=mypy
CLEAN_TARGETS+=mypy-clean
DIRTY_TARGETS+=mypy-dirty
