#:[docs]
#:title = Documentation
#:description = Documentation generation with Sphinx.
#:depends = core.venv
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
#:[setting.DOCS_BIN]
#:description = The Sphinx build executable.
#:default = $(VENV_SCRIPTS)sphinx-build
#:
#:[setting.DOCS_AUTOBUILD_BIN]
#:description = The Sphinx auto build executable.
#:default = $(VENV_SCRIPTS)sphinx-autobuild
#:
#:[setting.DOCS_SOURCE]
#:description = Documentation source folder.
#:default = docs/source
#:
#:[setting.DOCS_TARGET]
#:description = Documentation generation target folder.
#:default = docs/html
#:
#:[setting.DOCS_REQUIREMENTS]
#:description = Documentation Python requirements to be installed (via pip).
#:default =


##############################################################################
# docs
##############################################################################

docs-install: venv
	@echo "Install Sphinx"
	@$(VENV_SCRIPTS)pip install -U sphinx sphinx-autobuild $(DOCS_REQUIREMENTS)

.PHONY: docs
docs: docs-install
	@echo "Build sphinx docs"
	@test -e $(DOCS_BIN) && $(DOCS_BIN) $(DOCS_SOURCE) $(DOCS_TARGET)
	@test -e $(DOCS_BIN) || echo "Sphinx binary not exists"

.PHONY: docs-live
docs-live: docs-install
	@echo "Rebuild Sphinx documentation on changes, with live-reload in the browser"
	@test -e $(DOCS_AUTOBUILD_BIN) && $(DOCS_AUTOBUILD_BIN) $(DOCS_SOURCE) $(DOCS_TARGET)
	@test -e $(DOCS_AUTOBUILD_BIN) || echo "Sphinx autobuild binary not exists"

.PHONY: docs-clean
docs-clean:
	@rm -rf $(DOCS_TARGET)
