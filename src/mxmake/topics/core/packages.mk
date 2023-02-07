#:[packages]
#:title = Packages
#:description = Install python packages.
#:depends = core.mxfiles
#:
#:[target.packages]
#:description = Install packages with pip after creating files and checking
#:  out sources.
#:
#:[target.packages-dirty]
#:description = Build packages target on next make run.
#:
#:[target.packages-clean]
#:description = Remove prior installed packages

##############################################################################
# packages
##############################################################################

# additional sources targets which requires package re-install on change
-include $(MXMAKE_FILES)/additional_sources_targets.mk
ADDITIONAL_SOURCES_TARGETS?=

INSTALLED_PACKAGES=$(MXMAKE_FILES)/installed.txt

PACKAGES_TARGET:=$(INSTALLED_PACKAGES)
$(PACKAGES_TARGET): $(FILES_TARGET) $(ADDITIONAL_SOURCES_TARGETS)
	@echo "Install python packages"
	@$(MXENV_PATH)pip install -r $(FILES_TARGET)
	@$(MXENV_PATH)pip freeze > $(INSTALLED_PACKAGES)
	@touch $(PACKAGES_TARGET)

.PHONY: packages
packages: $(PACKAGES_TARGET)

.PHONY: packages-dirty
packages-dirty:
	@rm -f $(PACKAGES_TARGET)

.PHONY: packages-clean
packages-clean:
	@test -e $(FILES_TARGET) \
		&& test -e $(MXENV_PATH)pip \
		&& $(MXENV_PATH)pip uninstall -y -r $(FILES_TARGET) \
		|| :
	@rm -f $(PACKAGES_TARGET)

INSTALL_TARGETS+=packages
DIRTY_TARGETS+=packages-dirty
CLEAN_TARGETS+=packages-clean
