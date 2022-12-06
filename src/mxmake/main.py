from mxmake.domains import get_domain
from mxmake.domains import load_domains
from mxmake.templates import template
from mxmake.utils import list_value
from mxmake.utils import ns_name
from textwrap import indent

import argparse
import inquirer
import logging
import mxdev
import sys
import typing


logger = logging.getLogger("mxmake")


parser = argparse.ArgumentParser()
command_parsers = parser.add_subparsers(dest="command", required=True)


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
    logger.info("mxmake: clean generated files")
    templates = list_value(configuration.settings.get(ns_name("templates")))
    if not templates:
        logger.info("mxmake: No templates defined")
    else:
        for name in templates:
            factory = template.lookup(name)
            instance = factory(configuration)  # type: ignore
            if instance.remove():
                logger.info(f'mxmake: removed "{instance.target_name}"')


def clean_command(args: argparse.Namespace):
    configuration = read_configuration(args.configuration)
    clean_files(configuration)


clean_parser = command_parsers.add_parser("clean", help="Remove generated files")
clean_parser.set_defaults(func=clean_command)
clean_parser.add_argument(
    "-c",
    "--configuration",
    help="mxdev configuration file",
    nargs="?",
    type=argparse.FileType("r"),
    default="mx.ini",
)


##############################################################################
# list
##############################################################################

def list_command(args: argparse.Namespace):
    if not args.domain:
        domains = load_domains()
        sys.stdout.write("Domains:\n")
        for domain_ in domains:
            sys.stdout.write(f"  - {domain_.name}\n")
        return

    domain = get_domain(args.domain)
    if domain is None:
        sys.stdout.write(f"Requested domain not found: {args.domain}\n")
        sys.exit(1)

    if not args.makefile:
        sys.stdout.write(f"Makefiles in domain {domain.name}:\n")
        for makefile_ in domain.makefiles:
            description = indent(makefile_.description, 4 * " ").strip()
            sys.stdout.write(f"  - {makefile_.name}: {description}\n")
        return

    makefile = domain.makefile(args.makefile)
    if makefile is None:
        sys.stdout.write(f"Requested makefile not found: {args.makefile}\n")
        sys.exit(1)

    sys.stdout.write(f"Makefile {domain.name}.{makefile.name}:\n")
    depends = (
        ", ".join(makefile.depends)
        if makefile.depends
        else "No dependencies"
    )
    sys.stdout.write(f"  Depends: {depends}\n")
    sys.stdout.write(f"  Targets:")
    targets = makefile.targets
    if not targets:
        sys.stdout.write(f" No targets provided\n")
    else:
        sys.stdout.write(f"\n")
        for target in targets:
            description = indent(target.description, 6 * " ").strip()
            sys.stdout.write(f"    {target.name}: {description}\n")
    sys.stdout.write(f"  Settings:")
    settings = makefile.settings
    if not settings:
        sys.stdout.write(f" No settings provided\n")
    else:
        sys.stdout.write(f"\n")
        for setting in settings:
            description = indent(setting.description, 8 * " ").strip()
            sys.stdout.write(
                f"    - {setting.name}: {setting.description}\n"
                f"      - default value: {setting.default}\n"
            )


list_parser = command_parsers.add_parser("list", help="List stuff")
list_parser.set_defaults(func=list_command)
list_parser.add_argument("-d", "--domain", help="Domain name")
list_parser.add_argument("-m", "--makefile", help="Makefile name")


##############################################################################
# init
##############################################################################

def init_command(args: argparse.Namespace):
    domains = load_domains()
    domain_choice = inquirer.prompt([
        inquirer.Checkbox(
            'domain',
            message='Include domains',
            choices=[d.name for d in domains]
        )
    ])
    for domain_name in domain_choice['domain']:
        domain = get_domain(domain_name)
        makefiles = {}
        for makefile in domain.makefiles:
            makefiles[makefile.name] = makefile
        print("")
        makefiles_choice = inquirer.prompt([
            inquirer.Checkbox(
                'makefiles',
                message=f'Include makefiles from domain "{domain_name}"',
                choices=makefiles.keys(),
                default=makefiles.keys()
            )
        ])
        for makefile_name in makefiles_choice['makefiles']:
            makefile_settings_questions = []
            for setting in makefiles[makefile_name].settings:
                setting_description = setting.description.replace("\n", " ")
                makefile_settings_questions.append(
                    inquirer.Text(
                        setting.name,
                        message=(
                            f'{setting_description}\n'
                            f'    {setting.name}'
                        ),
                        default=setting.default
                    )
                )
            if not makefile_settings_questions:
                continue
            print("")
            print(f'Makefile: {makefile_name}')
            makefile_settings = inquirer.prompt(makefile_settings_questions)


init_parser = command_parsers.add_parser("init", help="Initialize project")
init_parser.set_defaults(func=init_command)


##############################################################################
# main
##############################################################################

def main() -> None:
    mxdev.setup_logger(logging.INFO)
    args = parser.parse_args()
    args.func(args)
