from jinja2 import Environment
from jinja2 import PackageLoader
from mxenv.templates import template
from mxenv.utils import NAMESPACE
from mxenv.utils import list_value
from mxenv.utils import ns_name
import logging
import mxdev


logger = logging.getLogger('mxenv')


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
