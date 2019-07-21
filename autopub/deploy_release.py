import os
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from build_release import build_release
from create_github_release import create_github_release
from commit_release import git_commit_and_push
from prepare_release import prepare_release
from publish_release import publish_release


def deploy_release():
    prepare_release()
    build_release()
    git_commit_and_push()
    create_github_release()
    publish_release()
