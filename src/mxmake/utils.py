import os
import typing


NAMESPACE = "mxmake-"


def mxenv_path() -> str:
    """MX environment path."""
    path = os.environ.get("MXMAKE_MXENV_PATH", os.path.join("venv", "bin"))
    if not path.endswith(os.path.sep):
        path = f"{path}{os.path.sep}"
    return path


def mxmake_files() -> str:
    """Target folder for mxmake related file generation."""
    return os.environ.get("MXMAKE_FILES", os.path.join(".mxmake", "files"))


def gh_actions_path() -> str:
    """Target folder for github actions related file generation."""
    return os.environ.get(
        "MXMAKE_GH_ACTIONS_PATH", os.path.join(".github", "workflows")
    )


def ns_name(name: str) -> str:
    """Return name prefixed by namespace."""
    return f"{NAMESPACE}{name}"


def list_value(value: str) -> typing.List[str]:
    """Convert string value from config file to list of strings. Separator is
    space. Supports newline.
    """
    if not value:
        return list()
    return [v.strip() for v in value.replace("\n", " ").strip().split(" ")]
