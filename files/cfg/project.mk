###############################################################################
# Project specific make file. Gets included if present.
###############################################################################

## Includes of other makefiles goes here
#include $(CONFIG_FOLDER)/<file>.mk

###############################################################################
# Project specific settings
###############################################################################

## Target specific setting overrides goes here
## See ``mxenv`` documentation for details.

## ``venv`` target
#PYTHON=python3
#VENV_FOLDER=venv

## ``files`` target
#SCRIPTS_FOLDER=$(VENV_FOLDER)/bin

## ``files`` and ``sources`` targets
#PROJECT_CONFIG=mxdev.ini

## ``system-dependencie``s target
#SYSTEM_DEPENDENCIES=package-a package-b

## ``docs`` target
#DOCS_BIN=$(VENV_FOLDER)/bin/sphinx-build
#DOCS_SOURCE=docs/source
#DOCS_TARGET=docs/html

## ``clean`` target
#CLEAN_TARGETS=file-or-folder-a file-or-folder-b

###############################################################################
# Project specific targets
###############################################################################

## Project specific targets are usually prefixed with ``project-``.

#.PHONY: project-install
#project-install: <target>
#	@echo "Install project"
