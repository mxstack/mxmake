#:[clean]
#:title = Clean
#:description = Project cleanup.
#:depends = core.coverage
#:
#:[target.clean]
#:description = Cleanup project environment.
#:
#:[target.full-clean]
#:description = Cleanup project environment including sources.
#:
#:[target.runtime-clean]
#:description = Remove runtime artifacts, like byte-code and caches.
#:
#:[setting.CLEAN_TARGETS]
#:description = Space separated list of files and folders to remove.
#:default =

###############################################################################
# clean
###############################################################################

CLEAN_TARGETS?=

.PHONY: clean
clean: files-clean venv-clean docs-clean coverage-clean
	@rm -rf $(CLEAN_TARGETS) .sentinels .installed.txt

.PHONY: full-clean
full-clean: clean sources-clean

.PHONY: runtime-clean
runtime-clean:
	@echo "Remove runtime artifacts, like byte-code and caches."
	@find . -name '*.py[c|o]' -delete
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +
