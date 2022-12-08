from collections import Counter
from dataclasses import dataclass
from pkg_resources import iter_entry_points

import configparser
import functools
import io
import operator
import os
import typing


@dataclass
class Setting:
    name: str
    description: str
    default: str


@dataclass
class Target:
    name: str
    description: str


@dataclass
class Makefile:
    domain: str
    name: str
    file: str

    @property
    def fqn(self):
        return f"{self.domain}.{self.name}"

    @property
    def file_data(self) -> typing.List[str]:
        if hasattr(self, "_file_data"):
            return self._file_data
        with open(self.file) as f:
            self.file_data = f.readlines()
        return self._file_data

    @file_data.setter
    def file_data(self, value: typing.List[str]):
        self._file_data = value

    @property
    def config(self) -> configparser.ConfigParser:
        if hasattr(self, "_config"):
            return self._config
        data = io.StringIO()
        for line in self.file_data:
            if line.startswith("#:"):
                data.write(line[2:])
        data.seek(0)
        config = self.config = configparser.ConfigParser(default_section=self.name)
        config.optionxform = str  # type: ignore
        config.read_file(data)
        return self._config

    @config.setter
    def config(self, value: configparser.ConfigParser):
        self._config = value

    @property
    def title(self) -> str:
        return self.config[self.name].get("title", "No Title")

    @property
    def description(self) -> str:
        return self.config[self.name].get("description", "No Description")

    @property
    def depends(self) -> typing.List[str]:
        return [
            dep.strip()
            for dep in self.config[self.name].get("depends", "").split("\n")
            if dep
        ]

    @property
    def settings(self) -> typing.List[Setting]:
        config = self.config
        return [
            Setting(
                name=name[8:],
                description=config[name].get("description", "No Description"),
                default=config[name].get("default", "No Default"),
            )
            for name in config.sections()
            if name.startswith("setting.")
        ]

    @property
    def targets(self) -> typing.List[Target]:
        config = self.config
        return [
            Target(
                name=name[7:],
                description=config[name].get("description", "No Description"),
            )
            for name in config.sections()
            if name.startswith("target.")
        ]

    def write_to(self, fd: typing.TextIO):
        leading_blankline = True
        for line in self.file_data:
            if line.startswith("#:"):
                continue
            if not line.strip().strip("\n") and leading_blankline:
                continue
            else:
                leading_blankline = False
            fd.write(line)


@dataclass
class Domain:
    name: str
    directory: str

    @property
    def makefiles(self) -> typing.List[Makefile]:
        return [
            Makefile(
                domain=self.name,
                name=name[:-3],
                file=os.path.join(self.directory, name),
            )
            for name in sorted(os.listdir(self.directory))
            if name.endswith(".mk")
        ]

    def makefile(self, name: str) -> typing.Optional[Makefile]:
        for makefile in self.makefiles:
            if makefile.name == name:
                return makefile
        return None


@functools.lru_cache(maxsize=4096)
def load_domains() -> typing.List[Domain]:
    return [ep.load() for ep in iter_entry_points("mxmake.domains")]


def get_domain(name: str) -> Domain:
    for domain in load_domains():
        if domain.name == name:
            return domain
    raise AttributeError(f"No such domain: {name}")


def get_makefile(fqn: str) -> Makefile:
    domain_name, name = fqn.split(".")
    domain = get_domain(domain_name)
    makefile = domain.makefile(name)
    if not makefile:
        raise AttributeError(f"No such makefile: {fqn}")
    return makefile


class MakefileConflictError(Exception):
    def __init__(self, counter: Counter):
        conflicting = list()
        for name, count in counter.items():
            if count > 1:
                conflicting.append(name)
        msg = "Conflicting makefile names: {}".format(sorted(conflicting))
        super(MakefileConflictError, self).__init__(msg)


class CircularDependencyMakefileError(Exception):
    def __init__(self, makefiles: typing.List[Makefile]):
        msg = "Makefiles define circular dependencies: {}".format(makefiles)
        super(CircularDependencyMakefileError, self).__init__(msg)


class MissingDependencyMakefileError(Exception):
    def __init__(self, makefile: Makefile):
        msg = "Makefile define missing dependency: {}".format(makefile)
        super(MissingDependencyMakefileError, self).__init__(msg)


def resolve_makefile_dependencies(
    makefiles: typing.List[Makefile],
) -> typing.List[Makefile]:
    """Return given makefiles ordered by dependencies.

    :raise MakefileConflictError: Makefile list contains conflicting names.
    :raise MissingDependencyMakefileError: Dependency makefile not included.
    :raise CircularDependencyMakefileError: Circular dependencies defined.
    """
    names = [res.fqn for res in makefiles]
    counter = Counter(names)
    if len(makefiles) != len(counter):
        raise MakefileConflictError(counter)
    ret = []
    handled = {}
    for makefile in makefiles[:]:
        if not makefile.depends:
            ret.append(makefile)
            handled[makefile.fqn] = makefile
            makefiles.remove(makefile)
        else:
            for dependency_name in makefile.depends:
                if dependency_name not in names:
                    raise MissingDependencyMakefileError(makefile)
    count = len(makefiles)
    while count > 0:
        count -= 1
        for makefile in makefiles[:]:
            hook_idx = 0
            not_yet = False
            for dependency_name in makefile.depends:
                if dependency_name in handled:
                    dependency = handled[dependency_name]
                    dep_idx = ret.index(dependency)
                    hook_idx = dep_idx if dep_idx > hook_idx else hook_idx
                else:
                    not_yet = True
                    break
            if not_yet:
                continue
            ret.insert(hook_idx + 1, makefile)
            handled[makefile.fqn] = makefile
            makefiles.remove(makefile)
            break
    if makefiles:
        raise CircularDependencyMakefileError(makefiles)
    return ret


def collect_missing_dependencies(
    makefiles: typing.List[Makefile],
) -> typing.List[Makefile]:
    """Expect a list of makefile instances, and add all missing depencecy
    makefiles.
    """
    to_check = {makefile.fqn for makefile in makefiles}
    checked = set()
    while to_check:
        current_fqn = to_check.pop()
        checked.add(current_fqn)
        new_depends = set(get_makefile(current_fqn).depends) - checked
        if new_depends:
            to_check.update(new_depends)
    return sorted(
        [get_makefile(makefile_name) for makefile_name in checked],
        key=operator.attrgetter("fqn"),
    )


##############################################################################
# domains shipped within mxmake
##############################################################################

domains_dir = os.path.join(os.path.dirname(__file__), "domains")

core = Domain(name="core", directory=os.path.join(domains_dir, "core"))
ldap = Domain(name="ldap", directory=os.path.join(domains_dir, "ldap"))
