Usage (mostly outdated)
=======================


Basics
------

To bootstrap a new project with *mxmake*, create a project for your project:

.. code-block:: sh

    $ wget https://raw.githubusercontent.com/mxstack/mxmake/main/makefiles/Makefile
    $ wget https://raw.githubusercontent.com/mxstack/mxmake/main/examples/mx.ini

Optionally create ``mk`` folder and inside create ``project.mk`` for project
specific settings, includes and custom make targets. If this file is present it
gets included when running make:

.. code-block:: sh

    $ mkdir mk
    $ cd mk
    $ wget https://raw.githubusercontent.com/mxstack/mxmake/main/examples/project.mk

After proper :ref:`Configuration` of the ini file, run:

.. code-block:: sh

    $ make install

This installs a Python virtual environment, generates the relevant files,
checks out the sources defined in ``mx.ini`` and installs everything using
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
-------------

Additional project configuration is located in ``mx.ini``.

Helper scripts are generated from templates which are defined in the
``settings`` section the ini file:

.. code-block:: ini

    [settings]
    mxmake-templates = name1 name2

Additional template related settings are defined in dedicated config sections
named after ``mxmake-<templatename>``:

.. code-block:: ini

    [mxmake-name1]
    setting = value

See :ref:`Templates` for documations about the available templates.

See `here <https://github.com/mxstack/mxdev>`_ for more documentation
about the ``mxdev`` config file.


Make
----

``mxmake`` provides a generic `Makefile` for managing common install and
development tasks. This file contains a set of unified make targets for working
on your project.

At the end of the `Makefile`, a file named `project.mk` gets included if
present. It is expected in the `mk` folder of your project. This file is
supposed to contain project specific includes, setting overrides and additional
cutom targets.

An example `project.mk` can be found
`here <https://github.com/mxstack/mxmake/tree/master/examples>`_.

The generic ``mxmake`` `Makefile` and a set of useful domain specific make files
to be included in your project can be found
`here <https://github.com/mxstack/mxmake/tree/master/makefiles>`_.


.. _Targets:

Targets
~~~~~~~

The available make targets are build with ``make <targetname>``.


Templates
---------

The following section describes the templates which can be build by ``mxmake``.


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
    # tell mxmake to generate test script
    mxmake-templates = run-tests

    # optional system variables to set before running the tests
    [mxmake-env]
    ENVVAR = value

    # test script related settings
    [mxmake-run-tests]
    # the section to use for environment variables
    environment = env

    # package related
    [packagename]
    # relative path to package checkout directory to search for tests
    mxmake-test-path = src


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
    # tell mxmake to generate coverage script
    mxmake-templates = run-coverage

    # optional system variables to set before running tests and coverage
    [mxmake-env]
    ENVVAR = value

    # coverage script related settings
    [mxmake-run-coverage]
    # the section to use for environment variables
    environment = env

    # package related
    [packagename]
    # relative path to package checkout directory to search for tests
    # also used by ``run-tests``
    mxmake-test-path = src
    # relative path(s) to package checkout directory to define coverage source path
    mxmake-source-path = src/packagename
    # relative path(s) to package checkout directory to define coverage omit path
    mxmake-omit-path = src/packagename/file.py
