from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from jinja2 import Environment
from jinja2 import FileSystemLoader
from mxmake import hook
from mxmake import main
from mxmake import parser
from mxmake import templates
from mxmake import topics
from mxmake import utils

import configparser
import doctest
import io
import mxdev
import os
import shutil
import tempfile
import typing
import unittest


###############################################################################
# helpers
###############################################################################


def temp_directory(fn):
    tempdir = tempfile.mkdtemp()

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
            tempdir = tempfile.mkdtemp()
            os.environ["MXMAKE_MXENV_PATH"] = tempdir
            os.environ["MXMAKE_SCRIPTS_FOLDER"] = tempdir
            os.environ["MXMAKE_CONFIG_FOLDER"] = tempdir
            try:
                if self.reset_registry:
                    with reset_template_registry():
                        fn(*a, tempdir=tempdir)
                else:
                    fn(*a, tempdir=tempdir)
            finally:
                shutil.rmtree(tempdir)
                del os.environ["MXMAKE_MXENV_PATH"]
                del os.environ["MXMAKE_SCRIPTS_FOLDER"]
                del os.environ["MXMAKE_CONFIG_FOLDER"]

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


###############################################################################
# Test utils
###############################################################################


class TestUtils(unittest.TestCase):
    def test_namespace(self):
        self.assertEqual(utils.NAMESPACE, "mxmake-")

    def test_mxenv_path(self):
        self.assertEqual(utils.mxenv_path(), os.path.join("venv", "bin") + os.path.sep)
        os.environ["MXMAKE_MXENV_PATH"] = "other"
        self.assertEqual(utils.mxenv_path(), "other" + os.path.sep)
        del os.environ["MXMAKE_MXENV_PATH"]

    def test_scripts_folder(self):
        self.assertEqual(utils.scripts_folder(), os.path.join("venv", "bin"))
        os.environ["MXMAKE_SCRIPTS_FOLDER"] = "other"
        self.assertEqual(utils.scripts_folder(), "other")
        del os.environ["MXMAKE_SCRIPTS_FOLDER"]

    def test_config_folder(self):
        self.assertEqual(utils.config_folder(), "cfg")
        os.environ["MXMAKE_CONFIG_FOLDER"] = "other"
        self.assertEqual(utils.config_folder(), "other")
        del os.environ["MXMAKE_CONFIG_FOLDER"]

    def test_ns_name(self):
        self.assertEqual(utils.ns_name("foo"), "mxmake-foo")

    def test_list_value(self):
        self.assertEqual(utils.list_value(""), [])
        self.assertEqual(utils.list_value("a\nb c"), ["a", "b", "c"])


###############################################################################
# Test teamplates
###############################################################################


class TestTemplates(RenderTestCase):
    def test_template(self):
        with reset_template_registry():

            @templates.template("template")
            class Template(templates.Template):
                pass

            self.assertEqual(templates.template._registry, dict(template=Template))
            self.assertEqual(templates.template.lookup("inexistent"), None)
            self.assertEqual(templates.template.lookup("template"), Template)

        self.assertEqual(
            templates.template._registry,
            {
                "topics.md": templates.Topics,
                "makefile": templates.Makefile,
                "mx.ini": templates.MxIni,
                "run-coverage": templates.CoverageScript,
                "run-tests": templates.TestScript,
            },
        )

    @template_directory()
    def test_Template(self, tempdir: str):
        # cannot instantiate abstract template
        with self.assertRaises(TypeError):
            templates.Template()  # type: ignore

        # create test template
        class Template(templates.Template):
            name = "template"
            target_folder = tempdir
            target_name = "target.out"
            template_name = "target.in"
            template_variables = dict(param="value")

        # cannot write template without template environment
        template = Template()
        with self.assertRaises(RuntimeError):
            template.write()

        # write template
        with open(os.path.join(tempdir, "target.in"), "w") as f:
            f.write("{{ param }}")
        environment = Environment(loader=FileSystemLoader(tempdir))
        template = Template(environment)
        template.write()
        with open(os.path.join(tempdir, "target.out")) as f:
            self.assertEqual(f.read(), "value")

        # check file mode
        self.assertEqual(template.file_mode, 0o644)
        # XXX: check file mode in file system

        # remove remplate
        removed = template.remove()
        self.assertTrue(removed)
        self.assertFalse(os.path.exists(os.path.join(tempdir, "target.out")))
        self.assertFalse(template.remove())

    @template_directory()
    def test_MxIniBoundTemplate(self, tempdir: str):
        # create test template
        class Template(templates.MxIniBoundTemplate):
            name = "template"
            target_folder = ""
            target_name = ""
            template_name = ""
            template_variables = {}

        # template settings
        hooks: typing.Dict[str, typing.Dict] = {}
        template = Template(TestConfiguration(hooks=hooks))
        self.assertEqual(template.settings, dict())
        hooks["mxmake-template"] = dict(key="val")
        self.assertEqual(template.settings, dict(key="val"))

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
        template = Template(TestConfiguration(hooks=hooks))
        self.assertEqual(template.env, {})
        hooks["mxmake-template"] = {"environment": "env"}
        self.assertEqual(template.env, {})
        hooks["mxmake-env"] = {"param": "value"}
        self.assertEqual(template.env, {"param": "value"})

    @template_directory()
    def test_TestScript(self, tempdir):
        config_file = io.StringIO()
        config_file.write(
            "[settings]\n"
            "[mxmake-env]\n"
            "ENV_PARAM = env_value\n"
            "[mxmake-run-tests]\n"
            "environment = env\n"
            "[package]\n"
            "url = https://github.com/org/package\n"
            "mxmake-test-path = src\n"
        )
        config_file.seek(0)

        configuration = mxdev.Configuration(config_file, hooks=[hook.Hook()])
        factory = templates.template.lookup("run-tests")
        template = factory(configuration, templates.get_template_environment())

        self.assertEqual(template.description, "Run tests")
        self.assertEqual(template.target_folder, utils.scripts_folder())
        self.assertEqual(template.target_name, "run-tests.sh")
        self.assertEqual(template.template_name, "run-tests.sh")
        self.assertEqual(
            template.template_variables,
            {
                "description": "Run tests",
                "env": {"ENV_PARAM": "env_value"},
                "testpaths": ["sources/package/src"],
                "mxenv_path": tempdir + os.path.sep,
            },
        )
        self.assertEqual(template.package_paths("inexistent"), [])
        self.assertEqual(
            template.package_paths(utils.ns_name("test-path")), ["sources/package/src"]
        )

        template.write()
        with open(os.path.join(tempdir, "run-tests.sh")) as f:
            self.checkOutput(
                """
                #!/bin/bash
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

                /.../zope-testrunner --auto-color --auto-progress \\
                    --test-path=sources/package/src \\
                    --module=$1

                unsetenv

                exit 0
                """,
                f.read(),
            )

        config_file = io.StringIO()
        config_file.write(
            "[settings]\n"
            "[package]\n"
            "url = https://github.com/org/package\n"
            "mxmake-test-path = src\n"
        )
        config_file.seek(0)

        configuration = mxdev.Configuration(config_file, hooks=[hook.Hook()])
        template = factory(configuration, templates.get_template_environment())
        template.write()
        with open(os.path.join(tempdir, "run-tests.sh")) as f:
            self.checkOutput(
                """
                #!/bin/bash
                #
                # THIS SCRIPT IS GENERATED BY MXMAKE.
                # CHANGES MADE IN THIS FILE WILL BE LOST.
                #
                # Run tests
                set -e

                /.../zope-testrunner --auto-color --auto-progress \\
                    --test-path=sources/package/src \\
                    --module=$1

                exit 0
                """,
                f.read(),
            )

    @template_directory()
    def test_CoverageScript(self, tempdir):
        config_file = io.StringIO()
        config_file.write(
            "[settings]\n"
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
        config_file.seek(0)

        configuration = mxdev.Configuration(config_file, hooks=[hook.Hook()])
        factory = templates.template.lookup("run-coverage")
        template = factory(configuration, templates.get_template_environment())

        self.assertEqual(template.description, "Run coverage")
        self.assertEqual(template.target_folder, utils.scripts_folder())
        self.assertEqual(template.target_name, "run-coverage.sh")
        self.assertEqual(template.template_name, "run-coverage.sh")
        self.assertEqual(
            template.template_variables,
            {
                "description": "Run coverage",
                "env": {"ENV_PARAM": "env_value"},
                "testpaths": ["sources/package/src"],
                "sourcepaths": ["sources/package/src/package"],
                "omitpaths": [
                    "sources/package/src/package/file1.py",
                    "sources/package/src/package/file2.py",
                ],
                "mxenv_path": tempdir + os.path.sep,
            },
        )
        self.assertEqual(template.package_paths("inexistent"), [])
        self.assertEqual(
            template.package_paths(utils.ns_name("test-path")), ["sources/package/src"]
        )
        self.assertEqual(
            template.package_paths(utils.ns_name("source-path")),
            ["sources/package/src/package"],
        )
        self.assertEqual(
            template.package_paths(utils.ns_name("omit-path")),
            [
                "sources/package/src/package/file1.py",
                "sources/package/src/package/file2.py",
            ],
        )

        template.write()
        with open(os.path.join(tempdir, "run-coverage.sh")) as f:
            self.checkOutput(
                """
                #!/bin/bash
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
                )

                sources=$(printf ",%s" "${sources[@]}")
                sources=${sources:1}

                omits=(
                    sources/package/src/package/file1.py
                    sources/package/src/package/file2.py
                )

                omits=$(printf ",%s" "${omits[@]}")
                omits=${omits:1}

                /.../coverage run \\
                    --source=$sources \\
                    --omit=$omits \\
                    -m zope.testrunner --auto-color --auto-progress \\
                    --test-path=sources/package/src

                /.../coverage report
                /.../coverage html

                unsetenv

                exit 0
                """,
                f.read(),
            )

        config_file = io.StringIO()
        config_file.write(
            "[settings]\n"
            "[package]\n"
            "url = https://github.com/org/package\n"
            "mxmake-test-path = src\n"
            "mxmake-source-path = src/package\n"
        )
        config_file.seek(0)

        configuration = mxdev.Configuration(config_file, hooks=[hook.Hook()])
        template = factory(configuration, templates.get_template_environment())
        template.write()
        with open(os.path.join(tempdir, "run-coverage.sh")) as f:
            self.checkOutput(
                """
                #!/bin/bash
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

                /.../coverage run \\
                    --source=$sources \\
                    -m zope.testrunner --auto-color --auto-progress \\
                    --test-path=sources/package/src

                /.../coverage report
                /.../coverage html

                exit 0
                """,
                f.read(),
            )

    @temp_directory
    def test_Makefile(self, tempdir):
        domains = [topics.get_domain("core.mxenv")]
        domains = topics.collect_missing_dependencies(domains)
        domains = topics.resolve_domain_dependencies(domains)
        domain_settings = {
            "core.base.DEPLOY_TARGETS": "",
            "core.mxenv.PYTHON_BIN": "python3",
            "core.mxenv.PYTHON_MIN_VERSION": "3.7",
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
        with open(os.path.join(tempdir, "Makefile")) as f:
            self.checkOutput(
                """
                ##############################################################################
                # THIS FILE IS GENERATED BY MXMAKE
                #
                # SETTINGS (ALL CHANGES MADE BELOW SETTINGS WILL BE LOST)
                #
                # DOMAINS:
                #: core.base
                #: core.mxenv
                ##############################################################################

                ## core.base

                # `deploy` target dependencies.
                # No default value.
                DEPLOY_TARGETS?=

                ## core.mxenv

                # Python interpreter to use.
                # Default: python3
                PYTHON_BIN?=python3

                # Minimum required Python version.
                # Default: 3.7
                PYTHON_MIN_VERSION?=3.7

                # Flag whether to use virtual environment. If `false`, the global
                # interpreter is used.
                # Default: true
                VENV_ENABLED?=true

                # Flag whether to create a virtual environment. If set to `false`
                # and `VENV_ENABLED` is `true`, `VENV_FOLDER` is expected to point to an
                # existing virtual environment.
                # Default: true
                VENV_CREATE?=true

                # The folder of the virtual environment.
                # Default: venv
                VENV_FOLDER?=venv

                # mxdev to install in virtual environment.
                # Default: https://github.com/mxstack/mxdev/archive/main.zip
                MXDEV?=mxdev

                # mxmake to install in virtual environment.
                # Default: https://github.com/mxstack/mxmake/archive/develop.zip
                MXMAKE?=mxmake

                ##############################################################################
                # END SETTINGS - DO NOT EDIT BELOW THIS LINE
                ##############################################################################

                INSTALL_TARGETS?=
                DIRTY_TARGETS?=
                CLEAN_TARGETS?=
                PURGE_TARGETS?=

                # Defensive settings for make: https://tech.davis-hansson.com/p/make/
                SHELL:=bash
                .ONESHELL:
                # for Makefile debugging purposes add -x to the .SHELLFLAGS
                .SHELLFLAGS:=-eu -o pipefail -O inherit_errexit -c
                .SILENT:
                .DELETE_ON_ERROR:
                MAKEFLAGS+=--warn-undefined-variables
                MAKEFLAGS+=--no-builtin-rules

                # Sentinel files
                SENTINEL_FOLDER?=.mxmake-sentinels
                SENTINEL?=$(SENTINEL_FOLDER)/about.txt
                $(SENTINEL):
                    @mkdir -p $(SENTINEL_FOLDER)
                    @echo "Sentinels for the Makefile process." > $(SENTINEL)

                ##############################################################################
                # mxenv
                ##############################################################################

                # Check if given Python is installed
                ifeq (,$(shell which $(PYTHON_BIN)))
                $(error "PYTHON=$(PYTHON_BIN) not found in $(PATH)")
                endif

                # Check if given Python version is ok
                PYTHON_VERSION_OK=$(shell $(PYTHON_BIN) -c "import sys; print((int(sys.version_info[0]), int(sys.version_info[1])) >= tuple(map(int, '$(PYTHON_MIN_VERSION)'.split('.'))))")
                ifeq ($(PYTHON_VERSION_OK),0)
                $(error "Need Python >= $(PYTHON_MIN_VERSION)")
                endif

                # Check if venv folder is configured if venv is enabled
                ifeq ($(shell [[ "$(VENV_ENABLED)" == "true" && "$(VENV_FOLDER)" == "" ]] && echo "true"),"true")
                $(error "VENV_FOLDER must be configured if VENV_ENABLED is true")
                endif

                # determine the executable path
                ifeq ("$(VENV_ENABLED)", "true")
                MXENV_PATH=$(VENV_FOLDER)/bin/
                else
                MXENV_PATH=
                endif

                MXENV_TARGET:=$(SENTINEL_FOLDER)/mxenv.sentinel
                $(MXENV_TARGET): $(SENTINEL)
                ifeq ("$(VENV_ENABLED)", "true")
                    @echo "Setup Python Virtual Environment under '$(VENV_FOLDER)'"
                    @$(PYTHON_BIN) -m venv $(VENV_FOLDER)
                endif
                    @$(MXENV_PATH)pip install -U pip setuptools wheel
                    @$(MXENV_PATH)pip install -U $(MXDEV)
                    @$(MXENV_PATH)pip install -U $(MXMAKE)
                    @touch $(MXENV_TARGET)

                .PHONY: mxenv
                mxenv: $(MXENV_TARGET)

                .PHONY: mxenv-dirty
                mxenv-dirty:
                    @rm -f $(MXENV_TARGET)

                .PHONY: mxenv-clean
                mxenv-clean: mxenv-dirty
                ifeq ("$(VENV_ENABLED)", "true")
                    @rm -rf $(VENV_FOLDER)
                else
                    @$(MXENV_PATH)pip uninstall -y $(MXDEV)
                    @$(MXENV_PATH)pip uninstall -y $(MXMAKE)
                endif

                INSTALL_TARGETS+=mxenv
                DIRTY_TARGETS+=mxenv-dirty
                CLEAN_TARGETS+=mxenv-clean

                ##############################################################################
                # Default targets
                ##############################################################################

                INSTALL_TARGET:=$(SENTINEL_FOLDER)/install.sentinel
                $(INSTALL_TARGET): $(INSTALL_TARGETS)
                    @touch $(INSTALL_TARGET)

                .PHONY: install
                install: $(INSTALL_TARGET)
                    @touch $(INSTALL_TARGET)

                .PHONY: deploy
                deploy: $(DEPLOY_TARGETS)

                .PHONY: dirty
                dirty: $(DIRTY_TARGETS)
                    @rm -f $(INSTALL_TARGET)

                .PHONY: clean
                clean: dirty $(CLEAN_TARGETS)
                    @rm -rf $(CLEAN_TARGETS) .mxmake-sentinels

                .PHONY: purge
                purge: clean $(PURGE_TARGETS)

                .PHONY: runtime-clean
                runtime-clean:
                    @echo "Remove runtime artifacts, like byte-code and caches."
                    @find . -name '*.py[c|o]' -delete
                    @find . -name '*~' -exec rm -f {} +
                    @find . -name '__pycache__' -exec rm -fr {} +
                """,
                f.read(),
            )

    @temp_directory
    def test_MxIni(self, tempdir):
        domains = [
            topics.get_domain("qa.test"),
            topics.get_domain("qa.coverage"),
        ]
        domains = topics.collect_missing_dependencies(domains)

        factory = templates.template.lookup("mx.ini")
        template = factory(tempdir, domains, templates.get_template_environment())

        template.write()
        with open(os.path.join(tempdir, "mx.ini")) as f:
            self.checkOutput(
                """
                [settings]
                threads = 5
                version-overrides =

                # mxmake related mxdev extensions

                # templates to generate
                mxmake-templates =
                    run-coverage
                    run-tests

                # environment variables
                [mxmake-env]
                # VAR = value

                [mxmake-run-coverage]
                environment = env

                [mxmake-run-tests]
                environment = env

                """,
                f.read(),
            )


###############################################################################
# Test parser
###############################################################################


class TestParser(unittest.TestCase):
    @temp_directory
    def test_MakefileParser(self, tempdir):
        domains = [topics.get_domain("core.mxenv")]
        domains = topics.collect_missing_dependencies(domains)
        domains = topics.resolve_domain_dependencies(domains)
        domain_settings = {
            "core.base.DEPLOY_TARGETS": "",
            "core.mxenv.PYTHON_BIN": "python3",
            "core.mxenv.PYTHON_MIN_VERSION": "3.7",
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

        makefile_path = os.path.join(tempdir, "Makefile")
        makefile_parser = parser.MakefileParser(makefile_path)
        self.assertEqual(makefile_parser.fqns, ["core.base", "core.mxenv"])
        self.assertEqual(
            makefile_parser.settings,
            {
                "core.base.DEPLOY_TARGETS": "",
                "core.mxenv.PYTHON_BIN": "python3",
                "core.mxenv.PYTHON_MIN_VERSION": "3.7",
                "core.mxenv.VENV_ENABLED": "true",
                "core.mxenv.VENV_CREATE": "true",
                "core.mxenv.VENV_FOLDER": "venv",
                "core.mxenv.MXDEV": "mxdev",
                "core.mxenv.MXMAKE": "mxmake",
            },
        )
        self.assertEqual(makefile_parser.topics, {"core": ["base", "mxenv"]})


###############################################################################
# Test hook
###############################################################################


class TestHook(unittest.TestCase):
    @template_directory()
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


###############################################################################
# Test topics
###############################################################################

MAKEFILE_TEMPLATE = """
#:[example]
#:title = Title
#:description = Description
#:depends =
#:    dependency-1
#:    dependency-2
#:
#:[target.example]
#:description = Build example
#:
#:[target.example-dirty]
#:description = Rebuild example on next make run
#:
#:[target.example-clean]
#:description = Clean example
#:
#:[setting.SETTING_A]
#:description = Setting A
#:default = A
#:
#:[setting.SETTING_B]
#:description = Setting B
#:default = B

SETTING_A?=A
SETTING_B?=B

EXAMPLE_TARGET:=$(SENTINEL_FOLDER)/example.sentinel
$(EXAMPLE_TARGET): $(SENTINEL)
	@echo "Building example"
	@touch $(EXAMPLE_TARGET)

.PHONY: example
example: $(EXAMPLE_TARGET)

.PHONY: example-dirty
example-dirty:
	@rm -f $(EXAMPLE_TARGET)

.PHONY: example-clean
example-clean:
	@rm -f $(EXAMPLE_TARGET)
"""


@dataclass
class TestDomain(topics.Domain):
    depends_: typing.List[str]

    @property
    def depends(self) -> typing.List[str]:
        return self.depends_


class TestDomains(unittest.TestCase):
    def test_load_topics(self):
        topics_ = topics.load_topics()
        self.assertTrue(topics.core in topics_)
        self.assertTrue(topics.ldap in topics_)

    def test_get_topic(self):
        topic = topics.get_topic("core")
        self.assertEqual(topic.name, "core")

    def test_get_domain(self):
        domain = topics.get_domain("core.mxenv")
        self.assertEqual(domain.fqn, "core.mxenv")

    @temp_directory
    def test_Domain(self, tmpdir):
        domain_path = os.path.join(tmpdir, "domain.mk")
        with open(domain_path, "w") as f:
            f.write(MAKEFILE_TEMPLATE)

        domain = topics.Domain(topic="topic", name="example", file=domain_path)
        self.assertTrue(len(domain.file_data) > 0)
        self.assertTrue(domain._file_data is domain.file_data)

        config = domain.config
        self.assertIsInstance(config, configparser.ConfigParser)
        self.assertTrue(domain._config is config)
        self.assertEqual(config["example"]["title"], "Title")
        self.assertEqual(config["example"]["description"], "Description")
        self.assertEqual(config["example"]["depends"], "\ndependency-1\ndependency-2")

        self.assertEqual(config["target.example"]["description"], "Build example")
        self.assertEqual(
            config["target.example-dirty"]["description"],
            "Rebuild example on next make run",
        )
        self.assertEqual(config["target.example-clean"]["description"], "Clean example")

        self.assertEqual(config["setting.SETTING_A"]["description"], "Setting A")
        self.assertEqual(config["setting.SETTING_A"]["default"], "A")
        self.assertEqual(config["setting.SETTING_B"]["description"], "Setting B")
        self.assertEqual(config["setting.SETTING_B"]["default"], "B")

        self.assertEqual(domain.title, "Title")
        self.assertEqual(domain.description, "Description")
        self.assertEqual(domain.depends, ["dependency-1", "dependency-2"])

        config["example"]["depends"] = ""
        self.assertEqual(domain.depends, [])

        targets = domain.targets
        self.assertEqual(len(targets), 3)
        self.assertEqual(targets[0].name, "example")
        self.assertEqual(targets[0].description, "Build example")

        settings = domain.settings
        self.assertEqual(len(settings), 2)
        self.assertEqual(settings[0].name, "SETTING_A")
        self.assertEqual(settings[0].description, "Setting A")
        self.assertEqual(settings[0].default, "A")

        out_path = os.path.join(tmpdir, "domain_out.mk")
        with open(out_path, "w") as fd:
            domain.write_to(fd)
        with open(out_path) as fd:
            out_content = fd.readlines()
        self.assertEqual(out_content[0], "SETTING_A?=A\n")
        self.assertEqual(out_content[-1], "\t@rm -f $(EXAMPLE_TARGET)\n")

    @temp_directory
    def test_Topic(self, tmpdir):
        topicdir = os.path.join(tmpdir, "topic")
        os.mkdir(topicdir)
        with open(os.path.join(topicdir, "domain-a.mk"), "w") as f:
            f.write("\n")
        with open(os.path.join(topicdir, "domain-b.mk"), "w") as f:
            f.write("\n")
        with open(os.path.join(topicdir, "somethinelse"), "w") as f:
            f.write("\n")

        topic = topics.Topic(name="topic", directory=topicdir)
        topic_domains = topic.domains
        self.assertEqual(len(topic_domains), 2)
        self.assertEqual(topic_domains[0].name, "domain-a")
        self.assertEqual(topic_domains[1].name, "domain-b")
        self.assertEqual(topic_domains[1].topic, "topic")

        self.assertEqual(topic.domain("domain-a").name, "domain-a")
        self.assertEqual(topic.domain("inexistent"), None)

    def test_DomainConflictError(self):
        counter = Counter(["a", "b", "b", "c", "c"])
        err = topics.DomainConflictError(counter)
        self.assertEqual(str(err), "Conflicting domain names: ['b', 'c']")

    def test_CircularDependencyDomainError(self):
        domain = TestDomain(topic="t1", name="f1", depends_=["f2"], file="f1.mk")
        err = topics.CircularDependencyDomainError([domain])
        self.assertEqual(
            str(err),
            (
                "Domains define circular dependencies: "
                "[TestDomain(topic='t1', name='f1', file='f1.mk', depends_=['f2'])]"
            ),
        )

    def test_MissingDependencyDomainError(self):
        domain = TestDomain(topic="t", name="t", depends_=["missing"], file="t.mk")
        err = topics.MissingDependencyDomainError(domain)
        self.assertEqual(
            str(err),
            (
                "Domain define missing dependency: "
                "TestDomain(topic='t', name='t', file='t.mk', depends_=['missing'])"
            ),
        )

    def test_DomainResolver(self):
        self.assertRaises(
            topics.DomainConflictError,
            topics.resolve_domain_dependencies,
            [
                TestDomain(topic="t", name="f", depends_=["t.f1"], file="t.mk"),
                TestDomain(topic="t", name="f", depends_=["t.f1"], file="t.mk"),
            ],
        )

        f1 = TestDomain(topic="t", name="f1", depends_=["t.f2"], file="f1.mk")
        f2 = TestDomain(topic="t", name="f2", depends_=["t.f3"], file="f2.mk")
        f3 = TestDomain(topic="t", name="f3", depends_=[], file="f3.mk")
        self.assertEqual(topics.resolve_domain_dependencies([f1, f2, f3]), [f3, f2, f1])
        self.assertEqual(topics.resolve_domain_dependencies([f2, f1, f3]), [f3, f2, f1])
        self.assertEqual(topics.resolve_domain_dependencies([f1, f3, f2]), [f3, f2, f1])

        f1 = TestDomain(topic="t", name="f1", depends_=["t.f2"], file="f1.mk")
        f2 = TestDomain(topic="t", name="f2", depends_=["t.f1"], file="f2.mk")
        self.assertRaises(
            topics.CircularDependencyDomainError,
            topics.resolve_domain_dependencies,
            [f1, f2],
        )

        f1 = TestDomain(topic="t", name="f1", depends_=["t.f2"], file="f1.mk")
        f2 = TestDomain(topic="t", name="f2", depends_=["t.missing"], file="f2.mk")
        self.assertRaises(
            topics.MissingDependencyDomainError,
            topics.resolve_domain_dependencies,
            [f1, f2],
        )

        f1 = TestDomain(topic="t", name="f1", depends_=["t.f2", "t.f4"], file="f1.mk")
        f2 = TestDomain(topic="t", name="f2", depends_=["t.f3", "t.f4"], file="f2.mk")
        f3 = TestDomain(topic="t", name="f3", depends_=["t.f4", "t.f5"], file="f3.mk")
        f4 = TestDomain(topic="t", name="f4", depends_=["t.f5"], file="f4.mk")
        f5 = TestDomain(topic="t", name="f5", depends_=[], file="f5.mk")
        self.assertEqual(
            topics.resolve_domain_dependencies([f1, f2, f3, f4, f5]),
            [f5, f4, f3, f2, f1],
        )
        self.assertEqual(
            topics.resolve_domain_dependencies([f5, f4, f3, f2, f1]),
            [f5, f4, f3, f2, f1],
        )
        self.assertEqual(
            topics.resolve_domain_dependencies([f4, f5, f2, f3, f1]),
            [f5, f4, f3, f2, f1],
        )
        self.assertEqual(
            topics.resolve_domain_dependencies([f1, f3, f2, f5, f4]),
            [f5, f4, f3, f2, f1],
        )

        f1 = TestDomain(topic="t", name="f1", depends_=["t.f2", "t.f3"], file="f1.mk")
        f2 = TestDomain(topic="t", name="f2", depends_=["t.f1", "t.f3"], file="f2.mk")
        f3 = TestDomain(topic="t", name="f3", depends_=["t.f1", "t.f2"], file="f3.mk")
        self.assertRaises(
            topics.CircularDependencyDomainError,
            topics.resolve_domain_dependencies,
            [f1, f2, f3],
        )

        f1 = TestDomain(topic="t", name="f1", depends_=["t.f2", "t.f3"], file="f1.ext")
        f2 = TestDomain(topic="t", name="f2", depends_=["t.f1", "t.f3"], file="f2.ext")
        f3 = TestDomain(topic="t", name="f3", depends_=["t.f1", "t.f4"], file="f3.ext")
        self.assertRaises(
            topics.MissingDependencyDomainError,
            topics.resolve_domain_dependencies,
            [f1, f2, f3],
        )

    def test_collect_missing_dependencies(self):
        domains = [
            topics.get_domain("ldap.python-ldap"),
            topics.get_domain("core.mxfiles"),
        ]
        all_dependencies = topics.collect_missing_dependencies(domains)
        self.assertEqual(
            sorted(domain.fqn for domain in all_dependencies),
            [
                "core.base",
                "core.mxenv",
                "core.mxfiles",
                "ldap.openldap",
                "ldap.python-ldap",
            ],
        )


###############################################################################
# Test main
###############################################################################


class TestMain(unittest.TestCase):
    @template_directory()
    def test_read_configuration(self, tempdir):
        config_file = io.StringIO()
        config_file.write("[settings]\n" "mxmake-templates = run-tests run-coverage")
        config_file.seek(0)
        configuration = main.read_configuration(config_file)
        self.assertIsInstance(configuration, mxdev.Configuration)
        templates = utils.list_value(
            configuration.settings.get(utils.ns_name("templates"))
        )
        self.assertEqual(templates, ["run-tests", "run-coverage"])

    @template_directory()
    def test_clean_mxfiles(self, tempdir):
        config_file = io.StringIO()
        config_file.write("[settings]\n")
        config_file.seek(0)
        configuration = main.read_configuration(config_file)
        with self.assertLogs() as captured:
            main.clean_files(configuration)
            self.assertEqual(len(captured.records), 2)
            self.assertEqual(
                captured.records[0].getMessage(), "mxmake: clean generated files"
            )
            self.assertEqual(
                captured.records[1].getMessage(), "mxmake: No templates defined"
            )

        with open(os.path.join(tempdir, "run-tests.sh"), "w") as f:
            f.write("")
        config_file = io.StringIO()
        config_file.write("[settings]\n" "mxmake-templates = run-tests\n")
        config_file.seek(0)
        configuration = main.read_configuration(config_file)
        with self.assertLogs() as captured:
            main.clean_files(configuration)
            self.assertEqual(len(captured.records), 2)
            self.assertEqual(
                captured.records[0].getMessage(), "mxmake: clean generated files"
            )
            self.assertEqual(
                captured.records[1].getMessage(),
                'mxmake: removed "run-tests.sh"',
            )
        self.assertEqual(sorted(os.listdir(tempdir)), [])


if __name__ == "__main__":
    unittest.main()
