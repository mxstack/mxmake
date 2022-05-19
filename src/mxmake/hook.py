from jinja2 import Environment
from jinja2 import PackageLoader
from mxmake.templates import template
from mxmake.utils import NAMESPACE
from mxmake.utils import list_value
from mxmake.utils import ns_name
import logging
import mxdev


logger = logging.getLogger('mxmake')


def get_template_environment() -> Environment:
    return Environment(
        loader=PackageLoader('mxmake', 'templates'),
        trim_blocks=True,
        keep_trailing_newline=True
    )


class Hook(mxdev.Hook):
    namespace: str = NAMESPACE

    def __init__(self) -> None:
        logger.info('mxmake: hook initialized')

    def write(self, state: mxdev.State) -> None:
        config = state.configuration
        templates = list_value(config.settings.get(ns_name('templates')))
        if not templates:
            logger.info('mxmake: No templates defined')
            return
        environment = get_template_environment()
        for name in templates:
            factory = template.lookup(name)
            if not factory:
                msg = f'mxmake: No template registered under name {name}'
                logger.warning(msg)
                continue
            factory(config, environment).write()
