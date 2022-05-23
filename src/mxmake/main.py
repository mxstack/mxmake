from mxmake.targets import get_domain
from mxmake.targets import load_domains
from mxmake.templates import template
from mxmake.utils import list_value
from mxmake.utils import ns_name
import argparse
import logging
import mxdev
import sys
import typing


logger = logging.getLogger('mxmake')


parser = argparse.ArgumentParser()
command_parsers = parser.add_subparsers(dest='command', required=True)


##############################################################################
# clean
##############################################################################

def read_configuration(tio: typing.TextIO) -> mxdev.Configuration:
    hooks = mxdev.load_hooks()
    configuration = mxdev.Configuration(tio=tio, hooks=hooks)
    state = mxdev.State(configuration=configuration)
    mxdev.read(state)
    mxdev.read_hooks(state, hooks)
    return configuration


def clean_files(configuration: mxdev.Configuration) -> None:
    logger.info('mxmake: clean generated files')
    templates = list_value(configuration.settings.get(ns_name('templates')))
    if not templates:
        logger.info('mxmake: No templates defined')
    else:
        for name in templates:
            factory = template.lookup(name)
            instance = factory(configuration)
            if instance.remove():
                logger.info(f'mxmake: removed "{instance.target_name}"')


def clean_command(args: argparse.Namespace):
    configuration = read_configuration(args.configuration)
    clean_files(configuration)


clean_parser = command_parsers.add_parser(
    'clean',
    help='Remove generated files'
)
clean_parser.set_defaults(func=clean_command)
clean_parser.add_argument(
    '-c', '--configuration', help='mxdev configuration file',
    nargs='?', type=argparse.FileType('r'), default='mx.ini'
)


##############################################################################
# list
##############################################################################

def list_command(args: argparse.Namespace):
    if not args.domain:
        domains = load_domains()
        sys.stdout.write('Available Domains:\n')
        for domain in domains:
            sys.stdout.write(f'  * {domain.name}\n')
    else:
        domain = get_domain(args.domain)
        sys.stdout.write(f'Available Targets in {domain.name}:\n')
        for target in domain.targets:
            sys.stdout.write(f'  * {target.name} - {target.description}\n')


list_parser = command_parsers.add_parser(
    'list',
    help='List stuff'
)
list_parser.set_defaults(func=list_command)
list_parser.add_argument('-d', '--domain', help='Domain name')

##############################################################################
# main
##############################################################################

def main() -> None:
    mxdev.setup_logger(logging.INFO)
    args = parser.parse_args()
    args.func(args)
