from jinja2 import Environment
from jinja2 import PackageLoader
from mxmake.topics import Domain
from mxmake.topics import load_topics
from mxmake.utils import gh_actions_path
from mxmake.utils import mxmake_files
from mxmake.utils import ns_name
from pathlib import Path

import abc
import io
import mxdev
import typing


def get_template_environment() -> Environment:
    return Environment(
        loader=PackageLoader("mxmake", "templates"),
        trim_blocks=True,
        keep_trailing_newline=True,
    )


class template:
    """Template decorator and registry."""

    _registry: typing.Dict = dict()

    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, ob: typing.Type["Template"]) -> typing.Type["Template"]:
        ob.name = self.name
        self._registry[self.name] = ob
        return ob

    @classmethod
    def lookup(cls, name: str, bound: bool = False) -> typing.Any:
        # mypy reports errors if we define abstract ``Template`` as return
        # type, return type is always a subclass of ``Template``.
        factory = cls._registry.get(name)
        if not factory:
            raise RuntimeError(f"Template '{name}' not found")
        if bound and not issubclass(factory, MxIniBoundTemplate):
            raise RuntimeError(f"Template '{name}' if no bound template")
        return factory


class Template(abc.ABC):
    name: str
    file_mode: int = 0o644

    def __init__(
        self,
        environment: typing.Union[Environment, None] = None,
    ) -> None:
        # XXX: if environment is None, default to ``get_template_environment``?
        self.environment = environment

    @abc.abstractproperty
    def target_folder(self) -> Path:
        """Target folder for rendered template."""

    @abc.abstractproperty
    def target_name(self) -> str:
        """Target file name for rendered template."""

    @abc.abstractproperty
    def template_name(self) -> str:
        """Template name to use."""

    @abc.abstractproperty
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        """Variables for template rendering."""

    def write(self) -> None:
        """Render template and write result to file system."""
        if not self.environment:
            raise RuntimeError("Cannot write template without environment")
        target_folder = self.target_folder
        target_folder.mkdir(exist_ok=True)
        target_path = target_folder / self.target_name
        template = self.environment.get_template(self.template_name)
        with target_path.open("w") as f:
            f.write(template.render(**self.template_variables))
        target_path.chmod(self.file_mode)

    def remove(self) -> bool:
        """Remove rendered template if exists. Return bool if file existed."""
        target_path = self.target_folder / self.target_name
        try:
            target_path.unlink()
        except FileNotFoundError:
            return False
        return True


class MxIniBoundTemplate(Template):
    """Template which depends on ``mx.ini`` configuration.

    This templates are created by ``mxmake`` hook which expects this object's
    ``__init__`` signature.
    """

    def __init__(
        self,
        config: mxdev.Configuration,
        environment: typing.Union[Environment, None] = None,
    ) -> None:
        super().__init__(environment)
        self.config = config

    @property
    def settings(self) -> typing.Dict[str, str]:
        return self.config.hooks.get(ns_name(self.name), {})


class ShellScriptTemplate(Template):
    description: str = ""
    file_mode: int = 0o755


class EnvironmentTemplate(MxIniBoundTemplate):
    @property
    def env(self) -> typing.Dict[str, str]:
        """Dict containing environment variables."""
        env_name = self.settings.get("environment")
        return self.config.hooks.get(ns_name(env_name), {}) if env_name else {}


##############################################################################
# test script template
##############################################################################


@template("run-tests")
class TestScript(EnvironmentTemplate, ShellScriptTemplate):
    description: str = "Run tests"

    @property
    def test_runner(self):
        return self.config.settings.get("mxmake-test-runner", "pytest")

    @property
    def target_folder(self) -> Path:
        return mxmake_files()

    @property
    def target_name(self) -> str:
        return f"{self.name}.sh"

    @property
    def template_name(self) -> str:
        return f"{self.test_runner}-{self.target_name}"

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        return dict(
            description=self.description,
            env=self.env,
            testpaths=self.package_paths(ns_name("test-path")),
        )

    def package_paths(self, attr: str) -> typing.List[str]:
        paths = list()
        for name, package in self.config.packages.items():
            if attr not in package:
                continue
            for line in package[attr].split("\n"):
                if not line:
                    continue
                path = f"{package['target']}/{name}/{line}".rstrip("/")
                paths.append(path)
        if attr in self.config.settings:
            for line in self.config.settings[attr].split("\n"):
                if not line:
                    continue
                path = line.rstrip("/")
                paths.append(line.rstrip("/"))
        return paths


##############################################################################
# coverage script template
##############################################################################


@template("run-coverage")
class CoverageScript(TestScript):
    description: str = "Run coverage"

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        variables = super().template_variables
        variables["sourcepaths"] = self.package_paths(ns_name("source-path"))
        variables["omitpaths"] = self.package_paths(ns_name("omit-path"))
        return variables


##############################################################################
# pip config template
##############################################################################


@template("pip-conf")
class PipConf(MxIniBoundTemplate):
    description: str = "Pip config"
    target_name: str = "pip.conf"
    template_name: str = "pip.conf"

    @property
    def target_folder(self) -> Path:
        return mxmake_files()

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        return dict(
            find_links=[
                link.strip()
                for link in self.settings.get("find-links", "").split("\n")
                if link.strip()
            ]
        )


##############################################################################
# makefile template
##############################################################################


@template("makefile")
class Makefile(Template):
    description: str = "Makefile"
    target_name = "Makefile"
    template_name = "Makefile"
    target_folder = Path()

    def __init__(
        self,
        target_folder: Path,
        domains: typing.List[Domain],
        domain_settings: typing.Dict[str, str],
        environment: typing.Union[Environment, None] = None,
    ) -> None:
        super().__init__(environment)
        self.target_folder = target_folder
        self.domains = domains
        self.domain_settings = domain_settings

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        # collect domain settings
        settings = []
        for domain in self.domains:
            if not domain.settings:
                continue
            domain_setting = dict(fqn=domain.fqn, settings=[])
            settings.append(domain_setting)
            for setting in domain.settings:
                sfqn = f"{domain.fqn}.{setting.name}"
                domain_setting["settings"].append(
                    dict(
                        name=setting.name,
                        description=setting.description.split("\n"),
                        default=setting.default,
                        value=self.domain_settings[sfqn],
                    )
                )
        # render domain sections
        sections = io.StringIO()
        for domain in self.domains:
            sections.write("\n")
            domain.write_to(sections)
        sections.seek(0)
        # collect fqns of used domains
        fqns = sorted([domain.fqn for domain in self.domains])
        additional_targets = {}
        topics = {domain.topic for domain in self.domains}
        additional_targets["qa"] = "qa" in topics
        # additional_targets["docs"] = "docs" in topics
        # return template variables
        return dict(
            settings=settings,
            sections=sections,
            fqns=fqns,
            additional_targets=additional_targets,
        )


##############################################################################
# additional sources targets
##############################################################################


@template("additional_sources_targets")
class AdditionalSourcesTargets(Template):
    description: str = "Additional sources targets"
    target_name = "additional_sources_targets.mk"
    template_name = "additional_sources_targets.mk"

    def __init__(
        self,
        additional_sources_targets: typing.List[str],
        environment: typing.Union[Environment, None] = None,
    ) -> None:
        super().__init__(environment)
        self.additional_sources_targets = additional_sources_targets

    @property
    def target_folder(self) -> Path:
        return mxmake_files()

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        return dict(additional_sources_targets=self.additional_sources_targets)


##############################################################################
# mx.ini template
##############################################################################


@template("mx.ini")
class MxIni(Template):
    description: str = "mx configutation file"
    target_name = "mx.ini"
    template_name = "mx.ini"
    target_folder = Path()

    def __init__(
        self,
        target_folder: Path,
        domains: typing.List[Domain],
        environment: typing.Union[Environment, None] = None,
    ) -> None:
        super().__init__(environment)
        self.target_folder = target_folder
        self.domains = domains

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        mxmake_templates = []
        for domain in self.domains:
            if domain.fqn == "qa.test":
                mxmake_templates.append("run-tests")
            if domain.fqn == "qa.coverage":
                mxmake_templates.append("run-coverage")
        return dict(mxmake_templates=mxmake_templates)


##############################################################################
# topics.rst template
##############################################################################


@template("topics.md")
class Topics(Template):
    description: str = "Topics documentation for sphinx"
    target_name = ""
    template_name = "topics.md"
    target_folder = Path()

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        topics = load_topics()
        return {"topics": topics}

    def render(self):
        if not self.environment:
            raise RuntimeError("Cannot write template without environment")
        template = self.environment.get_template(self.template_name)
        return template.render(**self.template_variables)

    def write(self) -> None:
        raise NotImplementedError(
            "Topics template is not supposed to be written to file system"
        )


##############################################################################
# dependencies.md template
##############################################################################


@template("dependencies.md")
class Dependencies(Template):
    description: str = "Dependencies documentation for sphinx"
    target_name = ""
    template_name = "dependencies.md"
    target_folder = Path()

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        topics = load_topics()
        return {"topics": topics}

    def render(self):
        if not self.environment:
            raise RuntimeError("Cannot write template without environment")
        template = self.environment.get_template(self.template_name)
        return template.render(**self.template_variables)

    def write(self) -> None:
        raise NotImplementedError(
            "Dependencies template is not supposed to be written to file system"
        )


##############################################################################
# CI
##############################################################################


class ci_template:
    templates: typing.List = list()

    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, ob: typing.Type["Template"]) -> typing.Type["Template"]:
        template(self.name)(ob)
        self.templates.append(self.name)
        return ob


class GHActionsTemplate(Template):
    template_variables = dict()

    @property
    def target_folder(self) -> Path:
        return gh_actions_path()


##############################################################################
# gh-actions-docs template
##############################################################################


@ci_template("gh-actions-docs")
class GHActionsDocs(GHActionsTemplate):
    description: str = "Github action for generating docs"
    target_name = "docs.yml"
    template_name = "gh-actions-docs.yml"


##############################################################################
# gh-actions-lint template
##############################################################################


@ci_template("gh-actions-lint")
class GHActionsLint(GHActionsTemplate):
    description: str = "Github action to run linting"
    target_name = "lint.yml"
    template_name = "gh-actions-lint.yml"


##############################################################################
# gh-actions-test template
##############################################################################


@ci_template("gh-actions-test")
class GHActionsTest(GHActionsTemplate):
    description: str = "Github action to run tests"
    target_name = "test.yml"
    template_name = "gh-actions-test.yml"


##############################################################################
# gh-actions-typecheck template
##############################################################################


@ci_template("gh-actions-typecheck")
class GHActionsTypecheck(GHActionsTemplate):
    description: str = "Github action to running static type checks"
    target_name = "typecheck.yml"
    template_name = "gh-actions-typecheck.yml"
