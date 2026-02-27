#:[lint]
#:title = Volto Lint
#:description = Code linting and formatting for Volto frontend projects.
#:  Runs ESLint, Prettier, and Stylelint via pnpm scripts.
#:depends = volto.core
#:
#:[target.volto-lint]
#:description = Run ESLint, Prettier, and Stylelint checks.
#:
#:[target.volto-format]
#:description = Run ESLint, Prettier, and Stylelint with auto-fix.

##############################################################################
# volto lint
##############################################################################

.PHONY: volto-lint
volto-lint: $(VOLTO_TARGET)
	@echo "Run Volto lint checks"
	@pnpm lint
	@pnpm prettier
	@pnpm stylelint --allow-empty-input

.PHONY: volto-format
volto-format: $(VOLTO_TARGET)
	@echo "Run Volto format"
	@pnpm lint:fix
	@pnpm prettier:fix
	@pnpm stylelint:fix

CHECK_TARGETS+=volto-lint
FORMAT_TARGETS+=volto-format
