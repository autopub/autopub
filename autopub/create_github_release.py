import os
import sys

from base import (
    PROJECT_NAME,
    REPO_SLUG,
    TAG_PREFIX,
    check_exit_code,
    configure_git,
    get_project_version,
    get_release_info,
    run_process,
)


sys.path.append(os.path.dirname(__file__))  # noqa


def create_github_release():
    try:
        from github_release import gh_release_create
    except ModuleNotFoundError:
        print("Cannot create GitHub release due to missing dependency: github_release")
        sys.exit(1)

    configure_git()
    version = get_project_version()
    tag = f"{TAG_PREFIX}{version}"

    if not version:
        print("Unable to determine the current version")
        sys.exit(1)

    tag_exists = (
        check_exit_code([f'git show-ref --tags --quiet --verify -- "refs/tags/{tag}"'])
        == 0
    )

    if not tag_exists:
        run_process(["git", "tag", tag])
        run_process(["git", "push", "--tags"])

    _, changelog = get_release_info()

    gh_release_create(
        REPO_SLUG,
        tag,
        publish=True,
        name=f"{PROJECT_NAME} {version}",
        body=changelog,
        asset_pattern="dist/*",
    )
