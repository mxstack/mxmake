mxenv - Create development environments for python packages
===========================================================

.. toctree::
   :maxdepth: 3
   :caption: Contents:


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

    $ wget https://raw.githubusercontent.com/conestack/mxenv/master/makefiles/Makefile
    $ wget https://raw.githubusercontent.com/conestack/mxenv/master/examples/mxdev.ini

Optionally create ``mk`` folder and inside create ``project.mk`` for project
specific settings, includes and custom make targets. If this file is present it
gets included when running make:

.. code-block:: sh

    $ mkdir mk
    $ cd mk
    $ wget https://raw.githubusercontent.com/conestack/mxenv/master/examples/project.mk

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

See `here <https://github.com/bluedynamics/mxdev>`_ for more documentation
about the ``mxdev`` config file.


Make
----

``mxenv`` provides a generic `Makefile` for managing common install and
development tasks. This file contains a set of unified make targets for working
on your project.

At the end of the `Makefile`, a file named `project.mk` gets included if
present. It is expected in the `mk` folder of your project. This file is
supposed to contain project specific includes, setting overrides and additional
cutom targets.

An example `project.mk` can be found
`here <https://github.com/conestack/mxenv/tree/master/examples>`_.

The generic ``mxenv`` `Makefile` and a set of useful domain specific make files
to be included in your project can be found
`here <https://github.com/conestack/mxenv/tree/master/makefiles>`_.


.. _Targets:

Targets
~~~~~~~

The available make targets are build with ``make <targetname>``.


.. _venv:

venv
++++

Create python virtual environment. The following python packages are installed
respective updated:

- pip
- setuptools
- wheel
- mxdev
- mxenv

**Configuration options**:

- ``PYTHON``: The python interpreter to use for creating the virtual environment.
  Defaults to `python3`.
- ``VENV_FOLDER``: The folder where the virtual environment get created.
  Defaults to `venv`.


.. _venv-dirty:

venv-dirty
++++++++++

Build :ref:`venv` target on next make run.


.. _venv-clean:

venv-clean
++++++++++

Removes virtual environment.


.. _files:

files
+++++

Create all project files by running ``mxdev``. It does not checkout sources.

**Dependency targets**:

- :ref:`venv``

**Configuration options**:

- ``PROJECT_CONFIG``: The config file to use. Defaults to `mxdev.ini`.
- ``SCRIPTS_FOLDER``: Target folder for generated scripts. Defaults to `venv/bin`.
- ``CONFIG_FOLDER``: Target folder for generated config files. Defaults to `cfg`.


.. _files-dirty:

files-dirty
+++++++++++

Build :ref:`files` target on next make run.


.. _files-clean:

files-clean
+++++++++++

Remove generated project files.


.. _sources:

sources
+++++++

Checkout sources by running ``mxdev``. It does not generate project files.

**Dependency targets**:

- :ref:`files``

**Configuration options**:

- ``PROJECT_CONFIG``: The config file to use. Defaults to `mxdev.ini`.


.. _sources-dirty:

sources-dirty
+++++++++++++

Build :ref:`sources` target on next make run.


.. _sources-clean:

sources-clean
+++++++++++++

Removes sources folder.


.. _install:

install
+++++++

Install packages with pip after creating files and checking out sources.

**Dependency targets**:

- :ref:`sources``


.. _install-dirty:

install-dirty
+++++++++++++

Build :ref:`install` target on next make run.


.. _system-dependencies:

system-dependencies
+++++++++++++++++++

Install system dependencies.

**Configuration options**:

- ``SYSTEM_DEPENDENCIES``: Space separated system package names.


.. _docs:

docs
++++

Generate sphinx docs. Sphinx is expected to be installed. This is not done
automatically.

**Configuration options**:

- ``DOCS_BIN``: The Sphinx build executable. Defaults to
  `$(VENV_FOLDER)/bin/sphinx-build`.
- ``DOCS_SOURCE``: Documentation source folder. Defaults to `docs/source`.
- ``DOCS_TARGET``: Documentation generation target folder. Defaults to `docs/html`.


.. _docs-clean:

docs-clean
++++++++++

Removes generated docs.


.. _test:

test
++++

Run project tests. The :ref:`run-tests` template can be used for automatic
test script creation.

**Dependency targets**:

- :ref:`install``

**Configuration options**:

- ``TEST_COMMAND``: The command which gets executed. Defaults to
  `$(SCRIPTS_FOLDER)/run-tests.sh`, which is the default location the
  :ref:`run-tests` template gets rendered to if configured.


.. _coverage:

coverage
++++++++

Run project coverage. :ref:`run-coverage` template can be used for automatic
coverage script creation.

**Dependency targets**:

- :ref:`install``

**Configuration options**:

- ``COVERAGE_COMMAND``: The command which gets executed. Defaults to
  `$(SCRIPTS_FOLDER)/run-coverage.sh`, which is the default location the
  :ref:`run-coverage` template gets rendered to if configured.


.. _coverage-clean:

coverage-clean
++++++++++++++

Remove coverage related files and directories.


.. _clean:

clean
+++++

Cleanup project environment.

**Configuration options**:

- ``CLEAN_TARGETS``: Space separated list of files and folders to remove.


.. _full-clean:

full-clean
++++++++++

Cleanup project environment including sources.


.. runtime-clean:

runtime-clean
+++++++++++++

Remove runtime artifacts, like byte-code and caches.


.. _Templates:

Templates
---------

The following section describes the templates which can be build by ``mxenv``.


.. _run-tests:

run-tests
~~~~~~~~~

A script for running tests of python packages defined as ``mxdev`` sources. It
utilizes ``zope-testrunner``, thus expects it to be installed.

The generation target is ``scripts/run-tests.sh``.

Invocation of the test run is done via :ref:`test` make target.

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


.. _run-coverage:

run-coverage
~~~~~~~~~~~~

A script for running coverage tests of python packages defined as ``mxdev``
sources. It utilizes ``zope-testrunner`` and ``coverage``, thus expects these
packages to be installed.

The generation target is ``scripts/run-coverage.sh``.

Invocation of the coverage run is done via :ref:`coverage` make target.

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


Source Code
===========

The sources are in a GIT DVCS with its main branches at
`github <http://github.com/conestack/mxenv>`_.


Copyright
=========

- Copyright (c) 2022 Cone Contributors


Contributors
============

- Robert Niederreiter


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
