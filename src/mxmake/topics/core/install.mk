#:[install]
#:title = Install
#:description = Project installation.
#:depends = core.sources
#:
#:[target.install]
#:description = Install packages with pip after creating files and checking
#:  out sources.
#:
#:[target.install-dirty]
#:description = Build :ref:`install` target on next make run.

##############################################################################
# install
##############################################################################

INSTALLED_PACKAGES=.installed.txt

INSTALL_TARGET:=$(SENTINEL_FOLDER)/install.sentinel
$(INSTALL_TARGET): $(SOURCES_TARGET)
	@echo "Install python packages"
	@$(VENV_SCRIPTS)pip install -r requirements-mxdev.txt
	@$(VENV_SCRIPTS)pip freeze > $(INSTALLED_PACKAGES)
	@touch $(INSTALL_TARGET)

.PHONY: install
install: $(INSTALL_TARGET)

.PHONY: install-dirty
install-dirty:
	@rm -f $(INSTALL_TARGET)
