#:[test]
#:title = Test
#:description = Project testing.
#:depends = core.packages
#:
#:[target.test]
#:description = Run project tests. The :ref:`run-tests` template can be used
#:  for automatic test script creation.
#:
#:[setting.TEST_COMMAND]
#:description = The command which gets executed. Defaults to the location the
#:  :ref:`run-tests` template gets rendered to if configured.
#:default = .mxmake/files/run-tests.sh
#:
#:[setting.TEST_REQUIREMENTS]
#:description = Additional Python requirements for running tests to be
#:  installed (via pip).
#:default = pytest
#:
#:[setting.TEST_DEPENDENCY_TARGETS]
#:description = Additional make targets the test target depends on.
#:default =

##############################################################################
# test
##############################################################################

TEST_TARGET:=$(SENTINEL_FOLDER)/test.sentinel
$(TEST_TARGET): $(MXENV_TARGET)
	@echo "Install $(TEST_REQUIREMENTS)"
	@$(PYTHON_PACKAGE_COMMAND) install $(TEST_REQUIREMENTS)
	@touch $(TEST_TARGET)

.PHONY: test
test: $(FILES_TARGET) $(SOURCES_TARGET) $(PACKAGES_TARGET) $(TEST_TARGET) $(TEST_DEPENDENCY_TARGETS)
	@test -z "$(TEST_COMMAND)" && echo "No test command defined" && exit 1 || :
	@echo "Run tests using $(TEST_COMMAND)"
	@/usr/bin/env bash -c "$(TEST_COMMAND)"

.PHONY: test-dirty
test-dirty:
	@rm -f $(TEST_TARGET)

.PHONY: test-clean
test-clean: test-dirty
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y $(TEST_REQUIREMENTS) || :
	@rm -rf .pytest_cache

INSTALL_TARGETS+=$(TEST_TARGET)
CLEAN_TARGETS+=test-clean
DIRTY_TARGETS+=test-dirty
