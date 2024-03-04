from jinja2 import Environment
from jinja2 import FileSystemLoader
from mxmake import hook
from mxmake import templates
from mxmake import testing
from mxmake import topics
from mxmake import utils
from pathlib import Path

import mxdev
import typing


class TestTemplates(testing.RenderTestCase):
    def test_template(self):
        with testing.reset_template_registry():

            @templates.template("template")
            class Template(templates.Template):
                pass

            self.assertEqual(templates.template._registry, dict(template=Template))
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
                "run-coverage": templates.CoverageScript,
                "run-tests": templates.TestScript,
                "topics.md": templates.Topics,
                "gh-actions-docs": templates.GHActionsDocs,
                "gh-actions-lint": templates.GHActionsLint,
                "gh-actions-test": templates.GHActionsTest,
                "gh-actions-typecheck": templates.GHActionsTypecheck,
            },
        )

    @testing.template_directory()
    def test_Template(self, tempdir: Path):
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
        hooks: typing.Dict[str, typing.Dict] = {}
        template = Template(testing.TestConfiguration(hooks=hooks))
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
                "testpaths": ["sources/package/src", "src"],
            },
        )
        self.assertEqual(template.package_paths("inexistent"), [])
        self.assertEqual(
            template.package_paths(utils.ns_name("test-path")),
            ["sources/package/src", "src"],
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
            "core.mxenv.PRIMARY_PYTHON": "python3",
            "core.mxenv.PYTHON_MIN_VERSION": "3.7",
            "core.mxenv.PYTHON_PACKAGE_INSTALLER": "pip",
            "core.mxenv.MXENV_UV_GLOBAL": "false",
            "core.mxenv.VENV_ENABLED": "true",
            "core.mxenv.VENV_CREATE": "true",
            "core.mxenv.VENV_FOLDER": ".venv",
            "core.mxenv.MXDEV": "mxdev",
            "core.mxenv.MXMAKE": "mxmake",
        }
        factory = templates.template.lookup("makefile")
        template = factory(
            tempdir, domains, domain_settings, templates.get_template_environment()
        )

        template.write()
        with (tempdir / "Makefile").open() as f:
            self.checkOutput(
                """
                ##############################################################################
                # THIS FILE IS GENERATED BY MXMAKE
                #
                # DOMAINS:
                #: core.base
                #: core.mxenv
                #
                # SETTINGS (ALL CHANGES MADE BELOW SETTINGS WILL BE LOST)
                ##############################################################################

                ## core.base

                # `deploy` target dependencies.
                # No default value.
                DEPLOY_TARGETS?=

                # target to be executed when calling `make run`
                # No default value.
                RUN_TARGET?=

                # Additional files and folders to remove when running clean target
                # No default value.
                CLEAN_FS?=

                # Optional makefile to include before default targets. This can
                # be used to provide custom targets or hook up to existing targets.
                # Default: include.mk
                INCLUDE_MAKEFILE?=include.mk

                # Optional additional directories to be added to PATH in format
                # `/path/to/dir/:/path/to/other/dir`. Gets inserted first, thus gets searched
                # first.
                # No default value.
                EXTRA_PATH?=

                ## core.mxenv

                # Primary Python interpreter to use. It is used to create the
                # virtual environment if `VENV_ENABLED` and `VENV_CREATE` are set to `true`.
                # Default: python3
                PRIMARY_PYTHON?=python3

                # Minimum required Python version.
                # Default: 3.7
                PYTHON_MIN_VERSION?=3.7

                # Install packages using the given package installer method.
                # Supported are `pip` and `uv`. If uv is used, its global availability is
                # checked. Otherwise, it is installed, either in the virtual environment or
                # using the `PRIMARY_PYTHON`, dependent on the `VENV_ENABLED` setting. If
                # `VENV_ENABLED` and uv is selected, uv is used to create the virtual
                # environment.
                # Default: pip
                PYTHON_PACKAGE_INSTALLER?=pip

                # Flag whether to use a global installed 'uv' or install
                # it in the virtual environment.
                # Default: false
                MXENV_UV_GLOBAL?=false

                # Flag whether to use virtual environment. If `false`, the
                # interpreter according to `PRIMARY_PYTHON` found in `PATH` is used.
                # Default: true
                VENV_ENABLED?=true

                # Flag whether to create a virtual environment. If set to `false`
                # and `VENV_ENABLED` is `true`, `VENV_FOLDER` is expected to point to an
                # existing virtual environment.
                # Default: true
                VENV_CREATE?=true

                # The folder of the virtual environment.
                # If `VENV_ENABLED` is `true` and `VENV_CREATE` is true it is used as the
                # target folder for the virtual environment. If `VENV_ENABLED` is `true` and
                # `VENV_CREATE` is false it is expected to point to an existing virtual
                # environment. If `VENV_ENABLED` is `false` it is ignored.
                # Default: .venv
                VENV_FOLDER?=.venv

                # mxdev to install in virtual environment.
                # Default: mxdev
                MXDEV?=mxdev

                # mxmake to install in virtual environment.
                # Default: mxmake
                MXMAKE?=mxmake

                ##############################################################################
                # END SETTINGS - DO NOT EDIT BELOW THIS LINE
                ##############################################################################

                INSTALL_TARGETS?=
                DIRTY_TARGETS?=
                CLEAN_TARGETS?=
                PURGE_TARGETS?=

                export PATH:=$(if $(EXTRA_PATH),$(EXTRA_PATH):,)$(PATH)

                # Defensive settings for make: https://tech.davis-hansson.com/p/make/
                SHELL:=bash
                .ONESHELL:
                # for Makefile debugging purposes add -x to the .SHELLFLAGS
                .SHELLFLAGS:=-eu -o pipefail -O inherit_errexit -c
                .SILENT:
                .DELETE_ON_ERROR:
                MAKEFLAGS+=--warn-undefined-variables
                MAKEFLAGS+=--no-builtin-rules

                # mxmake folder
                MXMAKE_FOLDER?=.mxmake
                 # Sentinel files
                SENTINEL_FOLDER?=$(MXMAKE_FOLDER)/sentinels
                SENTINEL?=$(SENTINEL_FOLDER)/about.txt
                $(SENTINEL):
                	@mkdir -p $(SENTINEL_FOLDER)
                	@echo "Sentinels for the Makefile process." > $(SENTINEL)
                 ##############################################################################
                # mxenv
                ##############################################################################

                # Check if given Python is installed
                ifeq (,$(shell which $(PRIMARY_PYTHON)))
                $(error "PYTHON=$(PRIMARY_PYTHON) not found in $(PATH)")
                endif

                # Check if given Python version is ok
                PYTHON_VERSION_OK=$(shell $(PRIMARY_PYTHON) -c "import sys; print((int(sys.version_info[0]), int(sys.version_info[1])) >= tuple(map(int, '$(PYTHON_MIN_VERSION)'.split('.'))))")
                ifeq ($(PYTHON_VERSION_OK),0)
                $(error "Need Python >= $(PYTHON_MIN_VERSION)")
                endif

                # Check if venv folder is configured if venv is enabled
                ifeq ($(shell [[ "$(VENV_ENABLED)" == "true" && "$(VENV_FOLDER)" == "" ]] && echo "true"),"true")
                $(error "VENV_FOLDER must be configured if VENV_ENABLED is true")
                endif

                # Check if global python is used with uv (this is not supported by uv)
                ifeq ("$(VENV_ENABLED)$(PYTHON_PACKAGE_INSTALLER)","falseuv")
                $(error "Package installer uv does not work with a global Python interpreter.")
                endif

                # Determine the executable path
                ifeq ("$(VENV_ENABLED)", "true")
                export VIRTUAL_ENV=$(abspath $(VENV_FOLDER))
                ifeq ("$(OS)", "Windows_NT")
                VENV_EXECUTABLE_FOLDER=$(VIRTUAL_ENV)/Scripts
                else
                VENV_EXECUTABLE_FOLDER=$(VIRTUAL_ENV)/bin
                endif
                export PATH:=$(VENV_EXECUTABLE_FOLDER):$(PATH)
                MXENV_PYTHON=python
                else
                MXENV_PYTHON=$(PRIMARY_PYTHON)
                endif

                # Determine the package installer
                ifeq ("$(PYTHON_PACKAGE_INSTALLER)","uv")
                PYTHON_PACKAGE_COMMAND=uv pip
                else
                PYTHON_PACKAGE_COMMAND=$(MXENV_PYTHON) -m pip
                endif

                MXENV_TARGET:=$(SENTINEL_FOLDER)/mxenv.sentinel
                $(MXENV_TARGET): $(SENTINEL)
                ifeq ("$(VENV_ENABLED)", "true")
                ifeq ("$(VENV_CREATE)", "true")
                ifeq ("$(PYTHON_PACKAGE_INSTALLER)$(MXENV_UV_GLOBAL)","uvtrue")
                	@echo "Setup Python Virtual Environment using package 'uv' at '$(VENV_FOLDER)'"
                	@uv venv -p $(PRIMARY_PYTHON) --seed $(VENV_FOLDER)
                else
                	@echo "Setup Python Virtual Environment using module 'venv' at '$(VENV_FOLDER)'"
                	@$(PRIMARY_PYTHON) -m venv $(VENV_FOLDER)
                	@$(MXENV_PYTHON) -m ensurepip -U
                endif
                endif
                else
                	@echo "Using system Python interpreter"
                endif
                ifeq ("$(PYTHON_PACKAGE_INSTALLER)$(MXENV_UV_GLOBAL)","uvfalse")
                	@echo "Install uv"
                	@$(MXENV_PYTHON) -m pip install uv
                endif
                	@$(PYTHON_PACKAGE_COMMAND) install -U pip setuptools wheel
                	@echo "Install/Update MXStack Python packages"
                	@$(PYTHON_PACKAGE_COMMAND) install -U $(MXDEV) $(MXMAKE)
                	@touch $(MXENV_TARGET)

                .PHONY: mxenv
                mxenv: $(MXENV_TARGET)

                .PHONY: mxenv-dirty
                mxenv-dirty:
                	@rm -f $(MXENV_TARGET)

                .PHONY: mxenv-clean
                mxenv-clean: mxenv-dirty
                ifeq ("$(VENV_ENABLED)", "true")
                ifeq ("$(VENV_CREATE)", "true")
                	@rm -rf $(VENV_FOLDER)
                endif
                else
                	@$(PYTHON_PACKAGE_COMMAND) uninstall -y $(MXDEV)
                	@$(PYTHON_PACKAGE_COMMAND) uninstall -y $(MXMAKE)
                endif

                INSTALL_TARGETS+=mxenv
                DIRTY_TARGETS+=mxenv-dirty
                CLEAN_TARGETS+=mxenv-clean

                -include $(INCLUDE_MAKEFILE)
                 ##############################################################################
                # Default targets
                ##############################################################################
                 INSTALL_TARGET:=$(SENTINEL_FOLDER)/install.sentinel
                $(INSTALL_TARGET): $(INSTALL_TARGETS)
                	@touch $(INSTALL_TARGET)

                .PHONY: install
                install: $(INSTALL_TARGET)
                	@touch $(INSTALL_TARGET)

                .PHONY: run
                run: $(RUN_TARGET)

                .PHONY: deploy
                deploy: $(DEPLOY_TARGETS)

                .PHONY: dirty
                dirty: $(DIRTY_TARGETS)
                	@rm -f $(INSTALL_TARGET)

                .PHONY: clean
                clean: dirty $(CLEAN_TARGETS)
                	@rm -rf $(CLEAN_TARGETS) $(MXMAKE_FOLDER) $(CLEAN_FS)

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

    @testing.temp_directory
    def test_MxIni(self, tempdir):
        domains = [
            topics.get_domain("qa.test"),
            topics.get_domain("qa.coverage"),
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
