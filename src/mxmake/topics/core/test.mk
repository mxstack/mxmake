#:[test]
#:title = Test
#:description = Project testing.
#:depends = core.install
#:
#:[target.test]
#:description = Run project tests. The :ref:`run-tests` template can be used
#:  for automatic test script creation.
#:
#:[setting.TEST_COMMAND]
#:description = The command which gets executed. Defaults to the location the
#:  :ref:`run-tests` template gets rendered to if configured.
#:default = $(SCRIPTS_FOLDER)/run-tests.sh
#:
#:[setting.TEST_DEPENDENCY_TARGETS]
#:description = Additional make targets the test target depends on.
#:default =

##############################################################################
# test
##############################################################################

.PHONY: test
test: $(FILES_SENTINEL) $(SOURCES_SENTINEL) $(INSTALL_SENTINEL) $(TEST_DEPENDENCY_TARGETS)
	@echo "Run tests"
	@test -z "$(TEST_COMMAND)" && echo "No test command defined"
	@test -z "$(TEST_COMMAND)" || bash -c "$(TEST_COMMAND)"
