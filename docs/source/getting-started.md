# Getting started

## How to bootstrap a project with mxmake

Requirements:

- [`make`](https://www.gnu.org/software/make/) has to be installed.
  This is usually done by your system's package manager - as `sudo apt install make` on Debian-/Ubuntu-based systems.
- `Python 3` has to be installed with the `venv` module.
  Some system Python installations need extra action here - as `sudo apt install python-venv` on Debian-/Ubuntu-based systems.

Create a project folder and enter it:

```shell
mkdir myproject
cd myproject
```

You can either install *mxmake* globally or in a virtual environment.

```{note}
While *mxstack* is under development, use the unreleased `develop` branch and install with
`pip install git+https://github.com/mxstack/mxmake.git@develop`.
```

For global installation do a `pip install mxmake`, otherwise create a virtual environment, activate it, and install it like so:

```shell
python3 -m venv venv
. venv/bin/activate
pip install mxmake
```

Now create an initial `Makefile` with *mxmake*:

```shell
mxmake init
```

This is an interactive session and some questions are to be answered.
If in doubt select the `core` topic and then just hit {kbd}`Return` until done.

This creates an empty `mx.ini` (only if it does not exist already) and a `Makefile`.

## How to change the settings

The `Makefile` consists of three sections:

1. Header with configured topics/domains
1. Settings (for customization)
1. Makefile logic (do not edit)

The header is not intended for editing, thus it does not cause any harm by adding or removing domains here.
It is considered during the execution of "mxmake init".
Added or removed topics are checked or unchecked accordingly on the next run.

The settings section is where customization is happening.
Domains can provide configurable settings.
Setting names must be unique among all domains.
Thus they are often prefixed.

Each setting provides a description and an optional default value.

For details read the chapter [on topics and it's domains](topics-and-domains).
