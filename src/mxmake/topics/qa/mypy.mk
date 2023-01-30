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

##############################################################################
# mypy
##############################################################################

MYPY_TARGET:=$(SENTINEL_FOLDER)/mypy.sentinel
$(MYPY_TARGET): $(MXENV_TARGET)
	@echo "Install mypy"
	@$(MXENV_PATH)pip install mypy $(MYPY_REQUIREMENTS)
	@touch $(MYPY_TARGET)

.PHONY: mypy-install
mypy-install: $(MYPY_TARGET)

.PHONY: mypy
mypy: $(PACKAGES_TARGET) mypy-install
	@echo "Run mypy"
	@$(MXENV_PATH)mypy $(MYPY_SRC)

INSTALL_TARGETS+=mypy-install
