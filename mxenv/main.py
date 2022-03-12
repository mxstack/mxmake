import argparse
import logging
import mxdev
import sys
from mxenv.templates import template
from mxenv.utils import ns_name
from mxenv.utils import list_value


logger = logging.getLogger('mxenv')


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
