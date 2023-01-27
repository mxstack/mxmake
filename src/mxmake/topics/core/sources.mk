#:[sources]
#:title = Sources
#:description = Source package management.
#:depends = core.files
#:
#:[target.sources]
#:description = Checkout sources by running ``mxdev``. It does not generate
#:  project files.
#:
#:[target.sources-dirty]
#:description = Build :ref:`sources` target on next make run.
#:
#:[target.sources-purge]
#:description = Removes sources folder.

##############################################################################
# sources
##############################################################################

SOURCES_TARGET:=$(SENTINEL_FOLDER)/sources.sentinel
$(SOURCES_TARGET): $(FILES_TARGET)
	@echo "Checkout project sources"
	@$(VENV_SCRIPTS)mxdev -o -c $(PROJECT_CONFIG)
	@touch $(SOURCES_TARGET)

.PHONY: sources
sources: $(SOURCES_TARGET)

.PHONY: sources-dirty
sources-dirty:
	@rm -f $(SOURCES_TARGET)

.PHONY: sources-purge
sources-purge: sources-dirty
	@rm -rf sources

DEV_INSTALL_TARGETS+=sources
DEV_DIRTY_TARGETS+=sources-dirty
DEV_PURGE_TARGETS+=sources-purge
