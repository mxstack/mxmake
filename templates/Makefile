###############################################################################
# Makefile for mxenv projects.
###############################################################################

# Project settings
PYTHON?=python3
VENV_FOLDER?=.
PROJECT_CONFIG?=mxdev.ini

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
SENTINEL_FOLDER:=.sentinels
SENTINEL:=$(SENTINEL_FOLDER)/about.txt
$(SENTINEL):
	@mkdir -p $(SENTINEL_FOLDER)
	@echo "Sentinels for the Makefile process." > $(SENTINEL)

###############################################################################
# venv
###############################################################################

PIP_BIN:=$(VENV_FOLDER)/bin/pip
#MXDEV:=mxdev
MXDEV:=https://github.com/bluedynamics/mxdev/archive/master.zip
#MVENV:=mxenv
MVENV:=https://github.com/conestack/mxenv/archive/master.zip

VENV_SENTINEL:=$(SENTINEL_FOLDER)/venv.sentinel

.PHONY: venv
venv: $(VENV_SENTINEL)

$(VENV_SENTINEL): $(SENTINEL)
	@echo "Setup Python Virtual Environment under '$(VENV_FOLDER)'"
	@$(PYTHON) -m venv $(VENV_FOLDER)
	@$(PIP_BIN) install -U pip setuptools wheel
	@$(PIP_BIN) install $(MXDEV)
	@$(PIP_BIN) install $(MVENV)
	@touch $(VENV_SENTINEL)

###############################################################################
# files
###############################################################################

FILES_SENTINEL:=$(SENTINEL_FOLDER)/files.sentinel

.PHONY: files
files: $(FILES_SENTINEL)

$(FILES_SENTINEL): $(VENV_SENTINEL)
	@echo "Create project files"
	@$(VENV_FOLDER)/bin/mxdev -n -c $(PROJECT_CONFIG)
	@touch $(FILES_SENTINEL)

###############################################################################
# sources
###############################################################################

SOURCES_SENTINEL:=$(SENTINEL_FOLDER)/sources.sentinel

.PHONY: sources
sources: $(SOURCES_SENTINEL)

$(SOURCES_SENTINEL): $(FILES_SENTINEL)
	@echo "Checkout project sources"
	@$(VENV_FOLDER)/bin/mxdev -o -c $(PROJECT_CONFIG)
	@touch $(SOURCES_SENTINEL)

###############################################################################
# install
###############################################################################

PIP_PACKAGES=.installed.txt
CUSTOM_PIP_INSTALL=scripts/custom-pip.sh

.PHONY: install
install: $(PIP_PACKAGES)

$(PIP_PACKAGES): $(SOURCES_SENTINEL)
	@echo "Install python packages"
	@test -e $(CUSTOM_PIP_INSTALL) && echo "Run custom scripts"
	@test -e $(CUSTOM_PIP_INSTALL) && $(CUSTOM_PIP_INSTALL)
	@$(PIP_BIN) install -r requirements-mxdev.txt
	@$(PIP_BIN) freeze > $(PIP_PACKAGES)

###############################################################################
# dependencies
###############################################################################

SYSTEM_DEPS=config/system-dependencies.conf

.PHONY: dependencies
dependencies: $(SYSTEM_DEPS)

$(SYSTEM_DEPS): $(FILES_SENTINEL)
	@echo "Install system dependencies"
	@test -e $(SYSTEM_DEPS) && sudo apt-get install -y $$(cat $(SYSTEM_DEPS))
	@test -e $(SYSTEM_DEPS) && touch $(SYSTEM_DEPS)
	@test -e $(SYSTEM_DEPS) || echo "System dependencies config not exists"

###############################################################################
# docs
###############################################################################

DOCS_BIN?=bin/sphinx-build
DOCS_SOURCE?=docs/source
DOCS_TARGET?=docs/html

.PHONY: docs
docs:
	@echo "Build sphinx docs"
	@test -e $(DOCS_BIN) && $(DOCS_BIN) $(DOCS_SOURCE) $(DOCS_TARGET)
	@test -e $(DOCS_BIN) || echo "Sphinx binary not exists"

###############################################################################
# test
###############################################################################

TEST_SCRIPT=scripts/run-tests.sh

.PHONY: test
test: $(PIP_PACKAGES)
	@echo "Run tests"
	@test -e $(TEST_SCRIPT) && $(TEST_SCRIPT)
	@test -e $(TEST_SCRIPT) || echo "Test script not exists"

###############################################################################
# coverage
###############################################################################

COVERAGE_SCRIPT=scripts/run-coverage.sh

.PHONY: coverage
coverage: $(PIP_PACKAGES)
	@echo "Run coverage"
	@test -e $(COVERAGE_SCRIPT) && $(COVERAGE_SCRIPT)
	@test -e $(COVERAGE_SCRIPT) || echo "Coverage script not exists"

###############################################################################
# clean
###############################################################################

COMMON_CLEAN_TARGETS=\
    .coverage .installed.txt .sentinels bin config/custom-clean.conf \
    config/system-dependencies.conf constraints-mxdev.txt docs/html htmlcov \
    include lib lib64 openldap pyvenv.cfg requirements-mxdev.txt \
    scripts/custom-pip.sh scripts/run-coverage.sh scripts/run-tests.sh \
    share
CUSTOM_CLEAN_TARGETS=config/custom-clean.conf

.PHONY: clean
clean:
	@echo "Clean environment"
	@test -e $(CUSTOM_CLEAN_TARGETS) && rm -rf $$(cat $(CUSTOM_CLEAN_TARGETS))
	@rm -rf $(COMMON_CLEAN_TARGETS)

###############################################################################
# Include custom make files
###############################################################################

-include config/*.mk
