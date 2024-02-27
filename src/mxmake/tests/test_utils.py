from mxmake import utils
from pathlib import Path

import os
import unittest


class TestUtils(unittest.TestCase):
    def test_namespace(self):
        self.assertEqual(utils.NAMESPACE, "mxmake-")

    def test_mxmake_files(self):
        self.assertEqual(utils.mxmake_files(), Path(".mxmake") / "files")
        os.environ["MXMAKE_FILES"] = "other"
        self.assertEqual(utils.mxmake_files(), Path("other"))
        del os.environ["MXMAKE_FILES"]

    def test_gh_actions_path(self):
        self.assertEqual(utils.gh_actions_path(), Path(".github") / "workflows")
        os.environ["MXMAKE_GH_ACTIONS_PATH"] = "other"
        self.assertEqual(utils.gh_actions_path(), Path("other"))
        del os.environ["MXMAKE_GH_ACTIONS_PATH"]

    def test_ns_name(self):
        self.assertEqual(utils.ns_name("foo"), "mxmake-foo")

    def test_list_value(self):
        self.assertEqual(utils.list_value(""), [])
        self.assertEqual(utils.list_value("a\nb c"), ["a", "b", "c"])
