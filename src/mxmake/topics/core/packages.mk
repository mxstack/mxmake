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
#:
#:[setting.PACKAGES_ALLOW_PRERELEASES]
#:description = Allow prerelease and development versions.
#:  By default, the package installer only finds stable versions.
#:default = false
##############################################################################
# packages
##############################################################################

# additional sources targets which requires package re-install on change
-include $(MXMAKE_FILES)/additional_sources_targets.mk
ADDITIONAL_SOURCES_TARGETS?=

INSTALLED_PACKAGES=$(MXMAKE_FILES)/installed.txt

ifeq ("$(PACKAGES_ALLOW_PRERELEASES)","true")
ifeq ("$(PYTHON_PACKAGE_INSTALLER)","uv")
PACKAGES_PRERELEASES=--prerelease=allow
else
PACKAGES_PRERELEASES=--pre
endif
else
PACKAGES_PRERELEASES=
endif

PACKAGES_TARGET:=$(INSTALLED_PACKAGES)
$(PACKAGES_TARGET): $(FILES_TARGET) $(ADDITIONAL_SOURCES_TARGETS)
	@echo "Install python packages"
	@$(PYTHON_PACKAGE_COMMAND) install $(PACKAGES_PRERELEASES) -r $(FILES_TARGET)
	@$(PYTHON_PACKAGE_COMMAND) freeze > $(INSTALLED_PACKAGES)
	@touch $(PACKAGES_TARGET)

.PHONY: packages
packages: $(PACKAGES_TARGET)

.PHONY: packages-dirty
packages-dirty:
	@rm -f $(PACKAGES_TARGET)

.PHONY: packages-clean
packages-clean:
	@test -e $(FILES_TARGET) \
		&& test -e $(MXENV_PYTHON) \
		&& $(MXENV_PYTHON) -m pip uninstall -y -r $(FILES_TARGET) \
		|| :
	@rm -f $(PACKAGES_TARGET)

INSTALL_TARGETS+=packages
DIRTY_TARGETS+=packages-dirty
CLEAN_TARGETS+=packages-clean
