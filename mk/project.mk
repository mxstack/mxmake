###############################################################################
# mxenv specific make file.
#
# This project file is for mxenv development itself.
#
# If you're searching for an examples, see examples folder.
###############################################################################

## ``venv`` target
MXENV=-e .

## ``test`` target
TEST_COMMAND=$(VENV_FOLDER)/bin/python setup.py test

## ``coverage`` target
COVERAGE_COMMAND=
