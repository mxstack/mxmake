from dataclasses import dataclass
from pkg_resources import iter_entry_points
import configparser
import io
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

    @property
    def file_data(self) -> typing.List[str]:
        if hasattr(self, '_file_data'):
            return self._file_data
        with open(self.file) as f:
            self.file_data = f.readlines()
        return self._file_data

    @file_data.setter
    def file_data(self, value: typing.List[str]):
        self._file_data = value

    @property
    def config(self) -> configparser.ConfigParser:
        if hasattr(self, '_config'):
            return self._config
        data = io.StringIO()
        for line in self.file_data:
            if line.startswith('#:'):
                data.write(line[2:])
        data.seek(0)
        config = self.config = configparser.ConfigParser(
            default_section=self.name,
            interpolation=configparser.ExtendedInterpolation()
        )
        config.optionxform = str  # type: ignore
        config.read_file(data)
        return self._config

    @config.setter
    def config(self, value: configparser.ConfigParser):
        self._config = value

    @property
    def title(self) -> str:
        return self.config[self.name].get('title', 'No Title')

    @property
    def description(self) -> str:
        return self.config[self.name].get('description', 'No Description')

    @property
    def depends(self) -> str:
        return self.config[self.name].get('depends', '')

    @property
    def settings(self) -> typing.List[TargetSetting]:
        config = self.config
        return [
            TargetSetting(
                name=name,
                description=config[name].get('description', 'No Description'),
                default=config[name].get('default', 'No Default')
            ) for name in config.sections()
        ]

    def write_to(self, path: str):
        leading_blankline = True
        with open(path, 'w') as f:
            for line in self.file_data:
                if line.startswith('#:'):
                    continue
                if not line.strip().strip('\n') and leading_blankline:
                    continue
                else:
                    leading_blankline = False
                f.write(line)

@dataclass
class Domain:
    name: str
    directory: str

    @property
    def targets(self) -> typing.List[Target]:
        return []


def load_domains() -> typing.List[Domain]:
    return [ep.load() for ep in iter_entry_points("mxmake.domains")]


LDAP = Domain(
    name='ldap',
    directory='targets/ldap'
)
