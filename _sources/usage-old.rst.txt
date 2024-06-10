Usage (mostly outdated)
=======================

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

.. _Templates:

Templates
---------

The following section describes the templates which can be build by ``mxmake``.

.. _run-tests:

run-tests
~~~~~~~~~

A script for running tests of python packages defined as ``mxdev`` sources. It
utilizes ``zope-testrunner``, thus expects it to be installed.

The generation target is ``scripts/run-tests.sh``.

Invocation of the test run is done via `test` make target.

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

Invocation of the coverage run is done via `coverage` make target.

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
