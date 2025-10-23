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

To update an existing Makefile without beeing prompted interactive, run `mxmake update`.

## How to change the settings

The `Makefile` consists of three sections:

1. Header with configured topics/domains
1. Settings (for customization)
1. Makefile logic (do not edit)

The header is not intended for editing, thus it does not cause any harm by adding or removing domains here.
It is considered during the execution of `mxmake init` respective `mxmake update`.
Added or removed topics are checked or unchecked accordingly on the next run.

The settings section is where customization is happening.
Domains can provide configurable settings.
Setting names must be unique among all domains.
Thus they are usually prefixed.

Each setting provides a description and an optional default value.

For details read the chapter [on topics and it's domains](topics-and-domains).

Do not add custom settings to settings section.
They will be lost on next `mxmake init` respective `mxmake update` run.

### Python Package Installer

By default, mxmake uses `pip` as the package installer. You can switch to [UV](https://docs.astral.sh/uv/) by setting `PYTHON_PACKAGE_INSTALLER=uv` in the settings section.

When using UV, mxmake automatically detects if UV is installed globally or installs it locally in the virtual environment.

```{note}
When using UV, you should explicitly set `UV_PYTHON` to specify which Python version UV should use. While `UV_PYTHON` currently defaults to `PRIMARY_PYTHON` for backward compatibility, this default may change in future versions. Set `UV_PYTHON` explicitly to avoid surprises.
```

Example:
```makefile
PRIMARY_PYTHON?=python3
PYTHON_PACKAGE_INSTALLER?=uv
UV_PYTHON?=3.14
```

## How to use on the Windows operating system

mxmake works excellent on Windows!

On Windows it needs a Bash shell.
Fortunately the GIT VCS comes with the a fully function Bash, the git-bash.
Please follow  [GIT's official installation instructions](https://git-scm.com/download/win).

Install [make as described here](https://gist.github.com/evanwill/0207876c3243bbb6863e65ec5dc3f058#make)

Further you need a [Python >=3.10 installation.](https://www.python.org/downloads/windows/).

Dependent on the topics and domains you use, you may need to install additional software, but this is no different from Linux/OSX.

## Troubleshooting

### UV not found error

If you get an error that UV is not found, install it. See the [official UV installation guide](https://docs.astral.sh/uv/getting-started/installation/) for detailed instructions.

```shell
# Global installation (recommended)
pip install uv

# Or use the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, run `mxmake update` to regenerate the Makefile.

### Python version mismatch

If UV uses a different Python version than expected, explicitly set `UV_PYTHON` in your Makefile settings:

```makefile
UV_PYTHON?=3.14
```

Then run `make install` again.

### Tests not running

If `make test` fails with "command not found", ensure the test runner script was generated:

```shell
ls .mxmake/files/run-tests.sh
```

If missing, check that your `mx.ini` includes `mxmake-templates = run-tests` and run `make install` to regenerate files.

### Make command not found

On Ubuntu/Debian: `sudo apt install make`
On macOS: Install Xcode Command Line Tools: `xcode-select --install`
On Windows: See [installation instructions](https://gist.github.com/evanwill/0207876c3243bbb6863e65ec5dc3f058#make)

### Settings not taking effect

Settings are only applied when you explicitly set them. If a setting has `?=`, it uses the default unless overridden.

Example: Change `PRIMARY_PYTHON?=python3.12` to `PRIMARY_PYTHON=python3.14` (remove the `?`) to force that value.

Note that environment variables always override Makefile settings. Check if a setting is defined in your shell environment:

```shell
echo $PRIMARY_PYTHON
```

After changing settings, run `make install` to apply them.

### Regenerating the Makefile

To add or remove domains without interactive prompts, use:

```shell
mxmake update
```

This preserves your current settings and updates the Makefile logic. To start fresh interactively, use `mxmake init`.

After upgrading mxmake to a newer version, run `mxmake update` to apply new features and improvements from the upgraded version.
