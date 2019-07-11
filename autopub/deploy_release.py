import os
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from base import run_process
from create_github_release import create_github_release
from prepare_release import prepare_release
from commit_release import git_commit_and_push


def deploy_release():
    prepare_release()
    run_process(["poetry", "build"])
    create_github_release()
    git_commit_and_push()
    run_process(
        ["poetry", "publish", "-u", "$PYPI_USERNAME", "-p", "$PYPI_PASSWORD"]
    )
