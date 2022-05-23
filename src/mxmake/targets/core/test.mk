#:[test]
#:title = Test
#:description = Project testing.
#:depends = install
#:
#:target.test = Run project tests. The :ref:`run-tests` template can be used
#:  for automatic test script creation.
#:
#:[TEST_COMMAND]
#:description = The command which gets executed. Defaults to the location the
#:  :ref:`run-tests` template gets rendered to if configured.
#:default = $(SCRIPTS_FOLDER)/run-tests.sh

###############################################################################
# test
###############################################################################

TEST_COMMAND?=$(SCRIPTS_FOLDER)/run-tests.sh

.PHONY: test
test: $(FILES_SENTINEL) $(SOURCES_SENTINEL) $(INSTALL_SENTINEL)
	@echo "Run tests"
	@test -z "$(TEST_COMMAND)" && echo "No test command defined"
	@test -z "$(TEST_COMMAND)" || bash -c "$(TEST_COMMAND)"
