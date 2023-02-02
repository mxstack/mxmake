#:[npm]
#:title = Node Package Manager
#:description = Provide targets for working with Node Package Manager
#:depends = core.base
#:
#:[target.npm]
#:description = Installs packages with NPM.
#:
#:[target.npm-dirty]
#:description = Build :ref:`npm` target on next make run.
#:
#:[target.npm-clean]
#:description = Remove installed npm packages.
#:
#:[setting.NPM_PREFIX]
#:description = Value for `--prefix` option.
#:default = .
#:
#:[setting.NPM_PACKAGES]
#:description = Packages which get installed with `--no-save` option.
#:default =
#:
#:[setting.NPM_DEV_PACKAGES]
#:description = Packages which get installed with `--save-dev` option.
#:default =
#:
#:[setting.NPM_PROD_PACKAGES]
#:description = Packages which get installed with `--save-prod` option.
#:default =
#:
#:[setting.NPM_OPT_PACKAGES]
#:description = Packages which get installed with `--save-optional` option.
#:default =
#:
#:[setting.NPM_INSTALL_OPTS]
#:description = Additional install options. Possible values are `--save-exact`
#:  and `--save-bundle`.
#:default =

##############################################################################
# npm
##############################################################################

# case `system.dependencies` domain is included
SYSTEM_DEPENDENCIES+=npm

NPM_TARGET:=$(SENTINEL_FOLDER)/npm.sentinel
$(NPM_TARGET): $(SENTINEL)
	@echo "Install npm packages"
ifneq ("$(NPM_PACKAGES)"", "")
	@npm install --prefix $(NPM_PREFIX) --no-save install $(NPM_PACKAGES)
endif
ifneq ("$(NPM_DEV_PACKAGES)"", "")
	@npm install --prefix $(NPM_PREFIX) --save-dev $(NPM_INSTALL_OPTS) install $(NPM_DEV_PACKAGES)
endif
ifneq ("$(NPM_PROD_PACKAGES)"", "")
	@npm install --prefix $(NPM_PREFIX) --save-prod $(NPM_INSTALL_OPTS) install $(NPM_PROD_PACKAGES)
endif
ifneq ("$(NPM_OPT_PACKAGES)"", "")
	@npm install --prefix $(NPM_PREFIX) --save-optional $(NPM_INSTALL_OPTS) install $(NPM_OPT_PACKAGES)
endif
	@touch $(NPM_TARGET)

.PHONY: npm
npm: $(NPM_TARGET)

.PHONY: npm-dirty
npm-dirty:
	@rm -f $(NPM_TARGET)

.PHONY: npm-clean
npm-clean: npm-dirty
	@rm -rf $(NPM_PREFIX)/node_modules

INSTALL_TARGETS+=npm
DIRTY_TARGETS+=npm-dirty
CLEAN_TARGETS+=npm-clean
