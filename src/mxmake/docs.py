from mxmake.templates import get_template_environment
from mxmake.templates import template
from sphinx import addnodes
from sphinx.util.docstrings import prepare_docstring
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import nested_parse_with_titles


class DomainsDirective(SphinxDirective):
    def run(self):
        factory = template.lookup("domains.rst")
        domains_template = factory([], get_template_environment())
        # XXX: this not works yet
        #     - figure out how to correctly parse and hook document to sphinx
        #       including toctree
        #     - figure out how to force generation each time sphinx-build runs
        node = addnodes.desc()
        node.document = self.state.document
        contentnode = addnodes.desc_content(
            prepare_docstring(domains_template.render())
        )
        node.append(contentnode)
        nested_parse_with_titles(self.state, contentnode, node)
        return [node]


def setup(app):
    app.add_directive("mxmakedomains", DomainsDirective)
