from jinja2 import Environment
from jinja2 import FileSystemLoader
from mxmake import hook
from mxmake import templates
from mxmake import testing
from mxmake import topics
from mxmake import utils
from pathlib import Path

import doctest
import mxdev


EXPECTED_DIRECTORY = Path(__file__).parent / "expected"


class TestTemplates(testing.RenderTestCase):
    def test_template(self):
        with testing.reset_template_registry():

            @templates.template("template")
            class Template(templates.Template):
                pass

            self.assertEqual(templates.template._registry, {"template": Template})
            self.assertEqual(templates.template.lookup("template"), Template)
            with self.assertRaises(RuntimeError):
                templates.template.lookup("inexistent")

        self.assertEqual(
            templates.template._registry,
            {
                "additional_sources_targets": templates.AdditionalSourcesTargets,
                "dependencies.md": templates.Dependencies,
                "makefile": templates.Makefile,
                "mx.ini": templates.MxIni,
                "pip-conf": templates.PipConf,
                "proxy": templates.ProxyMk,
                "run-coverage": templates.CoverageScript,
                "run-tests": templates.TestScript,
                "topics.md": templates.Topics,
                "gh-actions-docs": templates.GHActionsDocs,
                "gh-actions-lint": templates.GHActionsLint,
                "gh-actions-test": templates.GHActionsTest,
                "gh-actions-typecheck": templates.GHActionsTypecheck,
                "plone-site": templates.PloneSitePy,
            },
        )

    @testing.template_directory()
    def test_Template(self, tempdir: Path):
        # cannot instantiate abstract template
        with self.assertRaises(TypeError):
            templates.Template()

        # create test template
        class Template(templates.Template):
            name = "template"
            target_folder = tempdir
            target_name = "target.out"
            template_name = "target.in"
            template_variables = {"param": "value"}

        # cannot write template without template environment
        template = Template()
        with self.assertRaises(RuntimeError):
            template.write()

        # write template
        with (tempdir / "target.in").open("w") as f:
            f.write("{{ param }}")
        environment = Environment(loader=FileSystemLoader(tempdir))
        template = Template(environment)
        template.write()
        with (tempdir / "target.out").open() as f:
            self.assertEqual(f.read(), "value")

        # check file mode
        self.assertEqual(template.file_mode, 0o644)
        # XXX: check file mode in file system

        # remove remplate
        removed = template.remove()
        self.assertTrue(removed)
        self.assertFalse((tempdir / "target.out").exists())
        self.assertFalse(template.remove())

    @testing.template_directory()
    def test_MxIniBoundTemplate(self, tempdir: str):
        # create test template
        class Template(templates.MxIniBoundTemplate):
            name = "template"
            target_folder = Path()
            target_name = ""
            template_name = ""
            template_variables = {}

        # template settings
        hooks: dict[str, dict] = {}
        template = Template(testing.TestConfiguration(hooks=hooks))
        self.assertEqual(template.settings, {})
        hooks["mxmake-template"] = {"key": "val"}
        self.assertEqual(template.settings, {"key": "val"})

    def test_ShellScriptTemplate(self):
        self.assertEqual(templates.ShellScriptTemplate.description, "")
        self.assertEqual(templates.ShellScriptTemplate.file_mode, 0o755)

    def test_EnvironmentTemplate(self):
        class Template(templates.EnvironmentTemplate):
            name = "template"
            target_folder = ""
            target_name = ""
            template_name = ""
            template_variables = {}

        hooks = {}
        template = Template(testing.TestConfiguration(hooks=hooks))
        self.assertEqual(template.env, {})
        hooks["mxmake-template"] = {"environment": "env"}
        self.assertEqual(template.env, {})
        hooks["mxmake-env"] = {"param": "value"}
        self.assertEqual(template.env, {"param": "value"})

    @testing.template_directory()
    def test_TestScript(self, tempdir):
        mxini = tempdir / "mx.ini"
        with mxini.open("w") as fd:
            fd.write(
                "[settings]\n"
                "mxmake-test-path = src\n"
                "    tests\n"
                "mxmake-test-runner = zope-testrunner\n"
                "[mxmake-env]\n"
                "ENV_PARAM = env_value\n"
                "[mxmake-run-tests]\n"
                "environment = env\n"
                "[package]\n"
                "url = https://github.com/org/package\n"
                "mxmake-test-path = src\n"
            )

        configuration = mxdev.Configuration(mxini, hooks=[hook.Hook()])
        factory = templates.template.lookup("run-tests")
        template = factory(configuration, templates.get_template_environment())

        self.assertEqual(template.description, "Run tests")
        self.assertEqual(template.target_folder, utils.mxmake_files())
        self.assertEqual(template.target_name, "run-tests.sh")
        self.assertEqual(template.template_name, "zope-testrunner-run-tests.sh")
        self.assertEqual(
            template.template_variables,
            {
                "description": "Run tests",
                "env": {"ENV_PARAM": "env_value"},
                "testpaths": ["sources/package/src", "src", "tests"],
                "testargs": "",
            },
        )
        self.assertEqual(template.package_paths("inexistent"), [])
        self.assertEqual(
            template.package_paths(utils.ns_name("test-path")),
            ["sources/package/src", "src", "tests"],
        )

        template.write()
        with (tempdir / "run-tests.sh").open() as f:
            self.checkOutput(
                """
                #!/usr/bin/env bash
                #
                # THIS SCRIPT IS GENERATED BY MXMAKE.
                # CHANGES MADE IN THIS FILE WILL BE LOST.
                #
                # Run tests
                set -e

                function setenv() {
                    export ENV_PARAM="env_value"
                }

                function unsetenv() {
                    unset ENV_PARAM
                }

                trap unsetenv ERR INT

                setenv
                zope-testrunner --auto-color --auto-progress \\
                    --test-path=sources/package/src \\
                    --test-path=src \\
                    --test-path=tests \\
                    --module=$1
                unsetenv
                exit 0
                """,
                f.read(),
            )

        with mxini.open("w") as fd:
            fd.write(
                "[settings]\n"
                "mxmake-test-runner = zope-testrunner\n"
                "[package]\n"
                "url = https://github.com/org/package\n"
                "mxmake-test-path = src\n"
            )

        configuration = mxdev.Configuration(mxini, hooks=[hook.Hook()])
        template = factory(configuration, templates.get_template_environment())
        template.write()
        with (tempdir / "run-tests.sh").open() as f:
            self.checkOutput(
                """
                #!/usr/bin/env bash
                #
                # THIS SCRIPT IS GENERATED BY MXMAKE.
                # CHANGES MADE IN THIS FILE WILL BE LOST.
                #
                # Run tests
                set -e

                zope-testrunner --auto-color --auto-progress \\
                    --test-path=sources/package/src \\
                    --module=$1

                exit 0
                """,
                f.read(),
            )

        with mxini.open("w") as fd:
            fd.write(
                "[settings]\n"
                "mxmake-test-runner = pytest\n"
                "[package]\n"
                "url = https://github.com/org/package\n"
                "mxmake-test-path = src\n"
            )

        configuration = mxdev.Configuration(mxini, hooks=[hook.Hook()])
        template = factory(configuration, templates.get_template_environment())
        template.write()
        with (tempdir / "run-tests.sh").open() as f:
            self.checkOutput(
                """
                #!/usr/bin/env bash
                #
                # THIS SCRIPT IS GENERATED BY MXMAKE.
                # CHANGES MADE IN THIS FILE WILL BE LOST.
                #
                # Run tests
                set -e

                pytest \\
                    sources/package/src

                exit 0
                """,
                f.read(),
            )

        with mxini.open("w") as fd:
            fd.write(
                "[settings]\n"
                "mxmake-test-runner = pytest\n"
                "[package]\n"
                "url = https://github.com/org/package\n"
            )

        configuration = mxdev.Configuration(mxini, hooks=[hook.Hook()])
        template = factory(configuration, templates.get_template_environment())
        template.write()
        with (tempdir / "run-tests.sh").open() as f:
            self.checkOutput(
                """
                #!/usr/bin/env bash
                #
                # THIS SCRIPT IS GENERATED BY MXMAKE.
                # CHANGES MADE IN THIS FILE WILL BE LOST.
                #
                # Run tests
                set -e

                pytest

                exit 0
                """,
                f.read(),
            )

    @testing.template_directory()
    def test_CoverageScript(self, tempdir):
        mxini = tempdir / "mx.ini"
        with mxini.open("w") as fd:
            fd.write(
                "[settings]\n"
                "mxmake-test-runner = zope-testrunner\n"
                "mxmake-test-path = src\n"
                "mxmake-source-path = src/local\n"
                "mxmake-omit-path =\n"
                "    src/local/file1.py\n"
                "    src/local/file2.py\n"
                "[mxmake-env]\n"
                "ENV_PARAM = env_value\n"
                "[mxmake-run-coverage]\n"
                "environment = env\n"
                "[package]\n"
                "url = https://github.com/org/package\n"
                "mxmake-test-path = src\n"
                "mxmake-source-path = src/package\n"
                "mxmake-omit-path =\n"
                "    src/package/file1.py\n"
                "    src/package/file2.py\n"
            )

        configuration = mxdev.Configuration(mxini, hooks=[hook.Hook()])
        factory = templates.template.lookup("run-coverage")
        template = factory(configuration, templates.get_template_environment())

        self.assertEqual(template.description, "Run coverage")
        self.assertEqual(template.target_folder, utils.mxmake_files())
        self.assertEqual(template.target_name, "run-coverage.sh")
        self.assertEqual(template.template_name, "zope-testrunner-run-coverage.sh")
        self.assertEqual(
            template.template_variables,
            {
                "description": "Run coverage",
                "env": {"ENV_PARAM": "env_value"},
                "testpaths": ["sources/package/src", "src"],
                "testargs": "",
                "sourcepaths": ["sources/package/src/package", "src/local"],
                "omitpaths": [
                    "sources/package/src/package/file1.py",
                    "sources/package/src/package/file2.py",
                    "src/local/file1.py",
                    "src/local/file2.py",
                ],
            },
        )
        self.assertEqual(template.package_paths("inexistent"), [])
        self.assertEqual(
            template.package_paths(utils.ns_name("test-path")),
            ["sources/package/src", "src"],
        )
        self.assertEqual(
            template.package_paths(utils.ns_name("source-path")),
            ["sources/package/src/package", "src/local"],
        )
        self.assertEqual(
            template.package_paths(utils.ns_name("omit-path")),
            [
                "sources/package/src/package/file1.py",
                "sources/package/src/package/file2.py",
                "src/local/file1.py",
                "src/local/file2.py",
            ],
        )

        template.write()
        with (tempdir / "run-coverage.sh").open() as f:
            self.checkOutput(
                """
                #!/usr/bin/env bash
                #
                # THIS SCRIPT IS GENERATED BY MXMAKE.
                # CHANGES MADE IN THIS FILE WILL BE LOST.
                #
                # Run coverage
                set -e

                function setenv() {
                    export ENV_PARAM="env_value"
                }

                function unsetenv() {
                    unset ENV_PARAM
                }

                trap unsetenv ERR INT

                setenv
                sources=(
                    sources/package/src/package
                    src/local
                )

                sources=$(printf ",%s" "${sources[@]}")
                sources=${sources:1}

                omits=(
                    sources/package/src/package/file1.py
                    sources/package/src/package/file2.py
                    src/local/file1.py
                    src/local/file2.py
                )

                omits=$(printf ",%s" "${omits[@]}")
                omits=${omits:1}
                coverage run \\
                    --source=$sources \\
                    --omit=$omits \\
                    -m zope.testrunner --auto-color --auto-progress \\
                    --test-path=sources/package/src \\
                    --test-path=src

                coverage report
                coverage html
                unsetenv
                exit 0
                """,
                f.read(),
            )

        with mxini.open("w") as fd:
            fd.write(
                "[settings]\n"
                "mxmake-test-runner = zope-testrunner\n"
                "[package]\n"
                "url = https://github.com/org/package\n"
                "mxmake-test-path = src\n"
                "mxmake-source-path = src/package\n"
            )

        configuration = mxdev.Configuration(mxini, hooks=[hook.Hook()])
        template = factory(configuration, templates.get_template_environment())
        template.write()
        with (tempdir / "run-coverage.sh").open() as f:
            self.checkOutput(
                """
                #!/usr/bin/env bash
                #
                # THIS SCRIPT IS GENERATED BY MXMAKE.
                # CHANGES MADE IN THIS FILE WILL BE LOST.
                #
                # Run coverage
                set -e

                sources=(
                    sources/package/src/package
                )

                sources=$(printf ",%s" "${sources[@]}")
                sources=${sources:1}


                coverage run \\
                    --source=$sources \\
                    -m zope.testrunner --auto-color --auto-progress \\
                    --test-path=sources/package/src

                coverage report
                coverage html

                exit 0
                """,
                f.read(),
            )

        with mxini.open("w") as fd:
            fd.write(
                "[settings]\n"
                "mxmake-test-runner = pytest\n"
                "[package]\n"
                "url = https://github.com/org/package\n"
                "mxmake-test-path = src\n"
                "mxmake-source-path = src/package\n"
            )

        configuration = mxdev.Configuration(mxini, hooks=[hook.Hook()])
        template = factory(configuration, templates.get_template_environment())
        template.write()
        with (tempdir / "run-coverage.sh").open() as f:
            self.checkOutput(
                """
                #!/usr/bin/env bash
                #
                # THIS SCRIPT IS GENERATED BY MXMAKE.
                # CHANGES MADE IN THIS FILE WILL BE LOST.
                #
                # Run coverage
                set -e

                sources=(
                    sources/package/src/package
                )

                sources=$(printf ",%s" "${sources[@]}")
                sources=${sources:1}


                coverage run \\
                    --source=$sources \\
                    -m pytest \\
                    sources/package/src

                coverage report
                coverage html

                exit 0
                """,
                f.read(),
            )

    @testing.template_directory()
    def test_PipConf(self, tempdir):
        mxini = tempdir / "mx.ini"
        with mxini.open("w") as fd:
            fd.write(
                "[settings]\n"
                "\n"
                "[mxmake-pip-conf]\n"
                "find-links =\n"
                "    file:///path/to/folder\n"
                "    https://tld.com/\n"
            )

        configuration = mxdev.Configuration(mxini, hooks=[hook.Hook()])
        factory = templates.template.lookup("pip-conf")
        template = factory(configuration, templates.get_template_environment())

        self.assertEqual(template.description, "Pip config")
        self.assertEqual(template.target_folder, utils.mxmake_files())
        self.assertEqual(template.target_name, "pip.conf")
        self.assertEqual(template.template_name, "pip.conf")
        self.assertEqual(
            template.template_variables,
            {"find_links": ["file:///path/to/folder", "https://tld.com/"]},
        )

        template.write()
        with (tempdir / "pip.conf").open() as f:
            self.checkOutput(
                """
                [global]
                find-links =
                    file:///path/to/folder
                    https://tld.com/
                """,
                f.read(),
            )

    @testing.template_directory()
    def test_AdditionalSourcesTargets(self, tempdir):
        factory = templates.template.lookup("additional_sources_targets")
        template = factory(["a", "b"], templates.get_template_environment())
        template.write()

        with (tempdir / "additional_sources_targets.mk").open() as f:
            self.checkOutput("ADDITIONAL_SOURCES_TARGETS=$(wildcard a b)", f.read())

    @testing.temp_directory
    def test_Makefile(self, tempdir):
        domains = [topics.get_domain("core.mxenv")]
        domains = topics.collect_missing_dependencies(domains)
        domains = topics.resolve_domain_dependencies(domains)
        domain_settings = {
            "core.base.DEPLOY_TARGETS": "",
            "core.base.RUN_TARGET": "",
            "core.base.CLEAN_FS": "",
            "core.base.INCLUDE_MAKEFILE": "include.mk",
            "core.base.EXTRA_PATH": "",
            "core.base.PROJECT_PATH_PYTHON": "",
            "core.mxenv.PRIMARY_PYTHON": "python3",
            "core.mxenv.PYTHON_MIN_VERSION": "3.10",
            "core.mxenv.PYTHON_PACKAGE_INSTALLER": "pip",
            "core.mxenv.UV_PYTHON": "$(PRIMARY_PYTHON)",
            "core.mxenv.VENV_ENABLED": "true",
            "core.mxenv.VENV_CREATE": "true",
            "core.mxenv.VENV_FOLDER": ".venv",
            "core.mxenv.MXDEV": "mxdev",
            "core.mxenv.MXMAKE": "mxmake",
            "core.mxenv.TOOL_RUNNER": "uvx",
        }
        factory = templates.template.lookup("makefile")
        template = factory(
            tempdir, domains, domain_settings, templates.get_template_environment()
        )

        template.write()
        print("Makefile written to", tempdir / "Makefile")
        with (
            (tempdir / "Makefile").open() as result,
            (EXPECTED_DIRECTORY / "Makefile").open() as expected,
        ):
            self.checkOutput(
                expected.read(), result.read(), optionflags=doctest.REPORT_UDIFF
            )

    @testing.temp_directory
    def test_MxIni(self, tempdir):
        domains = [
            topics.get_domain("qa.test"),
            topics.get_domain("qa.coverage"),
            topics.get_domain("applications.plone"),
        ]
        domains = topics.collect_missing_dependencies(domains)

        factory = templates.template.lookup("mx.ini")
        template = factory(tempdir, domains, templates.get_template_environment())

        template.write()
        with (tempdir / "mx.ini").open() as f:
            self.checkOutput(
                """
                [settings]
                threads = 5
                version-overrides =

                # mxmake related mxdev extensions

                # templates to generate
                mxmake-templates =
                    plone-site
                    run-coverage
                    run-tests

                # environment variables
                [mxmake-env]
                # VAR = value

                [mxmake-plone-site]
                distribution = volto
                extension_ids = plone.volto:default

                [mxmake-run-coverage]
                environment = env

                [mxmake-run-tests]
                environment = env

                """,
                f.read(),
            )

    @testing.template_directory()
    def test_PloneSite_all_defaults(self, tempdir):
        mxini = tempdir / "mx.ini"
        with mxini.open("w") as fd:
            fd.write("[settings]\n")
        configuration = mxdev.Configuration(mxini, hooks=[hook.Hook()])
        factory = templates.template.lookup("plone-site")
        template = factory(configuration, templates.get_template_environment())

        self.assertEqual(template.description, "Script to create or purge a Plone site")
        self.assertEqual(template.target_folder, utils.mxmake_files())
        self.assertEqual(template.target_name, "plone-site.py")
        self.assertEqual(template.template_name, "plone-site.py.tpl")
        self.assertEqual(
            template.template_variables,
            {
                "site": {
                    "default_language": "en",
                    "extension_ids": [],
                    "portal_timezone": "UTC",
                    "setup_content": False,
                    "site_id": "Plone",
                    "title": "Plone Site",
                }
            },
        )

        template.write()
        with (tempdir / "plone-site.py").open() as f:
            self.checkOutput(
                '''
                from AccessControl.SecurityManagement import newSecurityManager
                from plone.distribution.api.site import create
                from Products.CMFPlone.factory import _DEFAULT_PROFILE
                from Testing.makerequest import makerequest

                import os
                import transaction


                TRUTHY = frozenset(("t", "true", "y", "yes", "on", "1"))


                def asbool(value: str | bool | None) -> bool:
                    """Return the boolean value ``True`` if the case-lowered value of string
                    input ``s`` is a :term:`truthy string`. If ``s`` is already one of the
                    boolean values ``True`` or ``False``, return it.
                    """
                    if value is None:
                        return False
                    if isinstance(value, bool):
                        return value
                    return value.strip().lower() in TRUTHY


                PLONE_SITE_PURGE = asbool(os.getenv("PLONE_SITE_PURGE", "false"))
                PLONE_SITE_PURGE_FAIL_IF_NOT_EXISTS = asbool(
                    os.getenv("PLONE_SITE_PURGE_FAIL_IF_NOT_EXISTS", "true")
                )
                PLONE_SITE_CREATE = asbool(os.getenv("PLONE_SITE_CREATE", "true"))
                PLONE_SITE_CREATE_FAIL_IF_EXISTS = asbool(
                    os.getenv("PLONE_SITE_CREATE_FAIL_IF_EXISTS", "true")
                )

                config = {
                    "site_id": "Plone",
                    "title": "Plone Site",
                    "setup_content": "False",
                    "default_language": "en",
                    "portal_timezone": "UTC",
                    "profile_id": _DEFAULT_PROFILE,
                }
                config["setup_content"] = asbool(config["setup_content"])

                app = makerequest(globals()["app"])
                admin = app.acl_users.getUserById("admin")
                newSecurityManager(None, admin.__of__(app.acl_users))

                if PLONE_SITE_PURGE:
                    if config["site_id"] in app.objectIds():
                        app.manage_delObjects([config["site_id"]])
                        transaction.commit()
                        app._p_jar.sync()
                        print(f"Existing site with id={config['site_id']} purged!")
                        if not PLONE_SITE_CREATE:
                            print("Done.")
                            exit(0)
                    else:
                        print(f"Site with id={config['site_id']} does not exist!")
                        if PLONE_SITE_PURGE_FAIL_IF_NOT_EXISTS:
                            print("...failure!")
                            exit(1)
                        if not PLONE_SITE_CREATE:
                            print("Done.")
                            exit(0)

                if PLONE_SITE_CREATE:
                    if config["site_id"] in app.objectIds():
                        print(f"Site with id={config['site_id']} already exists!")
                        if PLONE_SITE_CREATE_FAIL_IF_EXISTS:
                            print("...failure!")
                            exit(1)
                        print("Done.")
                        exit(0)

                    site = create(app, "", config)
                    transaction.commit()
                    app._p_jar.sync()
                    print(f"New site with id={config['site_id']} created!")
                    print("Done.")
                ''',
                f.read(),
            )

    @testing.template_directory()
    def test_ProxyMk(self, tempdir):
        mxini = tempdir / "mx.ini"
        with mxini.open("w") as fd:
            fd.write(
                "[settings]\n"
                "\n"
                "[mxmake-proxy]\n"
                "folder =\n"
                "    applications:plone\n"
                "    i18n:*\n"
            )
        configuration = mxdev.Configuration(mxini, hooks=[hook.Hook()])
        factory = templates.template.lookup("proxy")
        template = factory(configuration, templates.get_template_environment())

        self.assertEqual(
            template.description,
            "Contains proxy targets for Makefiles of source folders",
        )
        self.assertEqual(template.target_folder, utils.mxmake_files())
        self.assertEqual(template.target_name, "proxy.mk")
        self.assertEqual(template.template_name, "proxy.mk")
        self.assertEqual(
            template.template_variables,
            {
                "targets": [
                    {"name": "plone-site-create", "folder": "folder"},
                    {"name": "plone-site-purge", "folder": "folder"},
                    {"name": "plone-site-recreate", "folder": "folder"},
                    {"name": "gettext-create", "folder": "folder"},
                    {"name": "gettext-update", "folder": "folder"},
                    {"name": "gettext-compile", "folder": "folder"},
                    {"name": "lingua-extract", "folder": "folder"},
                    {"name": "lingua", "folder": "folder"},
                ]
            },
        )

        template.write()
        with (tempdir / "proxy.mk").open() as f:
            self.checkOutput(
                """
                ##############################################################################
                # proxy targets
                ##############################################################################

                .PHONY: folder-plone-site-create
                folder-plone-site-create:
                	$(MAKE) -C "./folder/" plone-site-create

                .PHONY: folder-plone-site-purge
                folder-plone-site-purge:
                	$(MAKE) -C "./folder/" plone-site-purge

                .PHONY: folder-plone-site-recreate
                folder-plone-site-recreate:
                	$(MAKE) -C "./folder/" plone-site-recreate

                .PHONY: folder-gettext-create
                folder-gettext-create:
                	$(MAKE) -C "./folder/" gettext-create

                .PHONY: folder-gettext-update
                folder-gettext-update:
                	$(MAKE) -C "./folder/" gettext-update

                .PHONY: folder-gettext-compile
                folder-gettext-compile:
                	$(MAKE) -C "./folder/" gettext-compile

                .PHONY: folder-lingua-extract
                folder-lingua-extract:
                	$(MAKE) -C "./folder/" lingua-extract

                .PHONY: folder-lingua
                folder-lingua:
                	$(MAKE) -C "./folder/" lingua

                """,
                f.read(),
            )
