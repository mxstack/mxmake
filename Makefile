##############################################################################
# THIS FILE IS GENERATED BY MXMAKE
#
# SETTINGS (ALL CHANGES MADE BELOW SETTINGS WILL BE LOST)
##############################################################################

## core.venv

# Python interpreter to use for creating the virtual environment.
# default: python3
PYTHON_BIN?=python3

# The folder where the virtual environment get created.
# default: venv
VENV_FOLDER?=venv

# mxdev to install in virtual environment.
# default: https://github.com/mxstack/mxdev/archive/main.zip
MXDEV?=https://github.com/mxstack/mxdev/archive/main.zip

# mxmake to install in virtual environment.
# default: https://github.com/mxstack/mxmake/archive/inquirer-sandbox.zip
MXMAKE?=-e .[docs]

## core.files

# The config file to use.
# default: mx.ini
PROJECT_CONFIG?=mx.ini

# Target folder for generated scripts.
# default: $(VENV_FOLDER)/bin
SCRIPTS_FOLDER?=$(VENV_FOLDER)/bin

# Target folder for generated config files.
# default: cfg
CONFIG_FOLDER?=cfg

## core.test

# The command which gets executed. Defaults to the location the
# :ref:`run-tests` template gets rendered to if configured.
# default: $(SCRIPTS_FOLDER)/run-tests.sh
TEST_COMMAND?=$(VENV_FOLDER)/bin/python setup.py test

# Additional make targets the test target depends on.
# default: 
TEST_DEPENDENCY_TARGETS?=

## core.coverage

# The command which gets executed. Defaults to the location the
# :ref:`run-coverage` template gets rendered to if configured.
# default: $(SCRIPTS_FOLDER)/run-coverage.sh
COVERAGE_COMMAND?=

## core.clean

# Space separated list of files and folders to remove.
# default: 
CLEAN_TARGETS?=dist mxmake.egg-info

## core.docs

# The Sphinx build executable.
# default: $(VENV_FOLDER)/bin/sphinx-build
DOCS_BIN?=$(VENV_FOLDER)/bin/sphinx-build

# Documentation source folder.
# default: docs/source
DOCS_SOURCE?=docs/source

# Documentation generation target folder.
# default: docs/html
DOCS_TARGET?=docs/html

## core.system-dependencies

# Space separated system package names.
# default: 
SYSTEM_DEPENDENCIES?=


##############################################################################
# Makefile for mxmake projects.
##############################################################################

# Defensive settings for make: https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
# for Makefile debugging purposes add -x to the .SHELLFLAGS
.SHELLFLAGS:=-eu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# Sentinel files
SENTINEL_FOLDER?=.sentinels
SENTINEL?=$(SENTINEL_FOLDER)/about.txt
$(SENTINEL):
	@mkdir -p $(SENTINEL_FOLDER)
	@echo "Sentinels for the Makefile process." > $(SENTINEL)

##############################################################################
# venv
##############################################################################

VENV_SENTINEL:=$(SENTINEL_FOLDER)/venv.sentinel
$(VENV_SENTINEL): $(SENTINEL)
	@echo "Setup Python Virtual Environment under '$(VENV_FOLDER)'"
	@$(PYTHON_BIN) -m venv $(VENV_FOLDER)
	@$(VENV_FOLDER)/bin/pip install -U pip setuptools wheel
	@$(VENV_FOLDER)/bin/pip install -U $(MXDEV)
	@$(VENV_FOLDER)/bin/pip install -U $(MXMAKE)
	@touch $(VENV_SENTINEL)

.PHONY: venv
venv: $(VENV_SENTINEL)

.PHONY: venv-dirty
venv-dirty:
	@rm -f $(VENV_SENTINEL)

.PHONY: venv-clean
venv-clean: venv-dirty
	@rm -rf $(VENV_FOLDER)

##############################################################################
# files
##############################################################################

# set environment variables for mxmake
define set_files_env
	@export MXMAKE_VENV_FOLDER=$(1)
	@export MXMAKE_SCRIPTS_FOLDER=$(2)
	@export MXMAKE_CONFIG_FOLDER=$(3)
endef

# unset environment variables for mxmake
define unset_files_env
	@unset MXMAKE_VENV_FOLDER
	@unset MXMAKE_SCRIPTS_FOLDER
	@unset MXMAKE_CONFIG_FOLDER
endef

FILES_SENTINEL:=$(SENTINEL_FOLDER)/files.sentinel
$(FILES_SENTINEL): $(PROJECT_CONFIG) $(VENV_SENTINEL)
	@echo "Create project files"
	$(call set_files_env,$(VENV_FOLDER),$(SCRIPTS_FOLDER),$(CONFIG_FOLDER))
	@$(VENV_FOLDER)/bin/mxdev -n -c $(PROJECT_CONFIG)
	$(call unset_files_env,$(VENV_FOLDER),$(SCRIPTS_FOLDER),$(CONFIG_FOLDER))
	@touch $(FILES_SENTINEL)

.PHONY: files
files: $(FILES_SENTINEL)

.PHONY: files-dirty
files-dirty:
	@rm -f $(FILES_SENTINEL)

.PHONY: files-clean
files-clean: files-dirty
	$(call set_files_env,$(VENV_FOLDER),$(SCRIPTS_FOLDER),$(CONFIG_FOLDER))
	@test -e $(VENV_FOLDER)/bin/mxmake && \
		$(VENV_FOLDER)/bin/mxmake clean -c $(PROJECT_CONFIG)
	$(call unset_files_env,$(VENV_FOLDER),$(SCRIPTS_FOLDER),$(CONFIG_FOLDER))
	@rm -f constraints-mxdev.txt requirements-mxdev.txt

##############################################################################
# sources
##############################################################################

SOURCES_SENTINEL:=$(SENTINEL_FOLDER)/sources.sentinel
$(SOURCES_SENTINEL): $(FILES_SENTINEL)
	@echo "Checkout project sources"
	@$(VENV_FOLDER)/bin/mxdev -o -c $(PROJECT_CONFIG)
	@touch $(SOURCES_SENTINEL)

.PHONY: sources
sources: $(SOURCES_SENTINEL)

.PHONY: sources-dirty
sources-dirty:
	@rm -f $(SOURCES_SENTINEL)

.PHONY: sources-clean
sources-clean: sources-dirty
	@rm -rf sources

##############################################################################
# install
##############################################################################

INSTALLED_PACKAGES=.installed.txt

INSTALL_SENTINEL:=$(SENTINEL_FOLDER)/install.sentinel
$(INSTALL_SENTINEL): $(SOURCES_SENTINEL)
	@echo "Install python packages"
	@$(VENV_FOLDER)/bin/pip install -r requirements-mxdev.txt
	@$(VENV_FOLDER)/bin/pip freeze > $(INSTALLED_PACKAGES)
	@touch $(INSTALL_SENTINEL)

.PHONY: install
install: $(INSTALL_SENTINEL)

.PHONY: install-dirty
install-dirty:
	@rm -f $(INSTALL_SENTINEL)

##############################################################################
# test
##############################################################################

.PHONY: test
test: $(FILES_SENTINEL) $(SOURCES_SENTINEL) $(INSTALL_SENTINEL) $(TEST_DEPENDENCY_TARGETS)
	@echo "Run tests"
	@test -z "$(TEST_COMMAND)" && echo "No test command defined"
	@test -z "$(TEST_COMMAND)" || bash -c "$(TEST_COMMAND)"

##############################################################################
# coverage
##############################################################################

.PHONY: coverage
coverage: $(FILES_SENTINEL) $(SOURCES_SENTINEL) $(INSTALL_SENTINEL)
	@echo "Run coverage"
	@test -z "$(COVERAGE_COMMAND)" && echo "No coverage command defined"
	@test -z "$(COVERAGE_COMMAND)" || bash -c "$(COVERAGE_COMMAND)"

.PHONY: coverage-clean
coverage-clean:
	@rm -rf .coverage htmlcov

##############################################################################
# clean
##############################################################################

.PHONY: clean
clean: files-clean venv-clean docs-clean coverage-clean
	@rm -rf $(CLEAN_TARGETS) .sentinels .installed.txt

.PHONY: full-clean
full-clean: clean sources-clean

.PHONY: runtime-clean
runtime-clean:
	@echo "Remove runtime artifacts, like byte-code and caches."
	@find . -name '*.py[c|o]' -delete
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

##############################################################################
# docs
##############################################################################

.PHONY: docs
docs:
	@echo "Build sphinx docs"
	@test -e $(DOCS_BIN) && $(DOCS_BIN) $(DOCS_SOURCE) $(DOCS_TARGET)
	@test -e $(DOCS_BIN) || echo "Sphinx binary not exists"

.PHONY: docs-clean
docs-clean:
	@rm -rf $(DOCS_TARGET)

##############################################################################
# system dependencies
##############################################################################

.PHONY: system-dependencies
system-dependencies:
	@echo "Install system dependencies"
	@test -z "$(SYSTEM_DEPENDENCIES)" && echo "No System dependencies defined"
	@test -z "$(SYSTEM_DEPENDENCIES)" \
		|| sudo apt-get install -y $(SYSTEM_DEPENDENCIES)

##############################################################################
#: core.base
#: core.venv
#: core.files
#: core.sources
#: core.install
#: core.test
#: core.coverage
#: core.clean
#: core.docs
#: core.system-dependencies
##############################################################################