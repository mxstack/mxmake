# Makefile to bootstrap an mxenv project.

PYTHON?=python3
VENV_FOLDER?=.
PIP_BIN=${VENV_FOLDER}/bin/pip
MXDEV?=https://github.com/bluedynamics/mxdev/archive/master.zip
MVENV?=https://github.com/conestack/mxenv/archive/master.zip

.PHONY: bootstrap
bootstrap:
	@echo "Bootstrap a new mxenv based project"
	@${PYTHON} -m venv ${VENV_FOLDER}
	@${PIP_BIN} install -U pip setuptools wheel
	@${PIP_BIN} install ${MXDEV}
	@${PIP_BIN} install ${MVENV}
