from mxmake import hook
from mxmake import testing

import mxdev
import os
import pathlib
import unittest


class TestHook(unittest.TestCase):
    @testing.template_directory()
    def test_Hook(self, tempdir):
        mxini = pathlib.Path(tempdir, "mx.ini")
        with mxini.open("w") as fd:
            fd.write(
                "[settings]\n" "mxmake-templates = run-tests run-coverage inexistent"
            )

        hook_ = hook.Hook()
        configuration = mxdev.Configuration(mxini, hooks=[hook_])
        state = mxdev.State(configuration=configuration)
        hook_.write(state)
        self.assertEqual(
            sorted(os.listdir(tempdir)), ["mx.ini", "run-coverage.sh", "run-tests.sh"]
        )
