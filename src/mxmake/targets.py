from collections import Counter
from dataclasses import dataclass
from pkg_resources import iter_entry_points
import configparser
import functools
import io
import os
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
        return [
            Target(
                name=name.rstrip('.mk'),
                file=os.path.join(self.directory, name)
            )
            for name in sorted(os.listdir(self.directory))
            if name.endswith('.mk')
        ]


@functools.lru_cache(maxsize=4096)
def load_domains() -> typing.List[Domain]:
    return [ep.load() for ep in iter_entry_points("mxmake.domains")]


def get_domain(name: str) -> Domain:
    for domain in load_domains():
        if domain.name == name:
            return domain


class TargetConflictError(Exception):

    def __init__(self, counter: Counter):
        conflicting = list()
        for name, count in counter.items():
            if count > 1:
                conflicting.append(name)
        msg = 'Conflicting target names: {}'.format(sorted(conflicting))
        super(TargetConflictError, self).__init__(msg)


class CircularDependencyTargetError(Exception):

    def __init__(self, targets: typing.List[Target]):
        msg = 'Targets define circular dependencies: {}'.format(targets)
        super(CircularDependencyTargetError, self).__init__(msg)


class MissingDependencyTargetError(Exception):

    def __init__(self, target: Target):
        msg = 'Target define missing dependency: {}'.format(target)
        super(MissingDependencyTargetError, self).__init__(msg)


def resolve_target_dependencies(
    targets: typing.List[Target]
) -> typing.List[Target]:
    """Return given targets ordered by dependencies.

    :raise TargetConflictError: Target list contains conflicting names.
    :raise MissingDependencyTargetError: Dependency target not included.
    :raise CircularDependencyTargetError: Circular dependencies defined.
    """
    names = [res.name for res in targets]
    counter = Counter(names)
    if len(targets) != len(counter):
        raise TargetConflictError(counter)
    ret = []
    handled = {}
    for target in targets[:]:
        if not target.depends:
            ret.append(target)
            handled[target.name] = target
            targets.remove(target)
        elif target.depends not in names:
            raise MissingDependencyTargetError(target)
    count = len(targets)
    while count > 0:
        count -= 1
        for target in targets[:]:
            if target.depends in handled:
                dependency = handled[target.depends]
                index = ret.index(dependency)
                ret.insert(index + 1, target)
                handled[target.name] = target
                targets.remove(target)
                break
    if targets:
        raise CircularDependencyTargetError(targets)
    return ret


##############################################################################
# domains shipped within mxmake
##############################################################################

targets_dir = os.path.join(os.path.dirname(__file__), 'targets')

core = Domain(
    name='core',
    directory=os.path.join(targets_dir, 'core')
)
ldap = Domain(
    name='ldap',
    directory=os.path.join(targets_dir, 'ldap')
)
