#:[coverage]
#:title = Coverage
#:description = Project coverage testing.
#:depends = install
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

###############################################################################
# coverage
###############################################################################

COVERAGE_COMMAND?=$(SCRIPTS_FOLDER)/run-coverage.sh

.PHONY: coverage
coverage: $(FILES_SENTINEL) $(SOURCES_SENTINEL) $(INSTALL_SENTINEL)
	@echo "Run coverage"
	@test -z "$(COVERAGE_COMMAND)" && echo "No coverage command defined"
	@test -z "$(COVERAGE_COMMAND)" || bash -c "$(COVERAGE_COMMAND)"

.PHONY: coverage-clean
coverage-clean:
	@rm -rf .coverage htmlcov
