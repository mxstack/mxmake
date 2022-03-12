from contextlib import contextmanager
from jinja2 import Environment
from jinja2 import FileSystemLoader
from mxenv import templates
from mxenv import utils
import mxdev
import os
import shutil
import tempfile
import typing
import unittest


###############################################################################
# Test utils
###############################################################################

class TestUtils(unittest.TestCase):

    def test_namespace(self):
        self.assertEqual(utils.NAMESPACE, 'mxenv-')

    def test_venv_folder(self):
        self.assertEqual(utils.venv_folder(), 'venv')
        os.environ['MXENV_VENV_FOLDER'] = 'other'
        self.assertEqual(utils.venv_folder(), 'other')
        del os.environ['MXENV_VENV_FOLDER']

    def test_scripts_folder(self):
        self.assertEqual(utils.scripts_folder(), os.path.join('venv', 'bin'))
        os.environ['MXENV_SCRIPTS_FOLDER'] = 'other'
        self.assertEqual(utils.scripts_folder(), 'other')
        del os.environ['MXENV_SCRIPTS_FOLDER']

    def test_config_folder(self):
        self.assertEqual(utils.config_folder(), 'cfg')
        os.environ['MXENV_CONFIG_FOLDER'] = 'other'
        self.assertEqual(utils.config_folder(), 'other')
        del os.environ['MXENV_CONFIG_FOLDER']

    def test_ns_name(self):
        self.assertEqual(utils.ns_name('foo'), 'mxenv-foo')

    def test_list_value(self):
        self.assertEqual(utils.list_value(''), [])
        self.assertEqual(utils.list_value('a\nb c'), ['a', 'b', 'c'])


###############################################################################
# Test teamplates
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
            os.environ['MXENV_VENV_FOLDER'] = tempdir
            os.environ['MXENV_SCRIPTS_FOLDER'] = tempdir
            os.environ['MXENV_CONFIG_FOLDER'] = tempdir
            try:
                if self.reset_registry:
                    with reset_template_registry():
                        fn(*a, tempdir=tempdir)
                else:
                    fn(*a, tempdir=tempdir)
            finally:
                shutil.rmtree(tempdir)
                del os.environ['MXENV_VENV_FOLDER']
                del os.environ['MXENV_SCRIPTS_FOLDER']
                del os.environ['MXENV_CONFIG_FOLDER']
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


class TestTemplates(unittest.TestCase):

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
        hooks['mxenv-template'] = dict(key='val')
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
        hooks['mxenv-template'] = {
            'environment': 'env'
        }
        self.assertEqual(template.env, {})
        hooks['mxenv-env'] = {
            'param': 'value'
        }
        self.assertEqual(template.env, {
            'param': 'value'
        })


if __name__ == '__main__':
    unittest.main()
