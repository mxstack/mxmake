#:[jsdoc]
#:title = JSDoc Documentation
#:description = JSDoc installation and integration into Sphinx.
#:depends = js.npm
#:
#:[target.jsdoc]
#:description = Provide jsdoc executable on PATH.

##############################################################################
# jsdoc
##############################################################################

JSDOC_PATH=$(shell pwd)/$(NPM_PREFIX)/node_modules/jsdoc

JSDOC_TARGET:=$(SENTINEL_FOLDER)/jsdoc.sentinel
$(JSDOC_TARGET): $(NPM_TARGET)
	@echo "Link jsdoc executable to name expected by Sphinx"
	@ln -sf $(JSDOC_PATH)/jsdoc.js $(JSDOC_PATH)/jsdoc
	@touch $(JSDOC_TARGET)

.PHONY: jsdoc
jsdoc: $(JSDOC_TARGET)
	@export PATH=$(PATH):$(JSDOC_PATH)

# extend npm dev packages
NPM_DEV_PACKAGES+=jsdoc

# extend sphinx requirements and docs targets
DOCS_REQUIREMENTS+=sphinx_js
DOCS_TARGETS+=jsdoc

# extend default targets
INSTALL_TARGETS+=$(JSDOC_TARGET)
