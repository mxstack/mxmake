**``mxenv`` - Create development environmets for python packages.**

.. image:: https://img.shields.io/pypi/v/mxenv.svg
    :target: https://pypi.python.org/pypi/mxenv
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/mxenv.svg
    :target: https://pypi.python.org/pypi/mxenv
    :alt: Number of PyPI downloads


Overview
--------

This tool helps creating development environments for python projects based
on `make <https://www.gnu.org/software/make>`_ and
`mxdev <https://github.com/bluedynamics/mxdev>`_.

``mxdev`` is used to manage a set of project related python package repositories
to work on. See `here <https://github.com/bluedynamics/mxdev>`_ for detailed
documentation.

``mxenv`` provides generating helper scripts for development and a Makefile for
running tasks like project installation or tests.

It's initial target is for development of the repositories contained in the
`conestack <https://github.com/conestack>`_ organization on github.


Usage
-----

Basics
~~~~~~

To bootstrap a new project with mxenv, download ``Makefile`` and ``mxdev.ini``
to your project folder:

.. code-block:: sh

    $ wget https://raw.githubusercontent.com/conestack/mxenv/master/files/Makefile
    $ wget https://raw.githubusercontent.com/conestack/mxenv/master/files/mxdev.ini

After proper :ref:`Configuration` of the ini file, run:

.. code-block:: sh

    $ make install

This installs a Python virtual environment, generates the relevant files,
checks out the sources defined in ``mxdev.ini`` and installs everything using
pip.

To run the test suite, type:

.. code-block:: sh

    $ make test

Run code coverage and create coverage report:

.. code-block:: sh

    $ make coverage

Cleanup the development environment:

.. code-block:: sh

    $ make clean

Cleanup everything including the sources:

.. code-block:: sh

    $ make full-clean

See :ref:`Targets` for more information about the available make targets.


.. _Configuration:

Configuration
~~~~~~~~~~~~~

Additional project configuration is located in ``mxdev.ini``.

Helper scripts are generated from templates which are defined in the
``settings`` section the ini file:

.. code-block:: ini

    [settings]
    mxenv-templates = name1 name2

Additional template related settings are defined in dedicated config sections
named after ``mxenv-<templatename>``:

.. code-block:: ini

    [mxenv-name1]
    setting = value

See :ref:`Templates` for documations about the available templates.

See `here <https://github.com/bluedynamics/mxdev>`_ for more
documentation about config file.


Make
----

The ``Makefile`` contains a set of targets for working on your project.

At the end of the ``Makefile``, all files ending with ``.mk`` contained in the
``config`` folder are included.

Some read-to-use include files can be found in the
`templates <https://github.com/conestack/mxenv/tree/master/files/cfg>`_.


.. _Targets:

Targets
~~~~~~~

The available make targets are build with ``make <targetname>``.

**venv**

Create python virtual environment. The following python packages are installed
respective updated:

- pip
- setuptools
- wheel
- mxdev
- mxenv

Configuration options:

- PYTHON: The python interpreter to use for creating the virtual environment.
  Defaults to ``python3``.
- VENV_FOLDER: The folder where the virtual environment get created. Defaults
  to ``venv``.

**venv-dirty**

Build ``venv`` target on next make run.

**venv-clean**

Removes virtual environment.

**files**

Create all project files by running ``mxdev``. It does not checkout sources.

Dependency targets:

- venv

Configuration options:

- PROJECT_CONFIG: The config file to use. Defaults to ``mxdev.ini``.
- SCRIPTS_FOLDER: Target folder for generated scripts. Defaults to ``venv/bin``.
- CONFIG_FOLDER: Target folder for generated config files. Defaults to ``cfg``.

**files-dirty**

Build ``files`` target on next make run.

**files-clean**

Remove generated project files.

**sources**

Checkout sources by running ``mxdev``. It does not generate project files.

Dependency targets:

- files

Configuration options:

- PROJECT_CONFIG: The config file to use. Defaults to ``mxdev.ini``.

**sources-dirty**

Build ``sources`` target on next make run.

**sources-clean**

Removes sources folder.

**install**

Install packages with pip after creating files and checking out sources.

Dependency targets:

- sources

**install-dirty**

Build ``install`` target on next make run.

**system-dependencies**

Install system dependencies.

Configuration options:

- SYSTEM_DEPENDENCIES: Space separated system package names.

**docs**

Generate sphinx docs. Sphinx is expected to be installed. This is not done
automatically.

Configuration options:

- DOCS_BIN: The Sphinx build executable. Defaults to  ``bin/sphinx-build``.
- DOCS_SOURCE: Documentation source folder. Defaults to ``docs/source``.
- DOCS_TARGET: Documentation generation target folder. Defaults to ``docs/html``.

**docs-clean**

Removes generated docs.

**test**

Run project tests.

Dependency targets:

- install

**coverage**

Run project coverage.

Dependency targets:

- install

**coverage-clean**

Remove coverage related files and directories.

**clean**

Cleanup project environment.

Configuration options:

- CLEAN_TARGETS: Space separated list of files and folders to remove.

**full-clean**

Cleanup project environment including sources.


.. _Templates:

Templates
---------

The following section describes the templates which can be build by mxenv.


run-tests
~~~~~~~~~

A script for running tests of python packages defined as mxdev sources. It
utilizes ``zope-testrunner``, thus expects it to be installed.

The generation target is ``scripts/run-tests.sh``.

Invocation of the test run is done via ``make tests``.

Configuration looks like so:

.. code-block:: ini

    [settings]
    # tell mxenv to generate test script
    mxenv-templates = run-tests

    # optional system variables to set before running the tests
    [mxenv-env]
    ENVVAR = value

    # test script related settings
    [mxenv-run-tests]
    # the section to use for environment variables
    environment = env

    # package related
    [packagename]
    # relative path to package checkout directory to search for tests
    mxenv-test-path = src


run-coverage
~~~~~~~~~~~~

A script for running coverage tests of python packages defined as mxdev sources.
It utilizes ``zope-testrunner`` and ``coverage``, thus expects these packages to
be installed.

The generation target is ``scripts/run-coverage.sh``.

Invocation of the coverage run is done via ``make coverage``.

Configuration looks like so:

.. code-block:: ini

    [settings]
    # tell mxenv to generate coverage script
    mxenv-templates = run-coverage

    # optional system variables to set before running tests and coverage
    [mxenv-env]
    ENVVAR = value

    # coverage script related settings
    [mxenv-run-coverage]
    # the section to use for environment variables
    environment = env

    # package related
    [packagename]
    # relative path to package checkout directory to search for tests
    # also used by ``run-tests``
    mxenv-test-path = src
    # relative path to package checkout directory to define coverage source path
    mxenv-source-path = src/node


Contributors
============

- Robert Niederreiter
