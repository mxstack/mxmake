from mxmake.parser import MakefileParser
from mxmake.templates import ci_template
from mxmake.templates import get_template_environment
from mxmake.templates import template
from mxmake.topics import collect_missing_dependencies
from mxmake.topics import Domain
from mxmake.topics import get_domain
from mxmake.topics import get_topic
from mxmake.topics import load_topics
from mxmake.topics import resolve_domain_dependencies
from mxmake.topics import set_domain_runtime_depends
from operator import attrgetter
from pathlib import Path
from textwrap import indent

import argparse
import inquirer
import logging
import mxdev
import sys
import typing
import yaml


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
# init/update
##############################################################################


def create_config(
    prompt: bool, preseeds: typing.Union[typing.Dict[str, typing.Any], None]
):
    if prompt and preseeds:
        sys.stdout.write("Either use prompt or preseeds, not both\n")
        sys.exit(1)

    # obtain target folder
    target_folder = Path.cwd()

    # parse existing makefile
    parser = MakefileParser(target_folder / "Makefile")

    # obtain topics to include
    topics = load_topics()
    if preseeds:
        sys.stdout.write("Collect topics from preseeds.\n")
        topic_choice = {"topic": list(preseeds.get("topics", {}).keys())}
    elif not prompt:
        sys.stdout.write("Update Makefile without prompting for settings.\n")
        topic_choice = {"topic": list(parser.topics)}
    else:
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
        sys.stdout.write("No topics selected. Abort\n")
        sys.exit(1)

    # obtain domains to include
    domains: typing.List[Domain] = []
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
        if preseeds:
            selected_fqns = [
                f"{topic_name}.{domain_name}"
                for domain_name in preseeds["topics"][topic_name]
            ]
            sys.stdout.write(f"Collect domains for topic {topic_name} from preseeds.\n")
            domains.extend((get_domain(fqn) for fqn in selected_fqns))
            continue
        if not prompt:
            sys.stdout.write(
                f"- update topic {topic_name} with domains "
                f"{', '.join([fqdn.split('.')[1] for fqdn in selected_fqns])}.\n"
            )
            domains.extend((get_domain(fqn) for fqn in selected_fqns))
            continue
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
            sys.stdout.write("No domains selected. Abort\n")
            sys.exit(1)
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
            # use default setting from preseeds
            if preseeds:
                unset = object()
                preseed_topic = preseeds.get("topics", {}).get(domain.topic)
                preseed_domain = preseed_topic.get(domain.name) if preseed_topic else {}
                preseed_value = (
                    preseed_domain.get(setting.name, unset) if preseed_domain else unset
                )
                if preseed_value is unset:
                    preseed_value = setting_default
            # use configured setting from parser if set
            elif sfqn in parser.settings:
                setting_default = parser.settings[sfqn]
            domain_settings[sfqn] = setting_default
            if not prompt or preseeds:
                continue
            settings_question.append(
                inquirer.Text(sfqn, message=sfqn, default=setting_default)
            )
        if prompt:
            sys.stdout.write(f"Edit Settings for {domain.fqn}?\n")
            yn = inquirer.text(message="y/N")
            if yn in ["Y", "y"]:
                domain_settings.update(inquirer.prompt(settings_question))
            sys.stdout.write("\n")

    if domains:
        # generate makefile
        factory = template.lookup("makefile")
        makefile_template = factory(
            target_folder, domains, domain_settings, get_template_environment()
        )
        makefile_template.write()
    else:
        sys.stdout.write("Skip generation of Makefile, nothing selected\n")

    # mx ini generation
    if prompt and not (target_folder / "mx.ini").exists():
        sys.stdout.write("\n``mx.ini`` configuration file not exists. Create One?\n")
        yn = inquirer.text(message="Y/n")
        if yn not in ["n", "N"]:
            factory = template.lookup("mx.ini")
            mx_ini_template = factory(
                target_folder, domains, get_template_environment()
            )
            mx_ini_template.write()
    elif not prompt and not preseeds and not (target_folder / "mx.ini").exists():
        sys.stdout.write(
            "No generation of mx configuration on update (file does not exist).\n"
        )
    elif preseeds and "mx-ini" in preseeds and not (target_folder / "mx.ini").exists():
        sys.stdout.write("Generate mx configuration file\n")
        factory = template.lookup("mx.ini")
        mx_ini_template = factory(target_folder, domains, get_template_environment())
        mx_ini_template.write()
    else:
        sys.stdout.write(
            "Skip generation of mx configuration file, file already exists\n"
        )

    # ci generation
    if prompt:
        sys.stdout.write("\nDo you want to create CI related files?\n")
        yn = inquirer.text(message="y/N")
        if yn in ["y", "Y"]:
            # ci_template
            ci_choice = inquirer.prompt(
                [
                    inquirer.Checkbox(
                        "ci", message="Generate CI files", choices=ci_template.templates
                    )
                ]
            )
            for template_name in ci_choice["ci"]:
                factory = template.lookup(template_name)
                factory(get_template_environment()).write()
    elif preseeds and "ci-templates" in preseeds:
        for template_name in preseeds["ci-templates"]:
            sys.stdout.write(f"Generate CI file from {template_name} template\n")
            factory = template.lookup(template_name)
            factory(get_template_environment()).write()


def init_command(args: argparse.Namespace):
    sys.stdout.write("\n#######################\n")
    sys.stdout.write("# mxmake initialization\n")
    sys.stdout.write("#######################\n\n")

    prompt = True
    preseeds = None
    if args.preseeds:
        prompt = False
        with open(args.preseeds) as fd:
            preseeds = yaml.load(fd.read(), yaml.SafeLoader)

    create_config(prompt=prompt, preseeds=preseeds)


init_parser = command_parsers.add_parser("init", help="Initialize project")
init_parser.set_defaults(func=init_command)
init_parser.add_argument("-p", "--preseeds", help="Preseeds file")


def update_command(args: argparse.Namespace):
    sys.stdout.write("\n###############\n")
    sys.stdout.write("# mxmake update\n")
    sys.stdout.write("###############\n\n")

    if not Path("Makefile").exists():
        sys.stdout.write("Makefile not exists, abort\n")
        sys.exit(1)

    create_config(prompt=False, preseeds=None)


update_parser = command_parsers.add_parser("update", help="Update makefile")
update_parser.set_defaults(func=update_command)


##############################################################################
# main
##############################################################################


def main() -> None:
    mxdev.setup_logger(logging.INFO)
    args = parser.parse_args()
    args.func(args)
