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

It's initial target is for development of the repositories contained in the
 `conestack <https://github.com/conestack>`_ organization on github.


Bootstrap
---------

To bootstrap a project with mxenv, navigate to yout project folder and download
the ``Makefile`` and ``mxdev.ini``:

.. code-block:: sh

    wget https://raw.githubusercontent.com/conestack/mxenv/master/templates/Makefile
    wget https://raw.githubusercontent.com/conestack/mxenv/master/templates/mxdev.ini


Configuration
-------------

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


Templates
---------

run-tests
~~~~~~~~~

A script for running tests of python packages defined as mxdev sources. It
utilizes ``zope-testrunner``, thus expects it to be installed.

The generation target is ``scripts/run-tests.sh``.

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


run-coverage
~~~~~~~~~~~~

A script for running coverage tests of python packages defined as mxdev sources.
It utilizes ``zope-testrunner`` and ``coverage``, thus expects these packages to
be installed.

The generation target is ``scripts/run-coverage.sh``.

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


custom-pip
~~~~~~~~~~

A script which gets executed by ``make pip`` before remaining requirements are
installed. This can be used for custom pip invocation, e.g. for packages
requiring special build configuration or similar.

The generation target is ``scripts/custom-pip.sh``.

Configuration looks like so:

.. code-block:: ini

    [settings]
    # tell mxenv to generate custom pip script
    mxenv-templates = custom-pip

    # custom pip script related settings
    [mxenv-custom-pip]
    scripts =
        scripts/custom-pip-1.sh
        scripts/custom-pip-2.sh


system-dependencies
~~~~~~~~~~~~~~~~~~~

A config file read by ``make deps`` to install required system dependencies for
development.

Currently it depends on ``sudo`` and ``apt``.

The generation target is ``config/system-dependencies.conf``.

Configuration looks like so:

.. code-block:: ini

    [settings]
    # tell mxenv to generate system dependencies config file
    mxenv-templates = system-dependencies

    # system dependencies related settings
    [mxenv-system-dependencies]
    # system packages to install
    dependencies = build-essential curl


custom-clean
~~~~~~~~~~~~

A config file read by ``make clean`` to remove additionally things from file
system when cleaning up.

Configuration looks like so:

.. code-block:: ini

    [settings]
    # tell mxenv to generate custom clean config file
    mxenv-templates = custom-clean

    # custom clean related settings
    [mxenv-custom-clean]
    # additional items to remove at cleanup
    to-remove = item1 item2


Contributors
============

- Robert Niederreiter
