#:[i18n]
#:title = Volto i18n
#:description = Translation management for Volto frontend projects.
#:depends = volto.core
#:
#:[target.volto-i18n]
#:description = Sync i18n translations for the Volto addon.
#:
#:[target.volto-ci-i18n]
#:description = Check that i18n translations are in sync (fails if not).

##############################################################################
# volto i18n
##############################################################################

.PHONY: volto-i18n
volto-i18n: $(VOLTO_TARGET)
	@echo "Sync Volto i18n"
	@pnpm --filter $(VOLTO_ADDON_NAME) i18n

.PHONY: volto-ci-i18n
volto-ci-i18n: $(VOLTO_TARGET)
	@echo "Check Volto i18n sync"
	@pnpm --filter $(VOLTO_ADDON_NAME) i18n && \
		git diff -G'^[^"POT]' --exit-code

.PHONY: i18n
i18n: volto-i18n
