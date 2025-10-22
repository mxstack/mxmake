# Preseeds

## Introduction

It is possible to pass configuration preseeds when creating a new project
with `mxmake init`. This is useful if you have recurring default settings
when creating projects with `mxmake`.

Preseeds are contained in yaml files and have the following format:

```yaml
# topics to include
topics:
  # include topic core
  core:
    # include domain mxenv
    mxenv:
      # set PYTHON_MIN_VERSION and PYTHON_PACKAGE_INSTALLER
      PYTHON_MIN_VERSION: 3.10
      PYTHON_PACKAGE_INSTALLER: uv
  qa:
    # include domains from qa topic but do not override default settings
    ruff:
    test:
    coverage:
# generate mx ini if not exists
mx-ini: true
# generate CI files from templates
ci-templates:
- gh-actions-test
```

Now initialize the project with the preseeds:

```shell
$ mxmake init -p preseeds.yaml
```

## Examples

### Create a simple Python project

mxmake was made for the easy management of Python projects.

This example shows how to create a very minimal project structure to build on.
[mxdev][https://pypi.org/project/mxdev/] is integrated to manage versions, sources and more.

Preconditions for this example:
[uv](https://docs.astral.sh/uv/) is installed in the `PATH`.

Use `uv init hello-world` to generate a minimal skeleton package.

Enter the `hello-world-` directory and create a file `preseed.yaml`:

```yaml
topics:
  core:
    mxenv:
      PYTHON_MIN_VERSION: "3.10"
      PYTHON_PACKAGE_INSTALLER: uv
    sources:
  qa:
    ruff
    mypy
    test

mx-ini: true
```

Then run:

```bash
uv mxmake init -p preseed.yaml
```

Edit the `mx.ini` and insert after the first line a new line: `main-package = -e .`.

Now run:
```bash
make install
```

Now you have a basic environment to build on.
`make format` wont work, because it looks in the `./src` directory, but this can be fixed by restrcuturing the code.
You may want to use a different skeleton generator than "uv" here.


### Create a Makefile for a simple Plone backend

[Plone](https://plone.org) is an enterprise CMS written in Python (backend) and Javascript (frontend).
mxmake helps to create the backend.
It helps to develop and manage code for integrations and distributions, Plone-add-ons and the Plone-core-development itself.

Preconditions for this example:
[uv](https://docs.astral.sh/uv/) is installed in the `PATH`.

Go in a fresh directory and create a file `plone-preseed.yaml`:

```yaml
topics:
  core:
    base:
      RUN_TARGET: zope-start
    mxenv:
      PYTHON_MIN_VERSION: "3.10"
      PYTHON_PACKAGE_INSTALLER: uv
  applications:
    zope:
    plone:
mx-ini: true
```

Run:
```bash
mxmake init -p plone-preseed.yaml
echo "-c https://dist.plone.org/release/6.1-latest/constraints.txt" >requirements.txt
echo "Plone" >>requirements.txt
```

In the
- 1st line the `Makefile` and the `mx.ini` configuration is generated,
- 2nd line a Python requirements is created with a reference to a Plone release file, pinning the versions,
- 3rd line the Plone package is declared as the main package.

Now "make" is now ready to run.

After the first command watch out for a line with the generated password.
It looks like so:

> Generated password for initial user 'admin' is: SOME-CRYPTIC-PASSWORD

Execute:

```bash
make plone-site-create
make run
```

In your browser go to [localhost:8080](http://localhost:8080).
There runs a Plone with a backend ready for Volto (the frontend application for Plone) installed.

This can be combined with the above example for a Python package to create self-contained reproducible environments for development and deployment.
