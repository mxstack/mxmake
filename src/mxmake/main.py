from mxmake.domains import collect_missing_dependencies
from mxmake.domains import get_domain
from mxmake.domains import get_makefile
from mxmake.domains import load_domains
from mxmake.domains import resolve_makefile_dependencies
from mxmake.templates import template
from mxmake.utils import list_value
from mxmake.utils import ns_name
from operator import attrgetter
from textwrap import indent

import argparse
import inquirer
import logging
import mxdev
import os
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
    depends = ", ".join(makefile.depends) if makefile.depends else "No dependencies"
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
    domain_choice = inquirer.prompt(
        [
            inquirer.Checkbox(
                "domain", message="Include domains", choices=[d.name for d in domains]
            )
        ]
    )
    makefiles = []
    for domain_name in domain_choice["domain"]:
        domain = get_domain(domain_name)
        fqns = [makefile.fqn for makefile in domain.makefiles]
        makefiles_choice = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "makefiles",
                    message=f'Include makefiles from domain "{domain_name}"',
                    choices=fqns,
                    default=fqns,
                )
            ]
        )
        for fqn in makefiles_choice["makefiles"]:
            makefiles.append(get_makefile(fqn))
    makefiles = collect_missing_dependencies(makefiles)
    makefiles = resolve_makefile_dependencies(makefiles)
    settings_question = []
    for makefile in sorted(makefiles, key=attrgetter('fqn')):
        for setting in makefile.settings:
            setting_description = setting.description.replace("\n", " ")
            settings_question.append(
                inquirer.Text(
                    f"{makefile.fqn}.{setting.name}",
                    message=(f"{makefile.fqn}\n{setting_description}\n    {setting.name}"),
                    default=setting.default,
                )
            )
    makefile_settings = inquirer.prompt(settings_question)
    makefile_path = os.path.join(os.getcwd(), 'Makefile')
    with open(makefile_path, 'w') as fd:
        fd.write(80 * "#" + "\n")
        fd.write("# THIS FILE IS GENERATED BY MXMAKE\n")
        fd.write(80 * "#" + "\n\n")
        fd.write("#:[contents]\n")
        fd.write("#:makefiles =\n")
        for makefile in makefiles:
            fd.write(f"#:    {makefile.fqn}\n")
        fd.write("\n")
        fd.write(80 * "#" + "\n")
        fd.write("# SETTINGS\n")
        fd.write(80 * "#" + "\n\n")
        for makefile in makefiles:
            if not makefile.settings:
                continue
            fd.write(f"## {makefile.fqn}\n\n")
            for setting in makefile.settings:
                sfqn = f"{makefile.fqn}.{setting.name}"
                value = makefile_settings[sfqn]
                description = setting.description.replace('\n', ' ')
                fd.write(f"# {description}\n")
                fd.write(f"# default: {setting.default}\n")
                fd.write(f"{setting.name}?={value}\n\n")
        for makefile in makefiles:
            makefile.write_to(fd)
            fd.write("\n")


init_parser = command_parsers.add_parser("init", help="Initialize project")
init_parser.set_defaults(func=init_command)


##############################################################################
# main
##############################################################################

def main() -> None:
    mxdev.setup_logger(logging.INFO)
    args = parser.parse_args()
    args.func(args)
