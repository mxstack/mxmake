from contextlib import contextmanager
from mxmake import templates
from pathlib import Path

import doctest
import mxdev
import os
import shutil
import tempfile
import typing
import unittest


def temp_directory(fn):
    tempdir = Path(tempfile.mkdtemp())

    def wrapper(self):
        try:
            fn(self, tempdir)
        finally:
            shutil.rmtree(tempdir)

    return wrapper


@contextmanager
def reset_template_registry():
    registry_orgin = templates.template._registry
    templates.template._registry = {}
    try:
        yield
    finally:
        templates.template._registry = registry_orgin


class template_directory:
    def __init__(self, reset_registry: bool = False):
        self.reset_registry = reset_registry

    def __call__(self, fn: typing.Callable):
        def wrapper(*a):
            tempdir = Path(tempfile.mkdtemp())
            os.environ["MXMAKE_FILES"] = str(tempdir)
            os.environ["MXMAKE_GH_ACTIONS_PATH"] = str(tempdir)
            try:
                if self.reset_registry:
                    with reset_template_registry():
                        fn(*a, tempdir=tempdir)
                else:
                    fn(*a, tempdir=tempdir)
            finally:
                shutil.rmtree(tempdir)
                del os.environ["MXMAKE_FILES"]
                del os.environ["MXMAKE_GH_ACTIONS_PATH"]

        return wrapper


class TestConfiguration(mxdev.Configuration):
    def __init__(
        self,
        settings: dict[str, str] | None = None,
        overrides: dict[str, str] | None = None,
        ignore_keys: list[str] | None = None,
        packages: dict[str, dict[str, str]] | None = None,
        hooks: dict[str, dict[str, str]] | None = None,
    ):
        self.settings = settings if settings is not None else {}
        self.overrides = overrides if overrides is not None else {}
        self.ignore_keys = ignore_keys if ignore_keys is not None else []
        self.packages = packages if packages is not None else {}
        self.hooks = hooks if hooks is not None else {}


class RenderTestCase(unittest.TestCase):
    class Failure(Exception):
        pass

    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        self._checker = doctest.OutputChecker()
        self._optionflags = (
            doctest.NORMALIZE_WHITESPACE
            | doctest.ELLIPSIS
            | doctest.REPORT_ONLY_FIRST_FAILURE
        )

    def checkOutput(self, want, got, optionflags=None):
        if optionflags is None:
            optionflags = self._optionflags
        success = self._checker.check_output(want, got, optionflags)
        if not success:
            raise RenderTestCase.Failure(
                self._checker.output_difference(
                    doctest.Example(source="", want=want + "\n"),
                    got,
                    optionflags,
                )
            )
