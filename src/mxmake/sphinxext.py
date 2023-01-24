from docutils import nodes
from docutils.statemachine import ViewList
from mxmake.templates import get_template_environment
from mxmake.templates import template
from sphinx import addnodes
from sphinx.util.docstrings import prepare_docstring
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import nested_parse_with_titles

class DomainsDirective(SphinxDirective):

    def _rest2node(self, rest, container=None):
        vl = ViewList(prepare_docstring(rest))
        if container is None:
            node = nodes.container()
        else:
            node = container()
        nested_parse_with_titles(self.state, vl, node)
        return node

    def run(self):
        factory = template.lookup("domains.rst")
        domains_template = factory([], get_template_environment())
        node = self._rest2node(domains_template.render())
        breakpoint()
        return [node]


def setup(app):
    app.add_directive("mxmakedomains", DomainsDirective)
