import os
import typing


NAMESPACE = 'mxenv-'


def venv_folder() -> str:
    """Folder containing the virtual environment."""
    return os.environ.get('MXENV_VENV_FOLDER', os.path.join('venv'))


def scripts_folder() -> str:
    """Target folder for script generation."""
    return os.environ.get('MXENV_SCRIPTS_FOLDER', os.path.join('venv', 'bin'))


def config_folder() -> str:
    """Target folder for config generation."""
    return os.environ.get('MXENV_CONFIG_FOLDER', os.path.join('cfg'))


def ns_name(name: str) -> str:
    """Return name prefixed by namespace."""
    return f'{NAMESPACE}{name}'


def list_value(value: str) -> typing.List[str]:
    """Convert string value from config file to list of strings. Separator is
    space. Supports newline.
    """
    if not value:
        return list()
    return [v.strip() for v in value.replace('\n', ' ').strip().split(' ')]
