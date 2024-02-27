#:[sphinx]
#:title = Sphinx Documentation
#:description = Documentation generation with Sphinx.
#:depends = core.mxenv
#:soft-depends = docs.jsdoc
#:
#:[target.docs]
#:description = Generate Sphinx docs.
#:
#:[target.docs-live]
#:description = Rebuild Sphinx documentation on changes, with live-reload in
#:  the browser using `sphinx-autobuild`.
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
# sphinx
##############################################################################

# additional targets required for building docs.
DOCS_TARGETS+=

SPHINX_BIN=sphinx-build
SPHINX_AUTOBUILD_BIN=sphinx-autobuild

DOCS_TARGET:=$(SENTINEL_FOLDER)/sphinx.sentinel
$(DOCS_TARGET): $(MXENV_TARGET)
	@echo "Install Sphinx"
	@$(PYTHON_PACKAGE_COMMAND) install -U sphinx sphinx-autobuild $(DOCS_REQUIREMENTS)
	@touch $(DOCS_TARGET)

.PHONY: docs
docs: $(DOCS_TARGET) $(DOCS_TARGETS)
	@echo "Build sphinx docs"
	@$(SPHINX_BIN) $(DOCS_SOURCE_FOLDER) $(DOCS_TARGET_FOLDER)

.PHONY: docs-live
docs-live: $(DOCS_TARGET) $(DOCS_TARGETS)
	@echo "Rebuild Sphinx documentation on changes, with live-reload in the browser"
	@$(SPHINX_AUTOBUILD_BIN) $(DOCS_SOURCE_FOLDER) $(DOCS_TARGET_FOLDER)

.PHONY: docs-dirty
docs-dirty:
	@rm -f $(DOCS_TARGET)

.PHONY: docs-clean
docs-clean: docs-dirty
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y \
		sphinx sphinx-autobuild $(DOCS_REQUIREMENTS) || :
	@rm -rf $(DOCS_TARGET_FOLDER)

INSTALL_TARGETS+=$(DOCS_TARGET)
DIRTY_TARGETS+=docs-dirty
CLEAN_TARGETS+=docs-clean
