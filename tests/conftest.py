import textwrap

import pytest


@pytest.fixture
def valid_release_text()-> str:
    return textwrap.dedent("""
    Release type: patch

    This is a new release.
    """).strip()