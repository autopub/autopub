import os

from invoke import task

DOCS_PORT = os.environ.get("DOCS_PORT", 8000)


@task
def docbuild(c):
    """Build documentation"""
    c.run("sphinx-build -W docs docs/_build")


@task(docbuild)
def docserve(c):
    """Serve docs at http://localhost:$DOCS_PORT/ (default port is 8000)"""
    from livereload import Server

    server = Server()
    server.watch("docs/conf.py", lambda: docbuild(c))
    server.watch("docs/**/*.md", lambda: docbuild(c))
    server.serve(port=DOCS_PORT, root="docs/_build")
