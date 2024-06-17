#:[nodejs]
#:title = Node.js
#:description = Provide targets for working with Node.js. A working version of
#:  Node.js is expected to be installed. We suggest using `nvm` for managing
#:  Node.JS installations.
#:depends = core.base
#:
#:[target.nodejs]
#:description = Installs Javascript packages using the current active node
#:  version with the configured package manager.
#:
#:[target.nodejs-dirty]
#:description = Build :ref:`nodejs` target on next make run.
#:
#:[target.nodejs-clean]
#:description = Remove installed Javascript packages.
#:
#:[setting.NODEJS_PACKAGE_MANAGER]
#:description = The package manager to use. Defaults to `npm`. Possible values
#:  are `npm` and `pnpm`
#:default = npm
#:
#:[setting.NODEJS_PREFIX]
#:description = Value for `--prefix` option when installing packages.
#:default = .
#:
#:[setting.NODEJS_PACKAGES]
#:description = Packages to install with `--no-save` option.
#:default =
#:
#:[setting.NODEJS_DEV_PACKAGES]
#:description = Packages to install with `--save-dev` option.
#:default =
#:
#:[setting.NODEJS_PROD_PACKAGES]
#:description = Packages to install with `--save-prod` option.
#:default =
#:
#:[setting.NODEJS_OPT_PACKAGES]
#:description = Packages to install with `--save-optional` option.
#:default =
#:
#:[setting.NODEJS_INSTALL_OPTS]
#:description = Additional install options. Possible values are `--save-exact`
#:  and `--save-bundle`.
#:default =

##############################################################################
# nodejs
##############################################################################

export PATH:=$(shell pwd)/$(NODEJS_PREFIX)/node_modules/.bin:$(PATH)


NODEJS_TARGET:=$(SENTINEL_FOLDER)/nodejs.sentinel
$(NODEJS_TARGET): $(SENTINEL)
	@echo "Install nodejs packages"
	@test -z "$(NODEJS_DEV_PACKAGES)" \
		&& echo "No dev packages to be installed" \
		|| $(NODEJS_PACKAGE_MANAGER) --prefix $(NODEJS_PREFIX) install \
			--save-dev \
			$(NODEJS_INSTALL_OPTS) \
			$(NODEJS_DEV_PACKAGES)
	@test -z "$(NODEJS_PROD_PACKAGES)" \
		&& echo "No prod packages to be installed" \
		|| $(NODEJS_PACKAGE_MANAGER) --prefix $(NODEJS_PREFIX) install \
			--save-prod \
			$(NODEJS_INSTALL_OPTS) \
			$(NODEJS_PROD_PACKAGES)
	@test -z "$(NODEJS_OPT_PACKAGES)" \
		&& echo "No opt packages to be installed" \
		|| $(NODEJS_PACKAGE_MANAGER) --prefix $(NODEJS_PREFIX) install \
			--save-optional \
			$(NODEJS_INSTALL_OPTS) \
			$(NODEJS_OPT_PACKAGES)
	@test -z "$(NODEJS_PACKAGES)" \
		&& echo "No packages to be installed" \
		|| $(NODEJS_PACKAGE_MANAGER) --prefix $(NODEJS_PREFIX) install \
			--no-save \
			$(NODEJS_PACKAGES)
	@touch $(NODEJS_TARGET)

.PHONY: nodejs
nodejs: $(NODEJS_TARGET)

.PHONY: nodejs-dirty
nodejs-dirty:
	@rm -f $(NODEJS_TARGET)

.PHONY: nodejs-clean
nodejs-clean: nodejs-dirty
	@rm -rf $(NODEJS_PREFIX)/node_modules

INSTALL_TARGETS+=nodejs
DIRTY_TARGETS+=nodejs-dirty
CLEAN_TARGETS+=nodejs-clean
