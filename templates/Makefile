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

# Colors
# OK=Green, warn=yellow, error=red
ifeq ($(TERM),)
# no colors if not in terminal
	MARK_COLOR=
	OK_COLOR=
	WARN_COLOR=
	ERROR_COLOR=
	NO_COLOR=
else
	MARK_COLOR=`tput setaf 6`
	OK_COLOR=`tput setaf 2`
	WARN_COLOR=`tput setaf 3`
	ERROR_COLOR=`tput setaf 1`
	NO_COLOR=`tput sgr0`
endif

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
	@echo "$(OK_COLOR)Setup Python Virtual Environment under '$(VENV_FOLDER)' $(NO_COLOR)"
	@$(PYTHON) -m venv $(VENV_FOLDER)
	@$(PIP_BIN) install -U pip setuptools wheel
	@$(PIP_BIN) install $(MXDEV)
	@$(PIP_BIN) install $(MVENV)
	@touch $(VENV_SENTINEL)

###############################################################################
# mxenv
###############################################################################

MXENV_SENTINEL:=$(SENTINEL_FOLDER)/mxenv.sentinel

.PHONY: mxenv
mxenv: $(MXENV_SENTINEL)

$(MXENV_SENTINEL): $(VENV_SENTINEL) $(SENTINEL)
	@echo "$(OK_COLOR)Create project files $(NO_COLOR)"
	@$(VENV_FOLDER)/bin/mxdev -n -c $(PROJECT_CONFIG)
	@touch $(MXENV_SENTINEL)

###############################################################################
# mxdev
###############################################################################

MXDEV_SENTINEL:=$(SENTINEL_FOLDER)/mxdev.sentinel

.PHONY: mxdev
mxdev: $(MXDEV_SENTINEL)

$(MXDEV_SENTINEL): $(MXENV_SENTINEL) $(VENV_SENTINEL) $(SENTINEL)
	@echo "$(OK_COLOR)Run mxdev $(NO_COLOR)"
	@$(VENV_FOLDER)/bin/mxdev -o -c $(PROJECT_CONFIG)
	@touch $(MXDEV_SENTINEL)

###############################################################################
# pip
###############################################################################

PIP_PACKAGES=.installed.txt
CUSTOM_PIP_INSTALL=scripts/custom-pip.sh

.PHONY: pip
pip: $(PIP_PACKAGES)

$(PIP_PACKAGES): $(MXDEV_SENTINEL) $(MXENV_SENTINEL) $(VENV_SENTINEL) $(SENTINEL)
	@echo "$(OK_COLOR)Install python packages $(NO_COLOR)"
ifneq ("$(wildcard $(CUSTOM_PIP_INSTALL))","")
	@echo "$(OK_COLOR)Run custom scripts $(NO_COLOR)"
	@$(CUSTOM_PIP_INSTALL)
endif
	@$(PIP_BIN) install -r requirements-mxdev.txt
	@$(PIP_BIN) freeze > $(PIP_PACKAGES)

###############################################################################
# deps
###############################################################################

SYSTEM_DEPS=config/system-dependencies.conf

.PHONY: deps
deps: $(SYSTEM_DEPS)

$(SYSTEM_DEPS): $(MXENV_SENTINEL)
	@echo "$(OK_COLOR)Install system dependencies $(NO_COLOR)"
ifneq ("$(wildcard $(SYSTEM_DEPS))","")
	@sudo apt-get install -y $$(cat $(SYSTEM_DEPS))
	@touch $(SYSTEM_DEPS)
else
	@echo "$(ERROR_COLOR)System dependencies config not exists $(ERROR_COLOR)"
endif

###############################################################################
# docs
###############################################################################

DOCS_BIN?=bin/sphinx-build
DOCS_SOURCE?=docs/source
DOCS_TARGET?=docs/html

.PHONY: docs
docs:
	@echo "$(OK_COLOR)Build sphinx docs $(NO_COLOR)"
ifneq ("$(wildcard $(DOCS_BIN))","")
	@$(DOCS_BIN) $(DOCS_SOURCE) $(DOCS_TARGET)
else
	@echo "$(ERROR_COLOR)Sphinx binary not exists $(ERROR_COLOR)"
endif

###############################################################################
# test
###############################################################################

TEST_SCRIPT=scripts/run-tests.sh

.PHONY: test
test:
	@echo "$(OK_COLOR)Run tests $(NO_COLOR)"
ifneq ("$(wildcard $(TEST_SCRIPT))","")
	@$(TEST_SCRIPT)
else
	@echo "$(ERROR_COLOR)Test script not exists $(ERROR_COLOR)"
endif

###############################################################################
# coverage
###############################################################################

COVERAGE_SCRIPT=scripts/run-coverage.sh

.PHONY: coverage
coverage:
	@echo "$(OK_COLOR)Run coverage $(NO_COLOR)"
ifneq ("$(wildcard $(COVERAGE_SCRIPT))","")
	@$(COVERAGE_SCRIPT)
else
	@echo "$(ERROR_COLOR)Coverage script not exists $(ERROR_COLOR)"
endif

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
	@echo "$(OK_COLOR)Clean environment $(NO_COLOR)"
ifneq ("$(wildcard $(CUSTOM_CLEAN_TARGETS))","")
	@rm -rf $$(cat $(CUSTOM_CLEAN_TARGETS))
endif
	@rm -rf $(COMMON_CLEAN_TARGETS)

###############################################################################
# Include custom make files
###############################################################################

-include config/*.mk
