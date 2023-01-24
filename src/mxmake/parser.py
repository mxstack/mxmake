from mxmake.topics import get_domain

import os
import typing


class MakefileParser:
    def __init__(self, path: str):
        self.path = path
        self.fqns = []
        self.topics = {}
        self.settings = {}
        self.parse()

    def parse_fqns(self, lines: typing.List[str]):
        for line in lines:
            if line.startswith("#:"):
                fqn = line[2:].strip()
                self.fqns.append(fqn)
                topic, name = fqn.split(".")
                self.topics.setdefault(topic, [])
                self.topics[topic].append(name)

    def parse_settings(self, lines: typing.List[str]):
        for fqn in self.fqns:
            domain = get_domain(fqn)
            for setting in domain.settings:
                for line in lines:
                    if line.startswith(f"{setting.name}?="):
                        value = line[line.find("?=") + 2 :]
                        self.settings[f"{fqn}.{setting.name}"] = value

    def parse(self):
        if not os.path.exists(self.path):
            return
        with open(self.path) as fd:
            lines = [line.strip().strip("\n") for line in fd.readlines() if line]
            self.parse_fqns(lines)
            self.parse_settings(lines)
