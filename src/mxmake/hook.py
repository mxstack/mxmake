from mxmake.templates import get_template_environment
from mxmake.templates import template
from mxmake.utils import list_value
from mxmake.utils import NAMESPACE
from mxmake.utils import ns_name
from pathlib import Path

import logging
import mxdev


logger = logging.getLogger("mxmake")


ADDITIONAL_SOURCES_TARGETS = [
    "constraints.txt",
    "pyproject.toml",
    "requirements.txt",
    "setup.cfg",
    "setup.py",
]


class Hook(mxdev.Hook):
    namespace: str = NAMESPACE

    def __init__(self) -> None:
        logger.info("mxmake: hook initialized")

    def generate_templates(self, state: mxdev.State):
        config = state.configuration
        templates = list_value(config.settings.get(ns_name("templates")))
        if not templates:
            logger.info("mxmake: No templates defined")
            return
        environment = get_template_environment()
        for name in templates:
            try:
                factory = template.lookup(name, bound=True)
            except RuntimeError as e:
                msg = f"mxmake: {str(e)}"
                logger.warning(msg)
                continue
            factory(config, environment).write()

    def generate_additional_sources_targets(self, state: mxdev.State):
        config = state.configuration
        additional_sources_targets = []
        sources_folder = Path(config.settings.get("default-target", "sources"))
        for package_name in config.packages:
            source_folder = sources_folder / package_name
            # case new source package has been added to mx.ini
            if not source_folder.exists():
                continue
            for child in source_folder.iterdir():
                if child in ADDITIONAL_SOURCES_TARGETS:
                    additional_sources_targets.append(source_folder / child)
        if not additional_sources_targets:
            return
        environment = get_template_environment()
        factory = template.lookup("additional_sources_targets")
        factory(additional_sources_targets, environment).write()

    def write(self, state: mxdev.State) -> None:
        self.generate_templates(state)
        self.generate_additional_sources_targets(state)
