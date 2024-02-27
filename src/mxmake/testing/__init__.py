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
    templates.template._registry = dict()
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
        settings: typing.Dict[str, str] = {},
        overrides: typing.Dict[str, str] = {},
        ignore_keys: typing.List[str] = [],
        packages: typing.Dict[str, typing.Dict[str, str]] = {},
        hooks: typing.Dict[str, typing.Dict[str, str]] = {},
    ):
        self.settings = settings
        self.overrides = overrides
        self.ignore_keys = ignore_keys
        self.packages = packages
        self.hooks = hooks


class RenderTestCase(unittest.TestCase):
    class Example(object):
        def __init__(self, want):
            self.want = want + "\n"

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
                    RenderTestCase.Example(want), got, optionflags
                )
            )
