#:[test]
#:title = Volto Test
#:description = Unit testing for Volto frontend projects using Jest.
#:depends = volto.core
#:
#:[target.volto-test]
#:description = Run Volto unit tests.
#:
#:[target.volto-ci-test]
#:description = Run Volto unit tests in CI mode with i18n pre-build and
#:  jest addon configuration.
#:
#:[setting.VOLTO_TEST_COMMAND]
#:description = Command to run Volto unit tests.
#:default = pnpm test

##############################################################################
# volto test
##############################################################################

.PHONY: volto-test
volto-test: $(VOLTO_TARGET)
	@echo "Run Volto unit tests"
	@$(VOLTO_TEST_COMMAND)

.PHONY: volto-ci-test
volto-ci-test: $(VOLTO_TARGET)
	@echo "Run Volto CI unit tests"
	@VOLTOCONFIG=$(CURRENT_DIR)/volto.config.js \
		pnpm --filter @plone/volto i18n
	@CI=1 RAZZLE_JEST_CONFIG=$(CURRENT_DIR)/jest-addon.config.js \
		pnpm run --filter @plone/volto test --passWithNoTests

.PHONY: test
test: volto-test
