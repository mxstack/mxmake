# Makefile for mxenv projects.

###############################################################################
# Settings

PYTHON?=python3
VENV_FOLDER?=.
PROJECT_CONFIG?=mxdev.ini

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

###############################################################################
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

###############################################################################
# Basics

PIP_BIN:=$(VENV_FOLDER)/bin/pip
MXDEV:=https://github.com/bluedynamics/mxdev/archive/master.zip
MVENV:=https://github.com/conestack/mxenv/archive/master.zip

# Sentinel files
SENTINEL_FOLDER:=make/.sentinels
SENTINEL:=$(SENTINEL_FOLDER)/about.txt
$(SENTINEL):
	@mkdir -p $(SENTINEL_FOLDER)
	@echo "Sentinels for the Makefile process." > $(SENTINEL)

###############################################################################
# venv

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

MXENV_SENTINEL:=$(SENTINEL_FOLDER)/mxenv.sentinel

.PHONY: mxenv
mxenv: $(MXENV_SENTINEL)

$(MXENV_SENTINEL): $(VENV_SENTINEL) $(SENTINEL)
	@echo "$(OK_COLOR)Create project files $(NO_COLOR)"
	@$(VENV_FOLDER)/bin/mxdev -n -c $(PROJECT_CONFIG)
	@touch $(MXENV_SENTINEL)

###############################################################################
# mxdev

MXDEV_SENTINEL:=$(SENTINEL_FOLDER)/mxdev.sentinel

.PHONY: mxdev
mxdev: $(MXDEV_SENTINEL)

$(MXDEV_SENTINEL): $(MXENV_SENTINEL) $(VENV_SENTINEL) $(SENTINEL)
	@echo "$(OK_COLOR)Run mxdev $(NO_COLOR)"
	@$(VENV_FOLDER)/bin/mxdev -c $(PROJECT_CONFIG)
	@touch $(MXDEV_SENTINEL)

###############################################################################
# pip

PIP_PACKAGES=installed.txt

.PHONY: pip
pip: $(PIP_PACKAGES)

$(PIP_PACKAGES): $(MXDEV_SENTINEL) $(MXENV_SENTINEL) $(VENV_SENTINEL) $(SENTINEL)
	@echo "$(OK_COLOR)Install python packages $(NO_COLOR)"
	@$(PIP_BIN) install -r requirements-mxdev.txt
	@$(PIP_BIN) freeze > $(PIP_PACKAGES)
