#:[base]
#:title = Base
#:description = Defines common build targets and basic settings for project.
#:
#:[target.install]
#:description = Install project. Installs the entire project either in
#:  `production` or `development` mode.
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
#:[setting.MXMAKE_MODE]
#:description = Run mode. either ``dev`` or ``prod``.
#:default = dev
#:
#:[setting.INSTALL_TARGETS]
#:description = Default `install` target dependencies.
#:default =
#:
#:[setting.DIRTY_TARGETS]
#:description = Default `dirty` target dependencies.
#:default =
#:
#:[setting.CLEAN_TARGETS]
#:description = Default `clean` target dependencies.
#:default =
#:
#:[setting.PURGE_TARGETS]
#:description = Default `purge` target dependencies.
#:default =
#:
#:[setting.DEV_INSTALL_TARGETS]
#:description = Additional `install` target dependencies in development mode.
#:default =
#:
#:[setting.DEV_DIRTY_TARGETS]
#:description = Additional `dirty` target dependencies in development mode.
#:default =
#:
#:[setting.DEV_CLEAN_TARGETS]
#:description = Additional `clean` target dependencies in development mode.
#:default =
#:
#:[setting.DEV_PURGE_TARGETS]
#:description = Additional `purge` target dependencies in development mode.
#:default =
#:
#:[setting.PROD_INSTALL_TARGETS]
#:description = Additional `install` target dependencies in production mode.
#:default =
#:
#:[setting.PROD_DIRTY_TARGETS]
#:description = Additional `dirty` target dependencies in production mode.
#:default =
#:
#:[setting.PROD_CLEAN_TARGETS]
#:description = Additional `clean` target dependencies in production mode.
#:default =
#:
#:[setting.PROD_PURGE_TARGETS]
#:description = Additional `purge` target dependencies in production mode.
#:default =

# Defensive settings for make: https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
# for Makefile debugging purposes add -x to the .SHELLFLAGS
.SHELLFLAGS:=-eu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# Sentinel files
SENTINEL_FOLDER?=.mxmake-sentinels
SENTINEL?=$(SENTINEL_FOLDER)/about.txt
$(SENTINEL):
	@mkdir -p $(SENTINEL_FOLDER)
	@echo "Sentinels for the Makefile process." > $(SENTINEL)
