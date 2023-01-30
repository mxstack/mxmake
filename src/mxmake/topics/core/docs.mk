#:[docs]
#:title = Documentation
#:description = Documentation generation with Sphinx.
#:depends = core.mxenv
#:
#:[target.docs]
#:description = Generate Sphinx docs. Sphinx is expected to be installed. This
#:  is not done automatically.
#:
#:[target.docs-live]
#:description = Rebuild Sphinx documentation on changes, with live-reload in the browser.
#:
#:[target.docs-clean]
#:description = Removes generated docs.
#:
#:[setting.DOCS_SOURCE_FOLDER]
#:description = Documentation source folder.
#:default = docs/source
#:
#:[setting.DOCS_TARGET_FOLDER]
#:description = Documentation generation target folder.
#:default = docs/html
#:
#:[setting.DOCS_REQUIREMENTS]
#:description = Documentation Python requirements to be installed (via pip).
#:default =

##############################################################################
# docs
##############################################################################

DOCS_BIN=$(MXENV_PATH)sphinx-build
DOCS_AUTOBUILD_BIN=$(MXENV_PATH)sphinx-autobuild

DOCS_TARGET:=$(SENTINEL_FOLDER)/docs.sentinel
$(DOCS_TARGET): $(MXENV_TARGET)
	@echo "Install Sphinx"
	@$(MXENV_PATH)pip install -U sphinx sphinx-autobuild $(DOCS_REQUIREMENTS)
	@touch $(DOCS_TARGET)

.PHONY: docs-install
docs-install: $(DOCS_TARGET)

.PHONY: docs
docs: docs-install
	@echo "Build sphinx docs"
	@test -e $(DOCS_BIN) && $(DOCS_BIN) $(DOCS_SOURCE_FOLDER) $(DOCS_TARGET_FOLDER)
	@test -e $(DOCS_BIN) || echo "Sphinx binary not exists"

.PHONY: docs-live
docs-live: docs-install
	@echo "Rebuild Sphinx documentation on changes, with live-reload in the browser"
	@test -e $(DOCS_AUTOBUILD_BIN) && $(DOCS_AUTOBUILD_BIN) $(DOCS_SOURCE_FOLDER) $(DOCS_TARGET_FOLDER)
	@test -e $(DOCS_AUTOBUILD_BIN) || echo "Sphinx autobuild binary not exists"

.PHONY: docs-dirty
docs-dirty:
	@rm -f $(DOCS_TARGET)

.PHONY: docs-clean
docs-clean: docs-dirty
	@rm -rf $(DOCS_TARGET_FOLDER)

INSTALL_TARGETS+=docs-install
DIRTY_TARGETS+=docs-dirty
CLEAN_TARGETS+=docs-clean
