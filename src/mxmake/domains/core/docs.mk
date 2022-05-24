#:[docs]
#:title = Documentation
#:description = Documentation generation with Sphinx.
#:depends = core.venv
#:
#:[target.docs]
#:description = Generate sphinx docs. Sphinx is expected to be installed. This
#:  is not done automatically.
#:
#:[target.docs-clean]
#:description = Removes generated docs.
#:
#:[setting.DOCS_BIN]
#:description = The Sphinx build executable.
#:default = $(VENV_FOLDER)/bin/sphinx-build
#:
#:[setting.DOCS_SOURCE]
#:description = Documentation source folder.
#:default = docs/source
#:
#:[setting.DOCS_TARGET]
#:description = Documentation generation target folder.
#:default = docs/html

###############################################################################
# docs
###############################################################################

DOCS_BIN?=$(VENV_FOLDER)/bin/sphinx-build
DOCS_SOURCE?=docs/source
DOCS_TARGET?=docs/html

.PHONY: docs
docs:
	@echo "Build sphinx docs"
	@test -e $(DOCS_BIN) && $(DOCS_BIN) $(DOCS_SOURCE) $(DOCS_TARGET)
	@test -e $(DOCS_BIN) || echo "Sphinx binary not exists"

.PHONY: docs-clean
docs-clean:
	@rm -rf $(DOCS_TARGET)
