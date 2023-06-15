import datetime

# Configuration file for the Sphinx documentation builder.
#
# Full list of options can be found in the Sphinx documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- Project Information -----------------------------------------------------

project = "AutoPub"
year = datetime.datetime.now().date().year
copyright = f"2019–{year}"
author = "Justin Mayer"


# -- General Configuration ---------------------------------------------------

extensions = [
    "myst_parser",
]

templates_path = ["_templates"]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML Output -------------------------------------------------

html_theme = "furo"
html_title = project

html_static_path = ["_static"]
