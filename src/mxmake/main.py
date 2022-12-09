from mxmake.domains import collect_missing_dependencies
from mxmake.domains import get_domain
from mxmake.domains import get_makefile
from mxmake.domains import load_domains
from mxmake.domains import resolve_makefile_dependencies
from mxmake.parser import MakefileParser
from mxmake.templates import get_template_environment
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
    print("\n#######################")
    print("# mxmake initialization")
    print("#######################\n")

    # obtain makefile target folder
    target_folder = os.getcwd()

    # parse existing makefile
    parser = MakefileParser(os.path.join(target_folder, "Makefile"))

    # obtain domains to include
    domains = load_domains()
    domain_choice = inquirer.prompt(
        [
            inquirer.Checkbox(
                "domain",
                message="Include domains",
                choices=[d.name for d in domains],
                default=parser.domains.keys(),
            )
        ]
    )
    if domain_choice is None:
        return

    # obtain makefiles to include
    makefiles = []
    for domain_name in domain_choice["domain"]:
        domain = get_domain(domain_name)
        all_fqns = [makefile.fqn for makefile in domain.makefiles]
        # use already configured makefiles from domain if present in existing
        # makefile
        if parser.domains.get(domain_name):
            selected_fqns = [
                f"{domain_name}.{name}" for name in parser.domains[domain_name]
            ]
        # fallback to all makefiles of domain if not configured yet or no
        # makefile generated yet
        else:
            selected_fqns = [makefile.fqn for makefile in domain.makefiles]
        makefiles_choice = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "makefiles",
                    message=f'Include makefiles from domain "{domain_name}"',
                    choices=all_fqns,
                    default=selected_fqns,
                )
            ]
        )
        if makefiles_choice is None:
            return
        for fqn in makefiles_choice["makefiles"]:
            makefiles.append(get_makefile(fqn))
    makefiles = collect_missing_dependencies(makefiles)
    makefiles = resolve_makefile_dependencies(makefiles)

    # obtain settings
    makefile_settings = {}
    for makefile in sorted(makefiles, key=attrgetter("fqn")):
        settings = makefile.settings
        if not settings:
            continue
        settings_question = []
        for setting in settings:
            sfqn = f"{makefile.fqn}.{setting.name}"
            setting_default = setting.default
            # use configured setting from parser if set
            if sfqn in parser.settings:
                setting_default = parser.settings[sfqn]
            makefile_settings[sfqn] = setting_default
            settings_question.append(
                inquirer.Text(sfqn, message=sfqn, default=setting_default)
            )
        print(f"Edit Settings for {makefile.fqn}?")
        yn = inquirer.text(message="y/N")
        if yn in ["Y", "y"]:
            makefile_settings.update(inquirer.prompt(settings_question))
        print("")

    if makefiles:
        # generate makefile
        factory = template.lookup("makefile")
        makefile_template = factory(
            target_folder, makefiles, makefile_settings, get_template_environment()
        )
        makefile_template.write()
    else:
        print("Skip generation of Makefile, nothing selected")

    # mx ini generation
    if not os.path.exists(os.path.join(target_folder, "mx.ini")):
        print("\n``mx.ini`` configuration file not exists. Create One?")
        yn = inquirer.text(message="Y/n")
        if yn not in ["n", "N"]:
            factory = template.lookup("mx.ini")
            mx_ini_template = factory(
                target_folder, makefiles, get_template_environment()
            )
            mx_ini_template.write()
    else:
        print("Skip generation of mx configuration file, file already exists")


init_parser = command_parsers.add_parser("init", help="Initialize project")
init_parser.set_defaults(func=init_command)


##############################################################################
# main
##############################################################################


def main() -> None:
    mxdev.setup_logger(logging.INFO)
    args = parser.parse_args()
    args.func(args)
