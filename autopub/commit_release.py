import os
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from base import (
    get_project_version,
    git,
    configure_git,
    PROJECT_NAME,
    PYPROJECT_FILE_NAME,
    CHANGELOG_FILE_NAME,
    RELEASE_FILE_NAME,
    VERSION_STRINGS,
)


def git_commit_and_push():
    configure_git()

    version = get_project_version()

    git(["add", PYPROJECT_FILE_NAME])
    git(["add", CHANGELOG_FILE_NAME])

    if VERSION_STRINGS:
        for version_file in VERSION_STRINGS:
            git(["add", version_file])

    git(["rm", "--cached", RELEASE_FILE_NAME])

    git(["commit", "-m", f"Release {PROJECT_NAME} {version}"])
    git(["push", "origin", "HEAD"])
