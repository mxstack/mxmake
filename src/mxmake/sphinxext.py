from docutils import nodes
from docutils.statemachine import ViewList
from mxmake.templates import get_template_environment
from mxmake.templates import template
from sphinx.util.docstrings import prepare_docstring
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import nested_parse_with_titles


class TopicsDirective(SphinxDirective):
    def _rest2node(self, rest, container=None):
        vl = ViewList(prepare_docstring(rest))
        if container is None:
            node = nodes.compound()
        else:
            node = container()
        nested_parse_with_titles(self.state, vl, node)
        return node

    def run(self):
        # call uses the Topics class in templates.py to render the template
        factory = template.lookup("topics.rst")
        tpl = factory(get_template_environment())
        node = self._rest2node(tpl.render())
        return node.children


def setup(app):
    app.add_directive("mxmaketopics", TopicsDirective)
