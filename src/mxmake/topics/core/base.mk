#:[base]
#:title = Base
#:description = Defines common build targets and basic settings for project.
#:
#:[target.install]
#:description = Install project. Installs the entire project supposed for
#:  development.
#:
#:[target.deploy]
#:description = Deploy project. Supposed to setup a production version of
#:  the project.
#:
#:[target.run]
#:description = Run project. Depending on target defined in `RUN_TARGET`
#:
#:[target.dirty]
#:description = Force make to rebuild targets on next make run.
#:
#:[target.clean]
#:description = Clean project. Removes all installation related files.
#:
#:[target.purge]
#:description = Purge project. Removes all installation related files and data.
#:  THIS IS AN OPERATION FOR POTENTIAL DATA LOSS! USE SPARINGLY AND AT YOUR
#:  OWN RISK!
#:
#:[target.runtime-clean]
#:description = Remove runtime artifacts, like byte-code and caches.
#:
#:[target.qa]
#:description = Run all QA related targets. only gets included if any qa
#:  related domain is used.
#:
#:[setting.DEPLOY_TARGETS]
#:description = `deploy` target dependencies.
#:default =
#:
#:[setting.RUN_TARGET]
#:description = target to be executed when calling `make run`
#:default =
#:
#:[setting.CLEAN_FS]
#:description = Additional files and folders to remove when running clean target
#:default =
#:
#:[setting.INCLUDE_MAKEFILE]
#:description = Optional makefile to include before default targets. This can
#:  be used to provide custom targets or hook up to existing targets.
#:default = include.mk
#:
#:[setting.EXTRA_PATH]
#:description = Optional additional directories to be added to PATH in format
#:  `/path/to/dir/:/path/to/other/dir`. Gets inserted first, thus gets searched
#:  first.
#:default =

export PATH:=$(if $(EXTRA_PATH),$(EXTRA_PATH):,)$(PATH)

# Defensive settings for make: https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
# for Makefile debugging purposes add -x to the .SHELLFLAGS
.SHELLFLAGS:=-eu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# mxmake folder
MXMAKE_FOLDER?=.mxmake

# Sentinel files
SENTINEL_FOLDER?=$(MXMAKE_FOLDER)/sentinels
SENTINEL?=$(SENTINEL_FOLDER)/about.txt
$(SENTINEL):
	@mkdir -p $(SENTINEL_FOLDER)
	@echo "Sentinels for the Makefile process." > $(SENTINEL)
