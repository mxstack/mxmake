#:[sources]
#:title = Sources
#:description = Source package management.
#:depends = core.mxenv
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
$(SOURCES_TARGET): $(PROJECT_CONFIG) $(MXENV_TARGET)
	@echo "Checkout project sources"
	@mxdev -o -c $(PROJECT_CONFIG)
	@touch $(SOURCES_TARGET)

.PHONY: sources
sources: $(SOURCES_TARGET)

.PHONY: sources-dirty
sources-dirty:
	@rm -f $(SOURCES_TARGET)

.PHONY: sources-purge
sources-purge: sources-dirty
	@rm -rf sources

INSTALL_TARGETS+=sources
DIRTY_TARGETS+=sources-dirty
PURGE_TARGETS+=sources-purge
