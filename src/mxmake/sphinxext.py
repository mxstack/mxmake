from docutils import nodes
from mxmake.templates import get_template_environment
from mxmake.templates import template
from myst_parser.mdit_to_docutils.sphinx_ import SphinxRenderer
from myst_parser.parsers.mdit import create_md_parser
from sphinx.util.docutils import SphinxDirective


class BaseDirective(SphinxDirective):
    TEMPLATE = ""

    def run(self):
        # call uses the Topics class in templates.py to render the template
        factory = template.lookup(self.TEMPLATE)
        tpl = factory(get_template_environment())

        # create a new parser with the sphinx myst renderer
        config = self.state.document.settings.env.myst_config
        parser = create_md_parser(config, SphinxRenderer)

        # create a new helper document to parse the template into
        doc = nodes.document(self.state.document.settings, self.state.document.reporter)
        doc["source"] = ""
        parser.options["document"] = doc

        # parse the template into the new document
        parser.render(tpl.render())

        # return the parsed nodes, but not the helper document
        return doc.children


class TopicsDirective(BaseDirective):
    TEMPLATE = "topics.md"


class DependenciesDirective(BaseDirective):
    TEMPLATE = "dependencies.md"


def setup(app):
    app.add_directive("mxmaketopics", TopicsDirective)
    app.add_directive("mxmakedependencies", DependenciesDirective)
