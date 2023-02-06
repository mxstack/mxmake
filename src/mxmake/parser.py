from mxmake.topics import get_domain

import os
import typing


class MakefileParser:
    def __init__(self, path: str):
        self.path = path
        self.fqns: typing.List = []
        self.topics: typing.Dict = {}
        self.settings: typing.Dict = {}
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
                value = self.parse_setting(lines, setting.name)
                if value is not None:
                    self.settings[f"{fqn}.{setting.name}"] = value

    def parse_setting(
        self, lines: typing.List[str], name: str
    ) -> typing.Union[str, None]:
        setting_scope = False
        value = None
        for line in lines:
            if setting_scope:
                if line:
                    value += f"\n{line}"
                if line.endswith("\\"):
                    continue
                setting_scope = False
                break
            if line.startswith(f"{name}?="):
                value = line[line.find("?=") + 2 :]
                if value.endswith("\\"):
                    setting_scope = True
                    continue
                break
        return value

    def parse(self) -> None:
        if not os.path.exists(self.path):
            return
        with open(self.path) as fd:
            lines = [line.rstrip() for line in fd.readlines() if line.strip()]
            self.parse_fqns(lines)
            self.parse_settings(lines)
