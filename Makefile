##############################################################################
# THIS FILE IS GENERATED BY MXMAKE
#
# DOMAINS:
#: core.base
#: core.mxenv
#: core.mxfiles
#: core.packages
#: docs.sphinx
#: qa.black
#: qa.coverage
#: qa.isort
#: qa.mypy
#: qa.test
#
# SETTINGS (ALL CHANGES MADE BELOW SETTINGS WILL BE LOST)
##############################################################################

## core.base

# `deploy` target dependencies.
# No default value.
DEPLOY_TARGETS?=

# Additional files and folders to remove when running clean target
# No default value.
CLEAN_FS?=

## core.mxenv

# Python interpreter to use.
# Default: python3
PYTHON_BIN?=python3

# Minimum required Python version.
# Default: 3.7
PYTHON_MIN_VERSION?=3.7

# Flag whether to use virtual environment.
# If `false`, the interpreter according to `PYTHON_BIN` found in `PATH` is used.
# Default: true
VENV_ENABLED?=true

# Flag whether to create a virtual environment. If set to `false`
# and `VENV_ENABLED` is `true`, `VENV_FOLDER` is expected to point to an
# existing virtual environment.
# Default: true
VENV_CREATE?=true

# The folder of the virtual environment.
# If `VENV_ENABLED` is `true` and `VENV_CREATE` is true it is used as the target folder for the virtual environment.
# If `VENV_ENABLED` is `true` and `VENV_CREATE` is false it is expected to point to an existing virtual environment.
# If `VENV_ENABLED` is `false` it is ignored.
# Default: venv
VENV_FOLDER?=venv

# mxdev to install in virtual environment.
# Default: https://github.com/mxstack/mxdev/archive/main.zip
MXDEV?=https://github.com/mxstack/mxdev/archive/main.zip

# mxmake to install in virtual environment.
# Default: https://github.com/mxstack/mxmake/archive/develop.zip
MXMAKE?=-e .

## qa.isort

# Source folder to scan for Python files to run isort on.
# Default: src
ISORT_SRC?=src

## qa.black

# Source folder to scan for Python files to run black on.
# Default: src
BLACK_SRC?=src

## docs.sphinx

# Documentation source folder.
# Default: docs/source
DOCS_SOURCE_FOLDER?=docs/source

# Documentation generation target folder.
# Default: docs/html
DOCS_TARGET_FOLDER?=docs/html

# Documentation Python requirements to be installed (via pip).
# No default value.
DOCS_REQUIREMENTS?=sphinx-conestack-theme myst-parser sphinxcontrib-mermaid

## core.mxfiles

# The config file to use.
# Default: mx.ini
PROJECT_CONFIG?=mx.ini

## qa.test

# The command which gets executed. Defaults to the location the
# :ref:`run-tests` template gets rendered to if configured.
# Default: .mxmake/files/run-tests.sh
TEST_COMMAND?=$(VENV_FOLDER)/bin/python -m mxmake.tests.__init__

# Additional make targets the test target depends on.
# No default value.
TEST_DEPENDENCY_TARGETS?=

## qa.mypy

# Source folder for code analysis.
# Default: src
MYPY_SRC?=src

# Mypy Python requirements to be installed (via pip).
# Default: types-setuptools
MYPY_REQUIREMENTS?=types-setuptools types-docutils

## qa.coverage

# The command which gets executed. Defaults to the location the
# :ref:`run-coverage` template gets rendered to if configured.
# Default: .mxmake/files/run-coverage.sh
COVERAGE_COMMAND?=$(VENV_FOLDER)/bin/coverage run -m mxmake.tests

##############################################################################
# END SETTINGS - DO NOT EDIT BELOW THIS LINE
##############################################################################

INSTALL_TARGETS?=
DIRTY_TARGETS?=
CLEAN_TARGETS?=
PURGE_TARGETS?=
CHECK_TARGETS?=
FORMAT_TARGETS?=

# Defensive settings for make: https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
# for Makefile debugging purposes add -x to the .SHELLFLAGS
.SHELLFLAGS:=-eu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# mxmake folder
MXMAKE_FOLDER?=.mxmake

# Sentinel files
SENTINEL_FOLDER?=$(MXMAKE_FOLDER)/sentinels
SENTINEL?=$(SENTINEL_FOLDER)/about.txt
$(SENTINEL):
	@mkdir -p $(SENTINEL_FOLDER)
	@echo "Sentinels for the Makefile process." > $(SENTINEL)

##############################################################################
# mxenv
##############################################################################

# Check if given Python is installed
ifeq (,$(shell which $(PYTHON_BIN)))
$(error "PYTHON=$(PYTHON_BIN) not found in $(PATH)")
endif

# Check if given Python version is ok
PYTHON_VERSION_OK=$(shell $(PYTHON_BIN) -c "import sys; print((int(sys.version_info[0]), int(sys.version_info[1])) >= tuple(map(int, '$(PYTHON_MIN_VERSION)'.split('.'))))")
ifeq ($(PYTHON_VERSION_OK),0)
$(error "Need Python >= $(PYTHON_MIN_VERSION)")
endif

# Check if venv folder is configured if venv is enabled
ifeq ($(shell [[ "$(VENV_ENABLED)" == "true" && "$(VENV_FOLDER)" == "" ]] && echo "true"),"true")
$(error "VENV_FOLDER must be configured if VENV_ENABLED is true")
endif

# determine the executable path
ifeq ("$(VENV_ENABLED)", "true")
MXENV_PATH=$(VENV_FOLDER)/bin/
else
MXENV_PATH=
endif

MXENV_TARGET:=$(SENTINEL_FOLDER)/mxenv.sentinel
$(MXENV_TARGET): $(SENTINEL)
ifeq ("$(VENV_ENABLED)", "true")
	@echo "Setup Python Virtual Environment under '$(VENV_FOLDER)'"
	@$(PYTHON_BIN) -m venv $(VENV_FOLDER)
endif
	@$(MXENV_PATH)pip install -U pip setuptools wheel
	@$(MXENV_PATH)pip install -U $(MXDEV)
	@$(MXENV_PATH)pip install -U $(MXMAKE)
	@touch $(MXENV_TARGET)

.PHONY: mxenv
mxenv: $(MXENV_TARGET)

.PHONY: mxenv-dirty
mxenv-dirty:
	@rm -f $(MXENV_TARGET)

.PHONY: mxenv-clean
mxenv-clean: mxenv-dirty
ifeq ("$(VENV_ENABLED)", "true")
	@rm -rf $(VENV_FOLDER)
else
	@$(MXENV_PATH)pip uninstall -y $(MXDEV)
	@$(MXENV_PATH)pip uninstall -y $(MXMAKE)
endif

INSTALL_TARGETS+=mxenv
DIRTY_TARGETS+=mxenv-dirty
CLEAN_TARGETS+=mxenv-clean

##############################################################################
# isort
##############################################################################

ISORT_TARGET:=$(SENTINEL_FOLDER)/isort.sentinel
$(ISORT_TARGET): $(MXENV_TARGET)
	@echo "Install isort"
	@$(MXENV_PATH)pip install isort
	@touch $(ISORT_TARGET)

.PHONY: isort-check
isort-check: $(ISORT_TARGET)
	@echo "Run isort check"
	@$(MXENV_PATH)isort --check $(ISORT_SRC)

.PHONY: isort-format
isort-format: $(ISORT_TARGET)
	@echo "Run isort format"
	@$(MXENV_PATH)isort $(ISORT_SRC)

.PHONY: isort-dirty
isort-dirty:
	@rm -f $(ISORT_TARGET)

.PHONY: isort-clean
isort-clean: isort-dirty
	@test -e $(MXENV_PATH)pip && $(MXENV_PATH)pip uninstall -y isort || :

INSTALL_TARGETS+=$(ISORT_TARGET)
CHECK_TARGETS+=isort-check
FORMAT_TARGETS+=isort-format
DIRTY_TARGETS+=isort-dirty
CLEAN_TARGETS+=isort-clean

##############################################################################
# black
##############################################################################

BLACK_TARGET:=$(SENTINEL_FOLDER)/black.sentinel
$(BLACK_TARGET): $(MXENV_TARGET)
	@echo "Install Black"
	@$(MXENV_PATH)pip install black
	@touch $(BLACK_TARGET)

.PHONY: black-check
black-check: $(BLACK_TARGET)
	@echo "Run black checks"
	@$(MXENV_PATH)black --check $(BLACK_SRC)

.PHONY: black-format
black-format: $(BLACK_TARGET)
	@echo "Run black format"
	@$(MXENV_PATH)black $(BLACK_SRC)

.PHONY: black-dirty
black-dirty:
	@rm -f $(BLACK_TARGET)

.PHONY: black-clean
black-clean: black-dirty
	@test -e $(MXENV_PATH)pip && $(MXENV_PATH)pip uninstall -y black || :

INSTALL_TARGETS+=$(BLACK_TARGET)
CHECK_TARGETS+=black-check
FORMAT_TARGETS+=black-format
DIRTY_TARGETS+=black-dirty
CLEAN_TARGETS+=black-clean

##############################################################################
# sphinx
##############################################################################

# additional targets required for building docs.
DOCS_TARGETS+=

SPHINX_BIN=$(MXENV_PATH)sphinx-build
SPHINX_AUTOBUILD_BIN=$(MXENV_PATH)sphinx-autobuild

DOCS_TARGET:=$(SENTINEL_FOLDER)/sphinx.sentinel
$(DOCS_TARGET): $(MXENV_TARGET)
	@echo "Install Sphinx"
	@$(MXENV_PATH)pip install -U sphinx sphinx-autobuild $(DOCS_REQUIREMENTS)
	@touch $(DOCS_TARGET)

.PHONY: docs
docs: $(DOCS_TARGET) $(DOCS_TARGETS)
	@echo "Build sphinx docs"
	@$(SPHINX_BIN) $(DOCS_SOURCE_FOLDER) $(DOCS_TARGET_FOLDER)

.PHONY: docs-live
docs-live: $(DOCS_TARGET) $(DOCS_TARGETS)
	@echo "Rebuild Sphinx documentation on changes, with live-reload in the browser"
	@$(SPHINX_AUTOBUILD_BIN) $(DOCS_SOURCE_FOLDER) $(DOCS_TARGET_FOLDER)

.PHONY: docs-dirty
docs-dirty:
	@rm -f $(DOCS_TARGET)

.PHONY: docs-clean
docs-clean: docs-dirty
	@rm -rf $(DOCS_TARGET_FOLDER)

INSTALL_TARGETS+=$(DOCS_TARGET)
DIRTY_TARGETS+=docs-dirty
CLEAN_TARGETS+=docs-clean

##############################################################################
# mxfiles
##############################################################################

# case `core.sources` domain not included
SOURCES_TARGET?=

# File generation target
MXMAKE_FILES?=$(MXMAKE_FOLDER)/files

# set environment variables for mxmake
define set_mxfiles_env
	@export MXMAKE_MXENV_PATH=$(1)
	@export MXMAKE_FILES=$(2)
endef

# unset environment variables for mxmake
define unset_mxfiles_env
	@unset MXMAKE_MXENV_PATH
	@unset MXMAKE_FILES
endef

$(PROJECT_CONFIG):
ifneq ("$(wildcard $(PROJECT_CONFIG))","")
	@touch $(PROJECT_CONFIG)
else
	@echo "[settings]" > $(PROJECT_CONFIG)
endif

LOCAL_PACKAGE_FILES:=$(wildcard pyproject.toml setup.cfg setup.py requirements.txt constraints.txt)

FILES_TARGET:=requirements-mxdev.txt
$(FILES_TARGET): $(PROJECT_CONFIG) $(MXENV_TARGET) $(SOURCES_TARGET) $(LOCAL_PACKAGE_FILES)
	@echo "Create project files"
	@mkdir -p $(MXMAKE_FILES)
	$(call set_mxfiles_env,$(MXENV_PATH),$(MXMAKE_FILES))
	@$(MXENV_PATH)mxdev -n -c $(PROJECT_CONFIG)
	$(call unset_mxfiles_env,$(MXENV_PATH),$(MXMAKE_FILES))
	@touch $(FILES_TARGET)

.PHONY: mxfiles
mxfiles: $(FILES_TARGET)

.PHONY: mxfiles-dirty
mxfiles-dirty:
	@touch $(PROJECT_CONFIG)

.PHONY: mxfiles-clean
mxfiles-clean: mxfiles-dirty
	@rm -rf constraints-mxdev.txt requirements-mxdev.txt $(MXMAKE_FILES)

INSTALL_TARGETS+=mxfiles
DIRTY_TARGETS+=mxfiles-dirty
CLEAN_TARGETS+=mxfiles-clean

##############################################################################
# packages
##############################################################################

# additional sources targets which requires package re-install on change
-include $(MXMAKE_FILES)/additional_sources_targets.mk
ADDITIONAL_SOURCES_TARGETS?=

INSTALLED_PACKAGES=$(MXMAKE_FILES)/installed.txt

PACKAGES_TARGET:=$(INSTALLED_PACKAGES)
$(PACKAGES_TARGET): $(FILES_TARGET) $(ADDITIONAL_SOURCES_TARGETS)
	@echo "Install python packages"
	@$(MXENV_PATH)pip install -r $(FILES_TARGET)
	@$(MXENV_PATH)pip freeze > $(INSTALLED_PACKAGES)
	@touch $(PACKAGES_TARGET)

.PHONY: packages
packages: $(PACKAGES_TARGET)

.PHONY: packages-dirty
packages-dirty:
	@rm -f $(PACKAGES_TARGET)

.PHONY: packages-clean
packages-clean:
	@test -e $(FILES_TARGET) \
		&& test -e $(MXENV_PATH)pip \
		&& $(MXENV_PATH)pip uninstall -y -r $(FILES_TARGET) \
		|| :
	@rm -f $(PACKAGES_TARGET)

INSTALL_TARGETS+=packages
DIRTY_TARGETS+=packages-dirty
CLEAN_TARGETS+=packages-clean

##############################################################################
# test
##############################################################################

.PHONY: test
test: $(FILES_TARGET) $(SOURCES_TARGET) $(PACKAGES_TARGET) $(TEST_DEPENDENCY_TARGETS)
	@echo "Run tests"
	@test -z "$(TEST_COMMAND)" && echo "No test command defined"
	@test -z "$(TEST_COMMAND)" || bash -c "$(TEST_COMMAND)"


##############################################################################
# mypy
##############################################################################

MYPY_TARGET:=$(SENTINEL_FOLDER)/mypy.sentinel
$(MYPY_TARGET): $(MXENV_TARGET)
	@echo "Install mypy"
	@$(MXENV_PATH)pip install mypy $(MYPY_REQUIREMENTS)
	@touch $(MYPY_TARGET)

.PHONY: mypy
mypy: $(PACKAGES_TARGET) $(MYPY_TARGET)
	@echo "Run mypy"
	@$(MXENV_PATH)mypy $(MYPY_SRC)

.PHONY: mypy-dirty
mypy-dirty:
	@rm -f $(MYPY_TARGET)

.PHONY: mypy-clean
mypy-clean: mypy-dirty
	@test -e $(MXENV_PATH)pip && $(MXENV_PATH)pip uninstall -y mypy || :
	@rm -rf .mypy_cache

INSTALL_TARGETS+=$(MYPY_TARGET)
CHECK_TARGETS+=mypy
CLEAN_TARGETS+=mypy-clean
DIRTY_TARGETS+=mypy-dirty

##############################################################################
# coverage
##############################################################################

COVERAGE_TARGET:=$(SENTINEL_FOLDER)/coverage.sentinel
$(COVERAGE_TARGET): $(MXENV_TARGET)
	@echo "Install Coverage"
	@$(MXENV_PATH)pip install -U coverage
	@touch $(COVERAGE_TARGET)

.PHONY: coverage
coverage: $(FILES_TARGET) $(SOURCES_TARGET) $(PACKAGES_TARGET) $(COVERAGE_TARGET)
	@echo "Run coverage"
	@test -z "$(COVERAGE_COMMAND)" && echo "No coverage command defined"
	@test -z "$(COVERAGE_COMMAND)" || bash -c "$(COVERAGE_COMMAND)"

.PHONY: coverage-dirty
coverage-dirty:
	@rm -f $(COVERAGE_TARGET)

.PHONY: coverage-clean
coverage-clean: coverage-dirty
	@test -e $(MXENV_PATH)pip && $(MXENV_PATH)pip uninstall -y coverage || :
	@rm -rf .coverage htmlcov

INSTALL_TARGETS+=$(COVERAGE_TARGET)
DIRTY_TARGETS+=coverage-dirty
CLEAN_TARGETS+=coverage-clean

##############################################################################
# Default targets
##############################################################################

INSTALL_TARGET:=$(SENTINEL_FOLDER)/install.sentinel
$(INSTALL_TARGET): $(INSTALL_TARGETS)
	@touch $(INSTALL_TARGET)

.PHONY: install
install: $(INSTALL_TARGET)
	@touch $(INSTALL_TARGET)

.PHONY: deploy
deploy: $(DEPLOY_TARGETS)

.PHONY: dirty
dirty: $(DIRTY_TARGETS)
	@rm -f $(INSTALL_TARGET)

.PHONY: clean
clean: dirty $(CLEAN_TARGETS)
	@rm -rf $(CLEAN_TARGETS) $(MXMAKE_FOLDER) $(CLEAN_FS)

.PHONY: purge
purge: clean $(PURGE_TARGETS)

.PHONY: runtime-clean
runtime-clean:
	@echo "Remove runtime artifacts, like byte-code and caches."
	@find . -name '*.py[c|o]' -delete
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

.PHONY: check
check: $(CHECK_TARGETS)

.PHONY: format
format: $(FORMAT_TARGETS)
