import os
import sys
import time

sys.path.append(os.path.dirname(__file__))  # noqa

from base import (
    run_process,
    check_exit_code,
    get_project_version,
    configure_git,
    PROJECT_NAME,
    REPO_SLUG,
    TAG_PREFIX,
    get_release_info,
)


def create_github_release():
    try:
        from github_release import gh_release_create, gh_asset_upload
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
    )

    # give some time to the API to get updated
    # not sure if this is the proper way to fix the issue
    # ideally the githubrelease package shouldn't need
    # to do another API call to get the release since it
    # should be returned by the create API.
    # anyway, this fix might be good enough for the time being

    time.sleep(2)

    gh_asset_upload(
        REPO_SLUG,
        tag,
        pattern="dist/*",
    )
