import argparse
import os
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from build_release import build_release
from check_release import check_release
from commit_release import git_commit_and_push
from create_github_release import create_github_release
from deploy_release import deploy_release
from prepare_release import prepare_release
from publish_release import publish_release


def check(arguments):
    check_release()


def prepare(arguments):
    prepare_release()


def build(arguments):
    build_release()


def commit(arguments):
    git_commit_and_push()


def githubrelease(arguments):
    create_github_release()


def publish(arguments):
    publish_release()


def deploy(arguments):
    deploy_release()


def parse_arguments():
    try:
        version = __import__("pkg_resources").get_distribution("autopub").version
    except Exception:
        version = "unknown"

    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=version)

    subparsers = parser.add_subparsers()

    check_parser = subparsers.add_parser("check")
    check_parser.set_defaults(func=check)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.set_defaults(func=prepare)

    build_parser = subparsers.add_parser("build")
    build_parser.set_defaults(func=build)

    commit_parser = subparsers.add_parser("commit")
    commit_parser.set_defaults(func=commit)

    githubrelease_parser = subparsers.add_parser("githubrelease")
    githubrelease_parser.set_defaults(func=githubrelease)

    publish_parser = subparsers.add_parser("publish")
    publish_parser.set_defaults(func=publish)

    deploy_parser = subparsers.add_parser("deploy")
    deploy_parser.set_defaults(func=deploy)

    arguments = parser.parse_args()

    return arguments


def main():
    arguments = parse_arguments()
    arguments.func(arguments)
