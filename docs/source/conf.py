# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = "mxmake"
copyright = "2022, mxstack Contributors"
author = "mxstack Contributors"

# The full version, including alpha/beta/rc tags
release = "1.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["mxmake.sphinxext", "myst_parser"]

# MySt specific extensions
myst_enable_extensions = [
    "deflist",  # You will be able to utilise definition lists
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "conestack"

html_theme_options = {
    "cs_color": "#FFFFFF",
    "cs_bg_color": "var(--bs-gray-900)",
    "logo_title": "mxmake",
    "github_url": "https://github.com/mxstack/mxmake",
    "pypi_url": "https://pypi.org/project/mxmake",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# theme specific options
html_theme_options = {
    'github_url': 'https://github.com/mxstack/mxmake',
    'pypi_url': 'https://pypi.org/project/mxmake',
    'logo_url': "_static/mxmake-logo.svg",
    'logo_title': "mxmake",
    'logo_width': "40px",
    'logo_height': "40px",
    "cs_bg_color": "#0A0A0A",
}