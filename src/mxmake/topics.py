from collections import Counter
from dataclasses import dataclass
from importlib.metadata import entry_points
from pathlib import Path

import configparser
import functools
import io
import operator
import typing


try:
    # do we have Python 3.12+
    from importlib.metadata import EntryPoints  # type: ignore # noqa: F401

    HAS_IMPORTLIB_ENTRYPOINTS = True
except ImportError:
    HAS_IMPORTLIB_ENTRYPOINTS = False


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
class Domain:
    topic: str
    name: str
    file: Path

    def __post_init__(self) -> None:
        # Runtime dependencies contain the list of dependencies used for
        # generating the makefile.
        #
        # They are computed by `set_domain_runtime_depends` and consist of
        # The hard dependencies and all soft dependencies included in domain
        # list.
        self.runtime_depends: typing.List[str] = []

    @property
    def fqn(self):
        return f"{self.topic}.{self.name}"

    @property
    def file_data(self) -> typing.List[str]:
        if (_file_data := getattr(self, "_file_data", None)) is not None:
            return _file_data
        with self.file.open() as f:
            self.file_data = f.readlines()
        return self._file_data

    @file_data.setter
    def file_data(self, value: typing.List[str]):
        self._file_data = value

    @property
    def config(self) -> configparser.ConfigParser:
        if (_config := getattr(self, "_config", None)) is not None:
            return _config
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
    def soft_depends(self) -> typing.List[str]:
        return [
            dep.strip()
            for dep in self.config[self.name].get("soft-depends", "").split("\n")
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


@dataclass(unsafe_hash=True)
class Topic:
    name: str
    directory: Path

    def __post_init__(self) -> None:
        config = configparser.ConfigParser(default_section="metadata")
        config.read(self.directory / "metadata.ini")
        self.title = config.get("metadata", "title")
        self.description = config.get("metadata", "description")

    @property
    def domains(self) -> typing.List[Domain]:
        return [
            Domain(
                topic=self.name,
                name=name.stem,
                file=self.directory / name,
            )
            for name in sorted(self.directory.iterdir())
            if name.suffix == ".mk"
        ]

    def domain(self, name: str) -> typing.Optional[Domain]:
        for domain in self.domains:
            if domain.name == name:
                return domain
        return None


@functools.lru_cache(maxsize=4096)
def load_topics() -> typing.List[Topic]:
    if HAS_IMPORTLIB_ENTRYPOINTS:
        topics_eps = entry_points(group="mxmake.topics")  # type: ignore
    else:
        eps = entry_points()
        if "mxmake.topics" not in eps:
            return []
        topics_eps = eps["mxmake.topics"]  # type: ignore
    # XXX: for some reasons entry points are loaded twice. not sure if this
    #      is a glitch when installing with uv or something related to
    #      importlib.metadata.entry_points
    return list(set([ep.load() for ep in topics_eps]))  # type: ignore


def get_topic(name: str) -> Topic:
    for topic in load_topics():
        if topic.name == name:
            return topic
    raise AttributeError(f"No such topic: {name}")


def get_domain(fqn: str) -> Domain:
    topic_name, name = fqn.split(".")
    topic = get_topic(topic_name)
    domain = topic.domain(name)
    if not domain:
        raise AttributeError(f"No such domain: {fqn}")
    return domain


class DomainConflictError(Exception):
    def __init__(self, counter: Counter):
        conflicting = list()
        for name, count in counter.items():
            if count > 1:
                conflicting.append(name)
        msg = "Conflicting domain names: {}".format(sorted(conflicting))
        super(DomainConflictError, self).__init__(msg)


class CircularDependencyDomainError(Exception):
    def __init__(self, domains: typing.List[Domain]):
        msg = "Domains define circular dependencies: {}".format(domains)
        super(CircularDependencyDomainError, self).__init__(msg)


class MissingDependencyDomainError(Exception):
    def __init__(self, domain: Domain):
        msg = "Domain define missing dependency: {}".format(domain)
        super(MissingDependencyDomainError, self).__init__(msg)


def resolve_domain_dependencies(
    domains: typing.List[Domain],
) -> typing.List[Domain]:
    """Return given domains ordered by dependencies.

    :raise DomainConflictError: Domain list contains conflicting names.
    :raise MissingDependencyDomainError: Dependency domain not included.
    :raise CircularDependencyDomainError: Circular dependencies defined.
    """
    names = [res.fqn for res in domains]
    counter = Counter(names)
    if len(domains) != len(counter):
        raise DomainConflictError(counter)
    ret = []
    handled = {}
    for domain in domains[:]:
        if not domain.runtime_depends:
            ret.append(domain)
            handled[domain.fqn] = domain
            domains.remove(domain)
        else:
            for dependency_name in domain.runtime_depends:
                if dependency_name not in names:
                    raise MissingDependencyDomainError(domain)
    count = len(domains)
    while count > 0:
        count -= 1
        for domain in domains[:]:
            hook_idx = 0
            not_yet = False
            for dependency_name in domain.runtime_depends:
                if dependency_name in handled:
                    dependency = handled[dependency_name]
                    dep_idx = ret.index(dependency)
                    hook_idx = dep_idx if dep_idx > hook_idx else hook_idx
                else:
                    not_yet = True
                    break
            if not_yet:
                continue
            ret.insert(hook_idx + 1, domain)
            handled[domain.fqn] = domain
            domains.remove(domain)
            break
    if domains:
        raise CircularDependencyDomainError(domains)
    return ret


def collect_missing_dependencies(
    domains: typing.List[Domain],
) -> typing.List[Domain]:
    """Expect a list of domain instances, and add all missing depencecy
    domains.
    """
    to_check = {domain.fqn for domain in domains}
    checked = set()
    while to_check:
        current_fqn = to_check.pop()
        checked.add(current_fqn)
        new_depends = set(get_domain(current_fqn).depends) - checked
        if new_depends:
            to_check.update(new_depends)
    return sorted(
        [get_domain(domain_name) for domain_name in checked],
        key=operator.attrgetter("fqn"),
    )


def set_domain_runtime_depends(domains: typing.List[Domain]) -> None:
    """Expect a list of domain instances, and set runtime_depends on each
    domain, which consists of the hard dependencies and the soft dependencies
    which are contained in domains.
    """
    all_fqns = [domain.fqn for domain in domains]
    for domain in domains:
        runtime_depends = domain.depends
        for fqn in domain.soft_depends:
            if fqn in all_fqns:
                runtime_depends.append(fqn)
        domain.runtime_depends = runtime_depends


##############################################################################
# topics shipped within mxmake
##############################################################################

topics_dir = Path(__file__).parent / "topics"

core = Topic(name="core", directory=topics_dir / "core")
docs = Topic(name="docs", directory=topics_dir / "docs")
js = Topic(name="js", directory=topics_dir / "js")
ldap = Topic(name="ldap", directory=topics_dir / "ldap")
qa = Topic(name="qa", directory=topics_dir / "qa")
system = Topic(name="system", directory=topics_dir / "system")
applications = Topic(name="applications", directory=topics_dir / "applications")
i18n = Topic(name="i18n", directory=topics_dir / "i18n")
