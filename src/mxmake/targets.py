from dataclasses import dataclass
from pkg_resources import iter_entry_points
import configparser
import typing


@dataclass
class TargetSetting:
    name: str
    description: str
    default: str


@dataclass
class Target:
    name: str
    file: str
    settings: typing.List[TargetSetting]


@dataclass
class Domain:
    name: str
    directory: str

    @property
    def targets(self) -> typing.List[Target]:
        return []


def load_domains() -> typing.List[Domain]:
    return [ep.load()() for ep in iter_entry_points("mxmake") if ep.name == "mxmake.domains"]


LDAP = Domain(
    name='ldap',
    directory='targets/ldap'
)
