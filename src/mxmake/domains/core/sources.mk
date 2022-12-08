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
#:[target.sources-clean]
#:description = Removes sources folder.

##############################################################################
# sources
##############################################################################

SOURCES_SENTINEL:=$(SENTINEL_FOLDER)/sources.sentinel
$(SOURCES_SENTINEL): $(FILES_SENTINEL)
	@echo "Checkout project sources"
	@$(VENV_FOLDER)/bin/mxdev -o -c $(PROJECT_CONFIG)
	@touch $(SOURCES_SENTINEL)

.PHONY: sources
sources: $(SOURCES_SENTINEL)

.PHONY: sources-dirty
sources-dirty:
	@rm -f $(SOURCES_SENTINEL)

.PHONY: sources-clean
sources-clean: sources-dirty
	@rm -rf sources
