from contextlib import contextmanager
from jinja2 import Environment
from jinja2 import FileSystemLoader
from mxmake import hook
from mxmake import main
from mxmake import templates
from mxmake import utils
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
            os.environ['MXMAKE_VENV_FOLDER'] = tempdir
            os.environ['MXMAKE_SCRIPTS_FOLDER'] = tempdir
            os.environ['MXMAKE_CONFIG_FOLDER'] = tempdir
            try:
                if self.reset_registry:
                    with reset_template_registry():
                        fn(*a, tempdir=tempdir)
                else:
                    fn(*a, tempdir=tempdir)
            finally:
                shutil.rmtree(tempdir)
                del os.environ['MXMAKE_VENV_FOLDER']
                del os.environ['MXMAKE_SCRIPTS_FOLDER']
                del os.environ['MXMAKE_CONFIG_FOLDER']
        return wrapper


class TestConfiguration(mxdev.Configuration):

    def __init__(
        self,
        settings: typing.Dict[str, str] = {},
        overrides: typing.Dict[str, str] = {},
        ignore_keys: typing.List[str] = [],
        packages: typing.Dict[str, typing.Dict[str, str]] = {},
        hooks: typing.Dict[str, typing.Dict[str, str]] = {}
    ):
        self.settings = settings
        self.overrides = overrides
        self.ignore_keys = ignore_keys
        self.packages = packages
        self.hooks = hooks


class RenderTestCase(unittest.TestCase):
    class Example(object):
        def __init__(self, want):
            self.want = want + '\n'

    class Failure(Exception):
        pass

    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        self._checker = doctest.OutputChecker()
        self._optionflags = (
            doctest.NORMALIZE_WHITESPACE |
            doctest.ELLIPSIS |
            doctest.REPORT_ONLY_FIRST_FAILURE
        )

    def checkOutput(self, want, got, optionflags=None):
        if optionflags is None:
            optionflags = self._optionflags
        success = self._checker.check_output(want, got, optionflags)
        if not success:
            raise RenderTestCase.Failure(self._checker.output_difference(
                RenderTestCase.Example(want),
                got, optionflags
            ))


###############################################################################
# Test utils
###############################################################################

class TestUtils(unittest.TestCase):

    def test_namespace(self):
        self.assertEqual(utils.NAMESPACE, 'mxmake-')

    def test_venv_folder(self):
        self.assertEqual(utils.venv_folder(), 'venv')
        os.environ['MXMAKE_VENV_FOLDER'] = 'other'
        self.assertEqual(utils.venv_folder(), 'other')
        del os.environ['MXMAKE_VENV_FOLDER']

    def test_scripts_folder(self):
        self.assertEqual(utils.scripts_folder(), os.path.join('venv', 'bin'))
        os.environ['MXMAKE_SCRIPTS_FOLDER'] = 'other'
        self.assertEqual(utils.scripts_folder(), 'other')
        del os.environ['MXMAKE_SCRIPTS_FOLDER']

    def test_config_folder(self):
        self.assertEqual(utils.config_folder(), 'cfg')
        os.environ['MXMAKE_CONFIG_FOLDER'] = 'other'
        self.assertEqual(utils.config_folder(), 'other')
        del os.environ['MXMAKE_CONFIG_FOLDER']

    def test_ns_name(self):
        self.assertEqual(utils.ns_name('foo'), 'mxmake-foo')

    def test_list_value(self):
        self.assertEqual(utils.list_value(''), [])
        self.assertEqual(utils.list_value('a\nb c'), ['a', 'b', 'c'])


###############################################################################
# Test teamplates
###############################################################################

class TestTemplates(RenderTestCase):

    def test_template(self):
        with reset_template_registry():
            @templates.template('template')
            class Template(templates.Template):
                pass

            self.assertEqual(
                templates.template._registry,
                dict(template=Template)
            )
            self.assertEqual(templates.template.lookup('inexistent'), None)
            self.assertEqual(templates.template.lookup('template'), Template)

        self.assertEqual(templates.template._registry, {
            'run-coverage': templates.CoverageScript,
            'run-tests': templates.TestScript
        })

    @template_directory()
    def test_Template(self, tempdir: str):
        # cannot instantiate abstract template
        with self.assertRaises(TypeError):
            templates.Template()

        # create test template
        class Template(templates.Template):
            name = 'template'
            target_folder = tempdir
            target_name = 'target.out'
            template_name = 'target.in'
            template_variables = dict(param='value')

        # cannot write template without template environment
        hooks = {}
        template = Template(TestConfiguration(hooks=hooks))
        with self.assertRaises(RuntimeError):
            template.write()

        # template settings
        self.assertEqual(template.settings, dict())
        hooks['mxmake-template'] = dict(key='val')
        self.assertEqual(template.settings, dict(key='val'))

        # write template
        with open(os.path.join(tempdir, 'target.in'), 'w') as f:
            f.write('{{ param }}')
        environment = Environment(loader=FileSystemLoader(tempdir))
        template = Template(TestConfiguration(hooks={}), environment)
        template.write()
        with open(os.path.join(tempdir, 'target.out')) as f:
            self.assertEqual(f.read(), 'value')

        # check file mode
        self.assertEqual(template.file_mode, 0o644)
        # XXX: check file mode in file system

        # remove remplate
        removed = template.remove()
        self.assertTrue(removed)
        self.assertFalse(os.path.exists(os.path.join(tempdir, 'target.out')))
        self.assertFalse(template.remove())

    def test_ShellScriptTemplate(self):
        self.assertEqual(templates.ShellScriptTemplate.description, '')
        self.assertEqual(templates.ShellScriptTemplate.file_mode, 0o755)

    def test_EnvironmentTemplate(self):
        class Template(templates.EnvironmentTemplate):
            name = 'template'
            target_folder = ''
            target_name = ''
            template_name = ''
            template_variables = {}

        hooks = {}
        template = Template(TestConfiguration(hooks=hooks))
        self.assertEqual(template.env, {})
        hooks['mxmake-template'] = {
            'environment': 'env'
        }
        self.assertEqual(template.env, {})
        hooks['mxmake-env'] = {
            'param': 'value'
        }
        self.assertEqual(template.env, {
            'param': 'value'
        })

    @template_directory()
    def test_TestScript(self, tempdir):
        config_file = io.StringIO()
        config_file.write(
            '[settings]\n'
            '[mxmake-env]\n'
            'ENV_PARAM = env_value\n'
            '[mxmake-run-tests]\n'
            'environment = env\n'
            '[package]\n'
            'url = https://github.com/org/package\n'
            'mxmake-test-path = src\n'
        )
        config_file.seek(0)

        configuration = mxdev.Configuration(config_file, hooks=[hook.Hook()])
        factory = templates.template.lookup('run-tests')
        template = factory(configuration, hook.get_template_environment())

        self.assertEqual(template.description, 'Run tests')
        self.assertEqual(template.target_folder, utils.scripts_folder())
        self.assertEqual(template.target_name, 'run-tests.sh')
        self.assertEqual(template.template_name, 'run-tests.sh')
        self.assertEqual(template.template_variables, {
            'description': 'Run tests',
            'env': {'ENV_PARAM': 'env_value'},
            'testpaths': ['sources/package/src'],
            'venv': tempdir
        })
        self.assertEqual(template.package_paths('inexistent'), [])
        self.assertEqual(
            template.package_paths(utils.ns_name('test-path')),
            ['sources/package/src']
        )

        template.write()
        with open(os.path.join(tempdir, 'run-tests.sh')) as f:
            self.checkOutput("""
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

            /.../bin/zope-testrunner --auto-color --auto-progress \\
                --test-path=sources/package/src \\
                --module=$1

            unsetenv

            exit 0
            """, f.read())

    @template_directory()
    def test_CoverageScript(self, tempdir):
        config_file = io.StringIO()
        config_file.write(
            '[settings]\n'
            '[mxmake-env]\n'
            'ENV_PARAM = env_value\n'
            '[mxmake-run-coverage]\n'
            'environment = env\n'
            '[package]\n'
            'url = https://github.com/org/package\n'
            'mxmake-test-path = src\n'
            'mxmake-source-path = src/package\n'
        )
        config_file.seek(0)

        configuration = mxdev.Configuration(config_file, hooks=[hook.Hook()])
        factory = templates.template.lookup('run-coverage')
        template = factory(configuration, hook.get_template_environment())

        self.assertEqual(template.description, 'Run coverage')
        self.assertEqual(template.target_folder, utils.scripts_folder())
        self.assertEqual(template.target_name, 'run-coverage.sh')
        self.assertEqual(template.template_name, 'run-coverage.sh')
        self.assertEqual(template.template_variables, {
            'description': 'Run coverage',
            'env': {'ENV_PARAM': 'env_value'},
            'testpaths': ['sources/package/src'],
            'sourcepaths': ['sources/package/src/package'],
            'venv': tempdir
        })
        self.assertEqual(template.package_paths('inexistent'), [])
        self.assertEqual(
            template.package_paths(utils.ns_name('test-path')),
            ['sources/package/src']
        )
        self.assertEqual(
            template.package_paths(utils.ns_name('source-path')),
            ['sources/package/src/package']
        )

        template.write()
        with open(os.path.join(tempdir, 'run-coverage.sh')) as f:
            self.checkOutput("""
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

            /.../bin/coverage run \\
                --source=$sources \\
                -m zope.testrunner --auto-color --auto-progress \\
                --test-path=sources/package/src

            /.../bin/coverage report
            /.../bin/coverage html

            unsetenv

            exit 0
            """, f.read())


###############################################################################
# Test hook
###############################################################################

class TestHook(unittest.TestCase):

    @template_directory()
    def test_Hook(self, tempdir):
        config_file = io.StringIO()
        config_file.write(
            '[settings]\n'
            'mxmake-templates = run-tests run-coverage inexistent'
        )
        config_file.seek(0)

        hook_ = hook.Hook()
        configuration = mxdev.Configuration(config_file, hooks=[hook_])
        state = mxdev.State(configuration=configuration)
        hook_.write(state)
        self.assertEqual(
            sorted(os.listdir(tempdir)),
            ['run-coverage.sh', 'run-tests.sh']
        )


###############################################################################
# Test main
###############################################################################

class TestMain(unittest.TestCase):

    @template_directory()
    def test_read_configuration(self, tempdir):
        config_file = io.StringIO()
        config_file.write(
            '[settings]\n'
            'mxmake-templates = run-tests run-coverage'
        )
        config_file.seek(0)
        configuration = main.read_configuration(config_file)
        self.assertIsInstance(configuration, mxdev.Configuration)
        templates = utils.list_value(
            configuration.settings.get(utils.ns_name('templates'))
        )
        self.assertEqual(templates, ['run-tests', 'run-coverage'])

    @template_directory()
    def test_clean_files(self, tempdir):
        config_file = io.StringIO()
        config_file.write(
            '[settings]\n'
        )
        config_file.seek(0)
        configuration = main.read_configuration(config_file)
        with self.assertLogs() as captured:
            main.clean_files(configuration)
            self.assertEqual(len(captured.records), 2)
            self.assertEqual(
                captured.records[0].getMessage(),
                'mxmake: clean generated files'
            )
            self.assertEqual(
                captured.records[1].getMessage(),
                'mxmake: No templates defined'
            )

        with open(os.path.join(tempdir, 'run-tests.sh'), 'w') as f:
            f.write('')
        config_file = io.StringIO()
        config_file.write(
            '[settings]\n'
            'mxmake-templates = run-tests\n'
        )
        config_file.seek(0)
        configuration = main.read_configuration(config_file)
        with self.assertLogs() as captured:
            main.clean_files(configuration)
            self.assertEqual(len(captured.records), 2)
            self.assertEqual(
                captured.records[0].getMessage(),
                'mxmake: clean generated files'
            )
            self.assertEqual(
                captured.records[1].getMessage(),
                'mxmake: removed "run-tests.sh"',
            )
        self.assertEqual(sorted(os.listdir(tempdir)), [])


if __name__ == '__main__':
    unittest.main()
