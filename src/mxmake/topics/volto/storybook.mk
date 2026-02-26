#:[storybook]
#:title = Volto Storybook
#:description = Storybook integration for Volto component development.
#:depends = volto.core
#:
#:[target.volto-storybook-start]
#:description = Start Storybook development server on port 6006.
#:
#:[target.volto-storybook-build]
#:description = Build static Storybook site.
#:
#:[setting.VOLTO_STORYBOOK_PORT]
#:description = Port for Storybook development server.
#:default = 6006

##############################################################################
# volto storybook
##############################################################################

VOLTO_STORYBOOK_BUILD_DIR?=$(CURRENT_DIR)/.storybook-build

.PHONY: volto-storybook-start
volto-storybook-start: $(VOLTO_TARGET)
	@echo "Start Volto Storybook"
	@pnpm run storybook

.PHONY: volto-storybook-build
volto-storybook-build: $(VOLTO_TARGET)
	@echo "Build Volto Storybook"
	@mkdir -p $(VOLTO_STORYBOOK_BUILD_DIR)
	@pnpm run storybook-build -o $(VOLTO_STORYBOOK_BUILD_DIR)
