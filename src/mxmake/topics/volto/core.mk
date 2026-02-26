#:[core]
#:title = Volto Core
#:description = Plone Volto frontend project setup. Provides targets for
#:  installing, starting, building, and cleaning a Volto project using pnpm
#:  workspaces and mrs-developer.
#:depends = core.base
#:
#:[target.volto-install]
#:description = Install Volto frontend packages using pnpm and mrs-developer.
#:
#:[target.volto-build-deps]
#:description = Build Volto workspace dependencies (@plone/registry,
#:  @plone/components).
#:
#:[target.volto-start]
#:description = Start Volto development server with hot reload.
#:
#:[target.volto-build]
#:description = Build production bundle.
#:
#:[target.volto-dirty]
#:description = Build :ref:`volto-install` target on next make run.
#:
#:[target.volto-clean]
#:description = Remove installed packages and cloned Volto core.
#:
#:[setting.VOLTO_ADDON_NAME]
#:description = The pnpm package name of the Volto addon in this project.
#:  Used for ``pnpm --filter`` commands.
#:default =
#:
#:[setting.VOLTO_MRS_DEVELOPER_PARAMS]
#:description = Additional parameters for ``mrs-developer missdev``.
#:default = --no-config --fetch-https

##############################################################################
# volto core
##############################################################################

CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

VOLTO_TARGET:=$(SENTINEL_FOLDER)/volto.sentinel
$(VOLTO_TARGET): $(SENTINEL) package.json mrs.developer.json
	@echo "Install Volto frontend packages"
	@pnpm dlx mrs-developer missdev $(VOLTO_MRS_DEVELOPER_PARAMS)
	@pnpm install
	@touch $(VOLTO_TARGET)

.PHONY: volto-install
volto-install: $(VOLTO_TARGET)

.PHONY: volto-build-deps
volto-build-deps: $(VOLTO_TARGET)
	@echo "Build Volto workspace dependencies"
	@pnpm --filter @plone/registry build
	@pnpm --filter @plone/components build

.PHONY: volto-start
volto-start: $(VOLTO_TARGET)
	@echo "Start Volto development server"
	@pnpm start

.PHONY: volto-build
volto-build: $(VOLTO_TARGET) volto-build-deps
	@echo "Build Volto production bundle"
	@pnpm build

.PHONY: volto-dirty
volto-dirty:
	@rm -f $(VOLTO_TARGET)

.PHONY: volto-clean
volto-clean: volto-dirty
	@rm -rf core node_modules

INSTALL_TARGETS+=volto-install
RUN_TARGET?=volto-start
DIRTY_TARGETS+=volto-dirty
CLEAN_TARGETS+=volto-clean
