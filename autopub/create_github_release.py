import os
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from github_release import gh_release_create

from base import (
    run_process,
    check_exit_code,
    get_project_version,
    configure_git,
    PROJECT_NAME,
    REPO_SLUG,
    get_release_info,
)


def create_github_release():
    configure_git()
    version = get_project_version()

    if not version:
        print("Unable to determine the current version")
        sys.exit(1)

    tag_exists = (
        check_exit_code(
            [f'git show-ref --tags --quiet --verify -- "refs/tags/{version}"']
        )
        == 0
    )

    if not tag_exists:
        run_process(["git", "tag", version])
        run_process(["git", "push", "--tags"])

    _, changelog = get_release_info()

    gh_release_create(
        REPO_SLUG,
        version,
        publish=True,
        name=f"{PROJECT_NAME} {version}",
        body=changelog,
        asset_pattern="dist/*",
    )
