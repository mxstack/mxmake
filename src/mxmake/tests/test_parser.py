from mxmake import parser
from mxmake import templates
from mxmake import testing
from mxmake import topics

import unittest


class TestParser(unittest.TestCase):
    @testing.temp_directory
    def test_MakefileParser(self, tempdir):
        domains = [topics.get_domain("core.mxenv")]
        domains = topics.collect_missing_dependencies(domains)
        domains = topics.resolve_domain_dependencies(domains)
        domain_settings = {
            "core.base.DEPLOY_TARGETS": "",
            "core.base.RUN_TARGET": "",
            "core.base.CLEAN_FS": "",
            "core.base.INCLUDE_MAKEFILE": "include.mk",
            "core.base.EXTRA_PATH": "",
            "core.mxenv.PRIMARY_PYTHON": "python3",
            "core.mxenv.PYTHON_MIN_VERSION": "3.7",
            "core.mxenv.PYTHON_PACKAGE_INSTALLER": "pip",
            "core.mxenv.MXENV_UV_GLOBAL": "false",
            "core.mxenv.VENV_ENABLED": "true",
            "core.mxenv.VENV_CREATE": "true",
            "core.mxenv.VENV_FOLDER": "venv",
            "core.mxenv.MXDEV": "mxdev",
            "core.mxenv.MXMAKE": "mxmake",
        }

        factory = templates.template.lookup("makefile")
        template = factory(
            tempdir, domains, domain_settings, templates.get_template_environment()
        )

        template.write()

        makefile_path = tempdir / "Makefile"
        makefile_parser = parser.MakefileParser(makefile_path)

        self.assertEqual(
            makefile_parser.parse_setting(["SETTING?=value"], "SETTING"), "value"
        )
        self.assertEqual(
            makefile_parser.parse_setting(
                ["SETTING?=value\\", "\tvalue\\", "\tvalue"], "SETTING"
            ),
            "value\\\n\tvalue\\\n\tvalue",
        )
        self.assertEqual(
            makefile_parser.parse_setting(
                ["SETTING?=\\", "\tvalue\\", "\tvalue"], "SETTING"
            ),
            "\\\n\tvalue\\\n\tvalue",
        )

        self.assertEqual(makefile_parser.fqns, ["core.base", "core.mxenv"])
        self.assertEqual(
            makefile_parser.settings,
            {
                "core.base.DEPLOY_TARGETS": "",
                "core.base.RUN_TARGET": "",
                "core.base.CLEAN_FS": "",
                "core.base.INCLUDE_MAKEFILE": "include.mk",
                "core.base.EXTRA_PATH": "",
                "core.mxenv.PRIMARY_PYTHON": "python3",
                "core.mxenv.PYTHON_MIN_VERSION": "3.7",
                "core.mxenv.PYTHON_PACKAGE_INSTALLER": "pip",
                "core.mxenv.MXENV_UV_GLOBAL": "false",
                "core.mxenv.VENV_ENABLED": "true",
                "core.mxenv.VENV_CREATE": "true",
                "core.mxenv.VENV_FOLDER": "venv",
                "core.mxenv.MXDEV": "mxdev",
                "core.mxenv.MXMAKE": "mxmake",
            },
        )
        self.assertEqual(makefile_parser.topics, {"core": ["base", "mxenv"]})
