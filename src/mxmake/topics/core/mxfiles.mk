#:[mxfiles]
#:title = Files
#:description = Project file generation.
#:depends = core.venv
#:
#:[target.mxfiles]
#:description = Create all project files by running ``mxdev``. It does not
#:  checkout sources.
#:
#:[target.mxfiles-dirty]
#:description = Build :ref:`mxfiles` target on next make run.
#:
#:[target.mxfiles-clean]
#:description = Remove generated project files.
#:
#:[setting.PROJECT_CONFIG]
#:description = The config file to use.
#:default = mx.ini
#:
#:[setting.SCRIPTS_FOLDER]
#:description = Target folder for generated scripts.
#:default = $(VENV_SCRIPTS)
#:
#:[setting.CONFIG_FOLDER]
#:description = Target folder for generated config files.
#:default = cfg

##############################################################################
# mxfiles
##############################################################################

# set environment variables for mxmake
define set_mxfiles_env
	@export MXMAKE_VENV_FOLDER=$(1)
	@export MXMAKE_SCRIPTS_FOLDER=$(2)
	@export MXMAKE_CONFIG_FOLDER=$(3)
endef

# unset environment variables for mxmake
define unset_mxfiles_env
	@unset MXMAKE_VENV_FOLDER
	@unset MXMAKE_SCRIPTS_FOLDER
	@unset MXMAKE_CONFIG_FOLDER
endef

FILES_TARGET:=$(SENTINEL_FOLDER)/mxfiles.sentinel
$(FILES_TARGET): $(PROJECT_CONFIG) $(VENV_TARGET)
	@echo "Create project files"
	$(call set_mxfiles_env,$(VENV_FOLDER),$(SCRIPTS_FOLDER),$(CONFIG_FOLDER))
	@$(VENV_SCRIPTS)mxdev -n -c $(PROJECT_CONFIG)
	$(call unset_mxfiles_env,$(VENV_FOLDER),$(SCRIPTS_FOLDER),$(CONFIG_FOLDER))
	@touch $(FILES_TARGET)

.PHONY: mxfiles
mxfiles: $(FILES_TARGET)

.PHONY: mxfiles-dirty
mxfiles-dirty:
	@rm -f $(FILES_TARGET)

.PHONY: mxfiles-clean
mxfiles-clean: mxfiles-dirty
	$(call set_mxfiles_env,$(VENV_FOLDER),$(SCRIPTS_FOLDER),$(CONFIG_FOLDER))
	@test -e $(VENV_SCRIPTS)mxmake && \
		$(VENV_SCRIPTS)mxmake clean -c $(PROJECT_CONFIG)
	$(call unset_mxfiles_env,$(VENV_FOLDER),$(SCRIPTS_FOLDER),$(CONFIG_FOLDER))
	@rm -f constraints-mxdev.txt requirements-mxdev.txt

INSTALL_TARGETS+=mxfiles
DIRTY_TARGETS+=mxfiles-dirty
CLEAN_TARGETS+=mxfiles-clean
