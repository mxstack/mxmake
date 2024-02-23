#:[mxfiles]
#:title = MX Files
#:description = Project file generation.
#:depends = core.mxenv
#:soft-depends = core.sources
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

##############################################################################
# mxfiles
##############################################################################

# case `core.sources` domain not included
SOURCES_TARGET?=

# File generation target
MXMAKE_FILES?=$(MXMAKE_FOLDER)/files

# set environment variables for mxmake
define set_mxfiles_env
	@export MXMAKE_FILES=$(1)
endef

# unset environment variables for mxmake
define unset_mxfiles_env
	@unset MXMAKE_FILES
endef

$(PROJECT_CONFIG):
ifneq ("$(wildcard $(PROJECT_CONFIG))","")
	@touch $(PROJECT_CONFIG)
else
	@echo "[settings]" > $(PROJECT_CONFIG)
endif

LOCAL_PACKAGE_FILES:=$(wildcard pyproject.toml setup.cfg setup.py requirements.txt constraints.txt)

FILES_TARGET:=requirements-mxdev.txt
$(FILES_TARGET): $(PROJECT_CONFIG) $(MXENV_TARGET) $(SOURCES_TARGET) $(LOCAL_PACKAGE_FILES)
	@echo "Create project files"
	@mkdir -p $(MXMAKE_FILES)
	$(call set_mxfiles_env,$(MXMAKE_FILES))
	@mxdev -n -c $(PROJECT_CONFIG)
	$(call unset_mxfiles_env)
	@test -e $(MXMAKE_FILES)/pip.conf && cp $(MXMAKE_FILES)/pip.conf $(VENV_FOLDER)/pip.conf || :
	@touch $(FILES_TARGET)

.PHONY: mxfiles
mxfiles: $(FILES_TARGET)

.PHONY: mxfiles-dirty
mxfiles-dirty:
	@touch $(PROJECT_CONFIG)

.PHONY: mxfiles-clean
mxfiles-clean: mxfiles-dirty
	@rm -rf constraints-mxdev.txt requirements-mxdev.txt $(MXMAKE_FILES)

INSTALL_TARGETS+=mxfiles
DIRTY_TARGETS+=mxfiles-dirty
CLEAN_TARGETS+=mxfiles-clean
