###############################################################################
# Project specific make file. Gets included if present.
###############################################################################

## Includes of other makefiles goes here
#include $(INCLUDE_FOLDER)/<file>.mk

###############################################################################
# Project specific settings
###############################################################################

## Target specific setting overrides goes here
## See ``mxmake`` documentation for details.

## ``venv`` target
#HOST_PYTHON=python3
#VENV_FOLDER=venv

## ``files`` target
#SCRIPTS_FOLDER=$(VENV_FOLDER)/bin
#CONFIG_FOLDER=cfg

## ``files`` and ``sources`` targets
#PROJECT_CONFIG=mx.ini

## ``system-dependencie``s target
#SYSTEM_DEPENDENCIES+=package-a package-b

## ``docs`` target
#DOCS_BIN=$(VENV_FOLDER)/bin/sphinx-build
#DOCS_SOURCE=docs/source
#DOCS_TARGET=docs/html

## ``test`` target
#TEST_COMMAND=$(SCRIPTS_FOLDER)/run-tests.sh

## ``coverage`` target
#COVERAGE_COMMAND=$(SCRIPTS_FOLDER)/run-coverage.sh

## ``clean`` target
#CLEAN_TARGETS+=file-or-folder-a file-or-folder-b

###############################################################################
# Project specific targets
###############################################################################

## Project specific targets are usually prefixed with ``project-``.

#.PHONY: project-install
#project-install: <target>
#	@echo "Install project"
