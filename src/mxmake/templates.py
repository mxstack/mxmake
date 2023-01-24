from jinja2 import Environment
from jinja2 import PackageLoader
from mxmake.topics import Makefile
from mxmake.utils import ns_name
from mxmake.utils import scripts_folder
from mxmake.utils import venv_folder

import abc
import io
import mxdev
import os
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
    def lookup(cls, name: str) -> typing.Union[typing.Type["Template"], None]:
        return cls._registry.get(name)


class Template(abc.ABC):
    name: str
    file_mode: int = 0o644

    def __init__(
        self,
        environment: typing.Union[Environment, None] = None,
    ) -> None:
        self.environment = environment

    @abc.abstractproperty
    def target_folder(self) -> str:
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
        os.makedirs(target_folder, exist_ok=True)
        target_path = os.path.join(target_folder, self.target_name)
        template = self.environment.get_template(self.template_name)
        with open(target_path, "w") as f:
            f.write(template.render(**self.template_variables))
        os.chmod(target_path, self.file_mode)

    def remove(self) -> bool:
        """Remove rendered template if exists. Return bool if file existed."""
        target_path = os.path.join(self.target_folder, self.target_name)
        if os.path.exists(target_path):
            os.remove(target_path)
            return True
        return False


class MxIniBoundTemplate(Template):
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
    def target_folder(self) -> str:
        return scripts_folder()

    @property
    def target_name(self) -> str:
        return f"{self.name}.sh"

    @property
    def template_name(self) -> str:
        return self.target_name

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        return dict(
            description=self.description,
            env=self.env,
            venv=venv_folder(),
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
# makefile template
##############################################################################


@template("makefile")
class Makefile(Template):
    description: str = "Makefile"
    target_name = "Makefile"
    template_name = "Makefile"
    target_folder = None

    def __init__(
        self,
        target_folder: str,
        makefiles: typing.List[Makefile],
        makefile_settings: typing.Dict[str, str],
        environment: typing.Union[Environment, None] = None,
    ) -> None:
        super().__init__(environment)
        self.target_folder = target_folder
        self.makefiles = makefiles
        self.makefile_settings = makefile_settings

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        # collect makefile settings
        settings = []
        for makefile in self.makefiles:
            if not makefile.settings:
                continue
            makefile_setting = dict(fqn=makefile.fqn, settings=[])
            settings.append(makefile_setting)
            for setting in makefile.settings:
                sfqn = f"{makefile.fqn}.{setting.name}"
                makefile_setting["settings"].append(
                    dict(
                        name=setting.name,
                        description=setting.description.split("\n"),
                        default=setting.default,
                        value=self.makefile_settings[sfqn],
                    )
                )
        # render makefile sections
        sections = io.StringIO()
        for makefile in self.makefiles:
            sections.write("\n")
            makefile.write_to(sections)
        sections.seek(0)
        # collect fqns of used makefiles
        fqns = [makefile.fqn for makefile in self.makefiles]
        # return template variables
        return dict(settings=settings, sections=sections, fqns=fqns)


##############################################################################
# mx.ini template
##############################################################################


@template("mx.ini")
class MxIni(Template):
    description: str = "mx configutation file"
    target_name = "mx.ini"
    template_name = "mx.ini"
    target_folder = None

    def __init__(
        self,
        target_folder: str,
        makefiles: typing.List[Makefile],
        environment: typing.Union[Environment, None] = None,
    ) -> None:
        super().__init__(environment)
        self.target_folder = target_folder
        self.makefiles = makefiles

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        mxmake_templates = []
        for makefile in self.makefiles:
            if makefile.fqn == "core.test":
                mxmake_templates.append("run-tests")
            if makefile.fqn == "core.coverage":
                mxmake_templates.append("run-coverage")
        return dict(mxmake_templates=mxmake_templates)


##############################################################################
# topics.rst template
##############################################################################


@template("topics.rst")
class Topics(Template):
    description: str = "Topics documentation for sphinx"
    target_name = None
    template_name = "topics.rst"
    target_folder = None

    def __init__(
        self,
        makefiles: typing.List[Makefile],
        environment: typing.Union[Environment, None] = None,
    ) -> None:
        super().__init__(environment)
        self.makefiles = makefiles

    @property
    def template_variables(self) -> typing.Dict[str, typing.Any]:
        return dict()

    def render(self):
        if not self.environment:
            raise RuntimeError("Cannot write template without environment")
        template = self.environment.get_template(self.template_name)
        return template.render(**self.template_variables)

    def write(self) -> None:
        raise NotImplementedError(
            "Topics template is not supposed to be written to file system"
        )
