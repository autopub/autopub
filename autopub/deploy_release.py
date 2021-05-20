import os
import sys

from build_release import build_release
from commit_release import git_commit_and_push
from create_github_release import create_github_release
from prepare_release import prepare_release
from publish_release import publish_release


sys.path.append(os.path.dirname(__file__))  # noqa


def deploy_release():
    prepare_release()
    build_release()
    git_commit_and_push()
    create_github_release()
    publish_release()
