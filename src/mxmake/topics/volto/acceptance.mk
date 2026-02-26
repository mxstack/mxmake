#:[acceptance]
#:title = Volto Acceptance
#:description = Acceptance testing for Volto projects using Cypress.
#:depends = volto.core
#:
#:[target.volto-acceptance-backend-start]
#:description = Start Docker-based Plone acceptance backend.
#:
#:[target.volto-acceptance-frontend-dev-start]
#:description = Start acceptance frontend in development mode.
#:
#:[target.volto-acceptance-test]
#:description = Run Cypress acceptance tests in interactive mode.
#:
#:[target.volto-ci-acceptance-test]
#:description = Run Cypress acceptance tests in headless CI mode.
#:
#:[setting.VOLTO_ACCEPTANCE_BACKEND_IMAGE]
#:description = Docker image for Plone acceptance backend.
#:default = plone/server-acceptance:6
#:
#:[setting.VOLTO_CYPRESS_CONFIG]
#:description = Path to Cypress configuration file.
#:default = cypress.config.js
#:
#:[setting.VOLTO_CYPRESS_SPEC_PATTERN]
#:description = Glob pattern for Cypress test specs.
#:default = cypress/tests/**/*.{js,jsx,ts,tsx}

##############################################################################
# volto acceptance
##############################################################################

.PHONY: volto-acceptance-backend-start
volto-acceptance-backend-start:
	@echo "Start Plone acceptance backend"
	@docker run -it --rm -p 55001:55001 $(VOLTO_ACCEPTANCE_BACKEND_IMAGE)

.PHONY: volto-acceptance-frontend-dev-start
volto-acceptance-frontend-dev-start: $(VOLTO_TARGET)
	@echo "Start acceptance frontend in development mode"
	@RAZZLE_API_PATH=http://127.0.0.1:55001/plone pnpm start

.PHONY: volto-acceptance-test
volto-acceptance-test: $(VOLTO_TARGET)
	@echo "Run Cypress acceptance tests"
	@pnpm --filter @plone/volto exec cypress open \
		--config-file $(CURRENT_DIR)/$(VOLTO_CYPRESS_CONFIG) \
		--config specPattern=$(CURRENT_DIR)'/$(VOLTO_CYPRESS_SPEC_PATTERN)'

.PHONY: volto-ci-acceptance-test
volto-ci-acceptance-test: $(VOLTO_TARGET)
	@echo "Run Cypress CI acceptance tests"
	@pnpm --filter @plone/volto exec cypress run \
		--config-file $(CURRENT_DIR)/$(VOLTO_CYPRESS_CONFIG) \
		--config specPattern=$(CURRENT_DIR)'/$(VOLTO_CYPRESS_SPEC_PATTERN)'
