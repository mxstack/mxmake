#:[jsdoc]
#:title = JSDoc Documentation
#:description = JSDoc installation and integration into Sphinx.
#:depends = js.npm

##############################################################################
# jsdoc
##############################################################################

# extend npm dev packages
NPM_DEV_PACKAGES+=jsdoc

# extend sphinx requirements and docs targets
DOCS_REQUIREMENTS+=sphinx_js
