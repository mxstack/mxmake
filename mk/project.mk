###############################################################################
# mxmake specific make file.
#
# This project file is for mxmake development itself.
#
# If you're searching for an examples, see examples folder.
###############################################################################

## ``venv`` target
MXMAKE=-e .[docs]

## ``test`` target
TEST_COMMAND=$(VENV_FOLDER)/bin/python setup.py test

## ``coverage`` target
COVERAGE_COMMAND=

## ``clean`` target
CLEAN_TARGETS+=dist mxmake.egg-info
