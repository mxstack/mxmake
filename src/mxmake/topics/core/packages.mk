#:[packages]
#:title = Packages
#:description = Install python packages.
#:depends = core.sources
#:
#:[target.packages]
#:description = Install packages with pip after creating files and checking
#:  out sources.
#:
#:[target.packages-dirty]
#:description = Build packages target on next make run.

##############################################################################
# packages
##############################################################################

INSTALLED_PACKAGES=.installed.txt

PACKAGES_TARGET:=$(SENTINEL_FOLDER)/packages.sentinel
$(PACKAGES_TARGET): sources
	@echo "Install python packages"
	@$(VENV_SCRIPTS)pip install -r requirements-mxdev.txt
	@$(VENV_SCRIPTS)pip freeze > $(INSTALLED_PACKAGES)
	@touch $(PACKAGES_TARGET)

.PHONY: packages
packages: $(PACKAGES_TARGET)

.PHONY: packages-dirty
packages-dirty:
	@rm -f $(PACKAGES_TARGET)

INSTALL_TARGETS+=packages
DIRTY_TARGETS+=packages-dirty