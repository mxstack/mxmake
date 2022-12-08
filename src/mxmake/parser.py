from mxmake.domains import get_makefile

import typing


class MakefileParser:

    def __init__(self, path: str):
        self.path = path
        self.fqns = []
        self.domains = {}
        self.settings = {}
        self.parse()

    def parse_fqns(self, lines: typing.List[str]):
        for line in lines:
            if line.startswith("#:"):
                fqn = line[2:].strip()
                self.fqns.append(fqn)
                domain, name = fqn.split('.')
                self.domains.setdefault(domain, [])
                self.domains[domain].append(name)

    def parse_settings(self, lines: typing.List[str]):
        for fqn in self.fqns:
            makefile = get_makefile(fqn)
            for setting in makefile.settings:
                for line in lines:
                    if line.startswith(f"{setting.name}?="):
                        value = line[line.find("?=") + 2:]
                        self.settings[f"{fqn}.{setting.name}"] = value

    def parse(self):
        with open(self.path) as fd:
            lines = [line.strip().strip("\n") for line in fd.readlines() if line]
            self.parse_fqns(lines)
            self.parse_settings(lines)
