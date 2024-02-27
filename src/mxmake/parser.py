from mxmake.topics import get_domain
from pathlib import Path

import typing


class SettingMissing(Exception):
    """Exception used in parser to indicate a missing setting in an existing
    makefile while parsing.
    """


class MakefileParser:
    def __init__(self, path: Path):
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
                try:
                    value = self.parse_setting(lines, setting.name)
                    self.settings[f"{fqn}.{setting.name}"] = value
                except SettingMissing:
                    continue

    def parse_setting(self, lines: typing.List[str], name: str) -> str:
        setting_missing = True
        setting_scope = False
        value = ""
        for line in lines:
            if setting_scope:
                if line:
                    value += f"\n{line}"
                if line.endswith("\\"):
                    continue
                setting_scope = False
                break
            if line.startswith(f"{name}?="):
                setting_missing = False
                value = line[line.find("?=") + 2 :]
                if value.endswith("\\"):
                    setting_scope = True
                    continue
                break
        if setting_missing:
            raise SettingMissing(name)
        return value

    def parse(self) -> None:
        if not self.path.exists():
            return
        with self.path.open() as fd:
            lines = [line.rstrip() for line in fd.readlines() if line.strip()]
            self.parse_fqns(lines)
            self.parse_settings(lines)
