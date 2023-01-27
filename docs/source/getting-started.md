# How to get started

## How to bootstrap a project with mxmake

Requirements:

- [`make`](https://www.gnu.org/software/make/) has to be installed.
  This is usually done by your systems package manager, like `sudo apt install make` on Debian-/Ubuntu-based systems.
- `Python 3` has to be installed with the `venv` module.
  Some system Python installations need extra action here, like `sudo apt install python-venv` on Debian-/Ubuntu-based systems.

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

## How to change the settings

todo

