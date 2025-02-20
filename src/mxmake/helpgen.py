from .parser import MakefileParser
from .topics import get_domain
from .topics import get_topic
from .topics import resolve_domain_dependencies
from .topics import set_domain_runtime_depends

import os
import sys
import textwrap


def print_help(makefile: "pathlib.Path"):
    """Parse the Makefile and print the help."""

    parser = MakefileParser(makefile)

    sys.stdout.write("\nUsage: make <target> [ARGUMENT1=value1] [ARGUMENT2=value2]\n\n")
    help_domain = os.environ.get("HELP_DOMAIN")
    if help_domain:
        sys.stdout.write(f"Help for domain '{help_domain}'\n\n")
    else:
        sys.stdout.write("Available targets:\n\n")

    domains = [get_domain(fqn) for fqn in parser.fqns]
    set_domain_runtime_depends(domains)
    idnt = "    "
    lvl = 1
    found = False
    for domain in resolve_domain_dependencies(domains):
        if help_domain and domain.name != help_domain:
            continue
        topic = get_topic(domain.topic)
        sys.stdout.write(
            f"DOMAIN '{domain.name}' (topic {topic.title})\n"
        )
        sys.stdout.write(
            "\n".join(
                textwrap.wrap(
                    domain.description,
                    width=79,
                    initial_indent=idnt * lvl,
                    subsequent_indent=idnt * lvl,
                )
            )
        )
        sys.stdout.write("\n\nTARGETS\n\n")
        for target in domain.targets:
            sys.stdout.write(f"{idnt*lvl}{target.name}\n")
            if help_domain:
                lvl += 1
                found = True
                sys.stdout.write(
                    "\n".join(
                        textwrap.wrap(
                            target.description,
                            width=79,
                            initial_indent=idnt * (lvl),
                            subsequent_indent=idnt * (lvl),
                        )
                    )
                )
                sys.stdout.write("\n\n")
                lvl -= 1
        if help_domain:
            sys.stdout.write(f"ARGUMENTS\n\n")
            for setting in domain.settings:
                fqn_setting = f"{domain.fqn}.{setting.name}"
                sys.stdout.write(
                    f"{idnt*lvl}{setting.name}={parser.settings.get(fqn_setting) or '<not set>'}\n"
                )
                sys.stdout.write(
                    "\n".join(
                        textwrap.wrap(
                            setting.description,
                            width=79,
                            initial_indent=idnt * (lvl + 1),
                            subsequent_indent=idnt * (lvl + 1),
                        )
                    )
                )
                sys.stdout.write("\n\n")
        else:
            sys.stdout.write("\n\n")


    if not help_domain:
        sys.stdout.write("")
        sys.stdout.write(
            "Need detailed help by domain containing all information?\nRun:\n\n    make help HELP_DOMAIN=<domain>\n"
        )
    elif not found:
        sys.stdout.write("No help found for requested domain st\n")
        sys.exit(1)