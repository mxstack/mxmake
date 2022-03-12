from jinja2 import Environment
from jinja2 import PackageLoader
import abc
import argparse
import logging
import mxdev
import os
import sys
import typing

logger = logging.getLogger('mxenv')

NAMESPACE = 'mxenv-'


###############################################################################
# utils
###############################################################################

def venv_folder() -> str:
    """Folder containing the virtual environment."""
    return os.environ.get('MXENV_VENV_FOLDER', os.path.join('venv'))


def scripts_folder() -> str:
    """Target folder for script generation."""
    return os.environ.get('MXENV_SCRIPTS_FOLDER', os.path.join('venv', 'bin'))


def config_folder() -> str:
    """Target folder for config generation."""
    return os.environ.get('MXENV_CONFIG_FOLDER', os.path.join('cfg'))


def ns_name(name: str) -> str:
    """Return name prefixed by namespace."""
    return f'{NAMESPACE}{name}'


def list_value(value: str) -> typing.List[str]:
    """Convert string value from config file to list of strings. Separator is
    space. Supports newline.
    """
    if not value:
        return list()
    return [v.strip() for v in value.replace('\n', ' ').strip().split(' ')]


###############################################################################
# template basics
###############################################################################

class template:
    """Template decorator and registry."""

    _registry: typing.Dict = dict()

    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, ob: typing.Type['Template']) -> typing.Type['Template']:
        ob.name = self.name
        self._registry[self.name] = ob
        return ob

    @classmethod
    def lookup(cls, name: str) -> typing.Union[typing.Type['Template'], None]:
        return cls._registry.get(name)


class Template(abc.ABC):
    name: str
    file_mode: int = 0o644

    def __init__(
        self,
        config: mxdev.Configuration,
        environment: typing.Union[Environment, None] = None
    ) -> None:
        self.config = config
        self.environment = environment

    @property
    def settings(self) -> typing.Dict[str, str]:
        return self.config.hooks.get(ns_name(self.name), {})

    @abc.abstractproperty
    def target_folder(self) -> str:
        """Target folder for rendered template."""

    @abc.abstractproperty
    def target_name(self) -> str:
        """Target file name for rendered template."""

    @abc.abstractproperty
    def template_name(self) -> str:
        """Template name to use."""

    @abc.abstractproperty
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        """Variables for template rendering."""

    def write(self) -> None:
        """Render template and write result to file system."""
        if not self.environment:
            raise RuntimeError('Cannot write template without environment')
        target_folder = self.target_folder
        os.makedirs(target_folder, exist_ok=True)
        target_path = os.path.join(target_folder, self.target_name)
        template = self.environment.get_template(self.template_name)
        with open(target_path, 'w') as f:
            f.write(template.render(**self.template_variables))
        os.chmod(target_path, self.file_mode)

    def remove(self) -> bool:
        """Remove rendered template if exists. Return bool if file existed."""
        target_path = os.path.join(self.target_folder, self.target_name)
        if os.path.exists(target_path):
            os.remove(target_path)
            return True
        return False


class ShellScriptTemplate(Template):
    description: str = ''
    file_mode: int = 0o755


class EnvironmentTemplate(Template):

    @property
    def env(self) -> typing.Dict[str, str]:
        """Dict containing environment variables."""
        env_name = self.settings.get('environment')
        return self.config.hooks.get(ns_name(env_name), {}) if env_name else {}


###############################################################################
# test script template
###############################################################################

@template('run-tests')
class TestScript(ShellScriptTemplate, EnvironmentTemplate):
    description: str = 'Run tests'

    @property
    def target_folder(self) -> str:
        return scripts_folder()

    @property
    def target_name(self) -> str:
        return f'{self.name}.sh'

    template_name = target_name

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        return dict(
            description=self.description,
            env=self.env,
            venv=venv_folder(),
            testpaths=self.package_paths(ns_name('test-path'))
        )

    def package_paths(self, attr: str) -> typing.List[str]:
        paths = list()
        for name, package in self.config.packages.items():
            if attr not in package:
                continue
            path = f"{package['target']}/{name}/{package[attr]}".rstrip('/')
            paths.append(path)
        return paths


###############################################################################
# coverage script template
###############################################################################

@template('run-coverage')
class CoverageScript(TestScript):
    description: str = 'Run coverage'

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        variables = super().template_variables
        variables['sourcepaths'] = self.package_paths(ns_name('source-path'))
        return variables


###############################################################################
# mxdev hook
###############################################################################

class Hook(mxdev.Hook):
    namespace: str = NAMESPACE

    def __init__(self) -> None:
        logger.info('mxenv: hook initialized')

    def write(self, state: mxdev.State) -> None:
        config = state.configuration
        templates = list_value(config.settings.get(ns_name('templates')))
        if not templates:
            logger.info('mxenv: No templates defined')
            return
        environment = Environment(
            loader=PackageLoader('mxenv', 'templates'),
            trim_blocks=True,
            keep_trailing_newline=True
        )
        for name in templates:
            factory = template.lookup(name)
            if not factory:
                msg = f'mxenv: No template registered under name {name}'
                logger.warning(msg)
                continue
            factory(config, environment).write()


###############################################################################
# cmd line
###############################################################################

def main() -> None:
    mxdev.setup_logger(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--configuration',
        help='mxdev configuration file',
        nargs="?",
        type=argparse.FileType('r'),
        required=True
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Remove generated files'
    )
    args = parser.parse_args()
    if args.clean:
        logger.info('mxenv: clean generated files')
        hooks = mxdev.load_hooks()
        configuration = mxdev.Configuration(tio=args.configuration, hooks=hooks)
        state = mxdev.State(configuration=configuration)
        mxdev.read(state)
        mxdev.read_hooks(state, hooks)
        config = state.configuration
        templates = list_value(config.settings.get(ns_name('templates')))
        if not templates:
            logger.info('mxenv: No templates defined')
        else:
            for name in templates:
                factory = template.lookup(name)
                instance = factory(config)
                if instance.remove():
                    logger.info(f'mxenv: removed "{instance.target_name}"')
        sys.exit(0)
    logger.info('mxenv: no action given')
    sys.exit(1)
