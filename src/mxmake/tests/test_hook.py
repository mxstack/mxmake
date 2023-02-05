from mxmake import hook
from mxmake import testing

import io
import mxdev
import os
import unittest


class TestHook(unittest.TestCase):
    @testing.template_directory()
    def test_Hook(self, tempdir):
        config_file = io.StringIO()
        config_file.write(
            "[settings]\n" "mxmake-templates = run-tests run-coverage inexistent"
        )
        config_file.seek(0)

        hook_ = hook.Hook()
        configuration = mxdev.Configuration(config_file, hooks=[hook_])
        state = mxdev.State(configuration=configuration)
        hook_.write(state)
        self.assertEqual(
            sorted(os.listdir(tempdir)), ["run-coverage.sh", "run-tests.sh"]
        )
