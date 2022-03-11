###############################################################################
# Makefile for mxenv projects.
###############################################################################

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

PYTHON?=python3
VENV_FOLDER?=venv
PIP_BIN:=$(VENV_FOLDER)/bin/pip
#MXDEV?=mxdev
MXDEV?=https://github.com/bluedynamics/mxdev/archive/master.zip
#MVENV?=mxenv
MVENV?=https://github.com/conestack/mxenv/archive/master.zip

VENV_SENTINEL:=$(SENTINEL_FOLDER)/venv.sentinel
$(VENV_SENTINEL): $(SENTINEL)
	@echo "Setup Python Virtual Environment under '$(VENV_FOLDER)'"
	@$(PYTHON) -m venv $(VENV_FOLDER)
	@$(PIP_BIN) install -U pip setuptools wheel
	@$(PIP_BIN) install -U $(MXDEV)
	@$(PIP_BIN) install -U $(MVENV)
	@touch $(VENV_SENTINEL)

.PHONY: venv
venv: $(VENV_SENTINEL)

.PHONY: venv-dirty
venv-dirty:
	@rm -f $(VENV_SENTINEL)

.PHONY: venv-clean
venv-clean: venv-dirty
	@rm -rf $(VENV_FOLDER)

###############################################################################
# files
###############################################################################

PROJECT_CONFIG?=mxdev.ini
SCRIPTS_FOLDER?=$(VENV_FOLDER)/bin
CONFIG_FOLDER?=cfg

FILES_SENTINEL:=$(SENTINEL_FOLDER)/files.sentinel
$(FILES_SENTINEL): $(PROJECT_CONFIG) $(VENV_SENTINEL)
	@echo "Create project files"
	@export MXENV_VENV_FOLDER=$(VENV_FOLDER)
	@export MXENV_SCRIPTS_FOLDER=$(SCRIPTS_FOLDER)
	@export MXENV_CONFIG_FOLDER=$(CONFIG_FOLDER)
	@$(VENV_FOLDER)/bin/mxdev -n -c $(PROJECT_CONFIG)
	@unset MXENV_VENV_FOLDER
	@unset MXENV_SCRIPTS_FOLDER
	@unset MXENV_CONFIG_FOLDER
	@touch $(FILES_SENTINEL)

.PHONY: files
files: $(FILES_SENTINEL)

.PHONY: files-dirty
files-dirty:
	@rm -f $(FILES_SENTINEL)

.PHONY: files-clean
files-clean: files-dirty
	@rm -f $(TEST_SCRIPT) $(COVERAGE_SCRIPT) \
		constraints-mxdev.txt requirements-mxdev.txt

###############################################################################
# sources
###############################################################################

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

###############################################################################
# install
###############################################################################

PIP_PACKAGES=.installed.txt

INSTALL_SENTINEL:=$(SENTINEL_FOLDER)/install.sentinel
$(INSTALL_SENTINEL): $(SOURCES_SENTINEL)
	@echo "Install python packages"
	@$(PIP_BIN) install -r requirements-mxdev.txt
	@$(PIP_BIN) freeze > $(PIP_PACKAGES)
	@touch $(INSTALL_SENTINEL)

.PHONY: install
install: $(INSTALL_SENTINEL)

.PHONY: install-dirty
install-dirty:
	@rm -f $(INSTALL_SENTINEL)

###############################################################################
# system dependencies
###############################################################################

SYSTEM_DEPENDENCIES?=

.PHONY: system-dependencies
system-dependencies:
	@echo "Install system dependencies"
	@test -z "$(SYSTEM_DEPENDENCIES)" && echo "No System dependencies defined"
	@test -z "$(SYSTEM_DEPENDENCIES)" || sudo apt-get install -y $(SYSTEM_DEPENDENCIES)

###############################################################################
# docs
###############################################################################

DOCS_BIN?=$(VENV_FOLDER)/bin/sphinx-build
DOCS_SOURCE?=docs/source
DOCS_TARGET?=docs/html

.PHONY: docs
docs:
	@echo "Build sphinx docs"
	@test -e $(DOCS_BIN) && $(DOCS_BIN) $(DOCS_SOURCE) $(DOCS_TARGET)
	@test -e $(DOCS_BIN) || echo "Sphinx binary not exists"

.PHONY: docs-clean
docs-clean:
	@rm -rf $(DOCS_TARGET)

###############################################################################
# test
###############################################################################

TEST_SCRIPT=$(SCRIPTS_FOLDER)/run-tests.sh

.PHONY: test
test: $(FILES_SENTINEL) $(SOURCES_SENTINEL) $(INSTALL_SENTINEL)
	@echo "Run tests"
	@test -e $(TEST_SCRIPT) && $(TEST_SCRIPT)
	@test -e $(TEST_SCRIPT) || echo "Test script not exists"

###############################################################################
# coverage
###############################################################################

COVERAGE_SCRIPT=$(SCRIPTS_FOLDER)/run-coverage.sh

.PHONY: coverage
coverage: $(FILES_SENTINEL) $(SOURCES_SENTINEL) $(INSTALL_SENTINEL)
	@echo "Run coverage"
	@test -e $(COVERAGE_SCRIPT) && $(COVERAGE_SCRIPT)
	@test -e $(COVERAGE_SCRIPT) || echo "Coverage script not exists"

.PHONY: coverage-clean
coverage-clean:
	@rm -rf .coverage htmlcov

###############################################################################
# clean
###############################################################################

CLEAN_TARGETS?=

.PHONY: clean
clean: venv-clean files-clean docs-clean coverage-clean
	@rm -rf $(CLEAN_TARGETS) .sentinels .installed.txt

.PHONY: full-clean
full-clean: clean sources-clean

###############################################################################
# Include custom make files
###############################################################################

-include $(CONFIG_FOLDER)/project.mk
