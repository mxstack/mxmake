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

export PATH:=$(shell pwd)/$(NPM_PREFIX)/node_modules/.bin:$(PATH)

# case `system.dependencies` domain is included
SYSTEM_DEPENDENCIES+=npm

NPM_TARGET:=$(SENTINEL_FOLDER)/npm.sentinel
$(NPM_TARGET): $(SENTINEL)
	@echo "Install npm packages"
	@test -z "$(NPM_DEV_PACKAGES)" \
		&& echo "No dev packages to be installed" \
		|| npm --prefix $(NPM_PREFIX) install \
			--save-dev \
			$(NPM_INSTALL_OPTS) \
			$(NPM_DEV_PACKAGES)
	@test -z "$(NPM_PROD_PACKAGES)" \
		&& echo "No prod packages to be installed" \
		|| npm --prefix $(NPM_PREFIX) install \
			--save-prod \
			$(NPM_INSTALL_OPTS) \
			$(NPM_PROD_PACKAGES)
	@test -z "$(NPM_OPT_PACKAGES)" \
		&& echo "No opt packages to be installed" \
		|| npm --prefix $(NPM_PREFIX) install \
			--save-optional \
			$(NPM_INSTALL_OPTS) \
			$(NPM_OPT_PACKAGES)
	@test -z "$(NPM_PACKAGES)" \
		&& echo "No packages to be installed" \
		|| npm --prefix $(NPM_PREFIX) install \
			--no-save \
			$(NPM_PACKAGES)
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
