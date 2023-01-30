#:[coverage]
#:title = Coverage
#:description = Project coverage testing.
#:depends = core.packages
#:
#:[target.coverage]
#:description = Run project coverage. :ref:`run-coverage` template can be
#:  used for automatic coverage script creation.
#:
#:[target.coverage-clean]
#:description = Remove coverage related files and directories.
#:
#:[setting.COVERAGE_COMMAND]
#:description = The command which gets executed. Defaults to the location the
#:  :ref:`run-coverage` template gets rendered to if configured.
#:default = $(SCRIPTS_FOLDER)/run-coverage.sh

##############################################################################
# coverage
##############################################################################

COVERAGE_TARGET:=$(SENTINEL_FOLDER)/coverage.sentinel
$(COVERAGE_TARGET): $(MXENV_TARGET)
	@echo "Install Coverage"
	@$(MXENV_PATH)pip install -U coverage
	@touch $(COVERAGE_TARGET)

.PHONY: coverage
coverage: $(FILES_TARGET) $(SOURCES_TARGET) $(PACKAGES_TARGET) $(COVERAGE_TARGET)
	@echo "Run coverage"
	@test -z "$(COVERAGE_COMMAND)" && echo "No coverage command defined"
	@test -z "$(COVERAGE_COMMAND)" || bash -c "$(COVERAGE_COMMAND)"

.PHONY: coverage-dirty
coverage-dirty:
	@rm -f $(COVERAGE_TARGET)

.PHONY: coverage-clean
coverage-clean: coverage-dirty
	@rm -rf .coverage htmlcov

INSTALL_TARGETS+=$(COVERAGE_TARGET)
DIRTY_TARGETS+=coverage-dirty
CLEAN_TARGETS+=coverage-clean
QA_TARGETS+=coverage
