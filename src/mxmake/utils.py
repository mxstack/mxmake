from pathlib import Path

import os
import typing


NAMESPACE = "mxmake-"


def mxmake_files() -> Path:
    """Target folder for mxmake related file generation."""
    return Path(os.environ.get("MXMAKE_FILES", Path(".mxmake") / "files"))


def gh_actions_path() -> Path:
    """Target folder for github actions related file generation."""
    return Path(
        os.environ.get(
            "MXMAKE_GH_ACTIONS_PATH",
            Path(".github") / "workflows",
        )
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
