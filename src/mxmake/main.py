from mxmake.parser import MakefileParser
from mxmake.templates import get_template_environment
from mxmake.templates import template
from mxmake.topics import collect_missing_dependencies
from mxmake.topics import get_domain
from mxmake.topics import get_topic
from mxmake.topics import load_topics
from mxmake.topics import resolve_domain_dependencies
from mxmake.topics import set_domain_runtime_depends
from operator import attrgetter
from textwrap import indent

import argparse
import inquirer
import logging
import mxdev
import os
import sys


logger = logging.getLogger("mxmake")


parser = argparse.ArgumentParser()
command_parsers = parser.add_subparsers(dest="command", required=True)


##############################################################################
# list
##############################################################################


def list_command(args: argparse.Namespace):
    if not args.topic:
        topics = load_topics()
        sys.stdout.write("Topics:\n")
        for topic_ in topics:
            sys.stdout.write(f"  - {topic_.name}\n")
        return

    topic = get_topic(args.topic)
    if topic is None:
        sys.stdout.write(f"Requested topic not found: {args.topic}\n")
        sys.exit(1)

    if not args.domain:
        sys.stdout.write(f"Domains in topic {topic.name}:\n")
        for domain_ in topic.domains:
            description = indent(domain_.description, 4 * " ").strip()
            sys.stdout.write(f"  - {domain_.name}: {description}\n")
        return

    domain = topic.domain(args.domain)
    if domain is None:
        sys.stdout.write(f"Requested domain not found: {args.domain}\n")
        sys.exit(1)

    sys.stdout.write(f"Domain {topic.name}.{domain.name}:\n")
    depends = ", ".join(domain.depends) if domain.depends else "No dependencies"
    sys.stdout.write(f"  Depends: {depends}\n")
    sys.stdout.write("  Targets:")
    targets = domain.targets
    if not targets:
        sys.stdout.write(" No targets provided\n")
    else:
        sys.stdout.write("\n")
        for target in targets:
            description = indent(target.description, 6 * " ").strip()
            sys.stdout.write(f"    {target.name}: {description}\n")
    sys.stdout.write("  Settings:")
    settings = domain.settings
    if not settings:
        sys.stdout.write(" No settings provided\n")
    else:
        sys.stdout.write("\n")
        for setting in settings:
            description = indent(setting.description, 8 * " ").strip()
            sys.stdout.write(
                f"    - {setting.name}: {setting.description}\n"
                f"      - default value: {setting.default}\n"
            )


list_parser = command_parsers.add_parser("list", help="List stuff")
list_parser.set_defaults(func=list_command)
list_parser.add_argument("-t", "--topic", help="Topic name")
list_parser.add_argument("-d", "--domain", help="Domain name")


##############################################################################
# init
##############################################################################


def init_command(args: argparse.Namespace):
    print("\n#######################")
    print("# mxmake initialization")
    print("#######################\n")

    # obtain target folder
    target_folder = os.getcwd()

    # parse existing makefile
    parser = MakefileParser(os.path.join(target_folder, "Makefile"))

    # obtain topics to include
    topics = load_topics()
    topic_choice = inquirer.prompt(
        [
            inquirer.Checkbox(
                "topic",
                message="Include topics",
                choices=[d.name for d in topics],
                default=list(parser.topics),
            )
        ]
    )
    if topic_choice is None:
        return

    # obtain domains to include
    domains = []
    for topic_name in topic_choice["topic"]:
        topic = get_topic(topic_name)
        all_fqns = [domain.fqn for domain in topic.domains]
        # use already configured domains from topic if present in existing
        # domain
        if parser.topics.get(topic_name):
            selected_fqns = [
                f"{topic_name}.{name}" for name in parser.topics[topic_name]
            ]
        # fallback to all domains of topic if not configured yet or no
        # domain generated yet
        else:
            selected_fqns = [domain.fqn for domain in topic.domains]
        domains_choice = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "domains",
                    message=f'Include domains from topic "{topic_name}"',
                    choices=all_fqns,
                    default=selected_fqns,
                )
            ]
        )
        if domains_choice is None:
            return
        for fqn in domains_choice["domains"]:
            domains.append(get_domain(fqn))
    domains = collect_missing_dependencies(domains)
    set_domain_runtime_depends(domains)
    domains = resolve_domain_dependencies(domains)

    # obtain settings
    domain_settings = {}
    for domain in sorted(domains, key=attrgetter("fqn")):
        settings = domain.settings
        if not settings:
            continue
        settings_question = []
        for setting in settings:
            sfqn = f"{domain.fqn}.{setting.name}"
            setting_default = setting.default
            # use configured setting from parser if set
            if sfqn in parser.settings:
                setting_default = parser.settings[sfqn]
            domain_settings[sfqn] = setting_default
            settings_question.append(
                inquirer.Text(sfqn, message=sfqn, default=setting_default)
            )
        print(f"Edit Settings for {domain.fqn}?")
        yn = inquirer.text(message="y/N")
        if yn in ["Y", "y"]:
            domain_settings.update(inquirer.prompt(settings_question))
        print("")

    if domains:
        # generate makefile
        factory = template.lookup("makefile")
        makefile_template = factory(
            target_folder, domains, domain_settings, get_template_environment()
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
                target_folder, domains, get_template_environment()
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
