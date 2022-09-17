import pytest


VALID_RELEASE_TEXT = """
---
release type: patch
---

This is a new release.
"""

MISSING_RELEASE_NOTES_TEXT = """
---
release type: patch
---
"""

DEPRECATED_RELEASE_TEXT = """
Release type: patch

This is a new release.
"""


@pytest.fixture
def valid_release_text() -> str:
    return VALID_RELEASE_TEXT.strip()


@pytest.fixture
def missing_release_notes_text() -> str:
    return MISSING_RELEASE_NOTES_TEXT.strip()


@pytest.fixture
def deprecated_release_text() -> str:
    return DEPRECATED_RELEASE_TEXT.strip()
