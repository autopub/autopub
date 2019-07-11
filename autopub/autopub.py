import argparse
import os
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from check_release import check_release
from prepare_release import prepare_release
from commit_release import git_commit_and_push
from create_github_release import create_github_release
from deploy_release import deploy_release


def check(arguments):
    check_release()


def prepare(arguments):
    prepare_release()


def commit(arguments):
    git_commit_and_push()


def githubrelease(arguments):
    create_github_release()


def deploy(arguments):
    deploy_release()


def parse_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    check_parser = subparsers.add_parser("check")
    check_parser.set_defaults(func=check)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.set_defaults(func=prepare)

    commit_parser = subparsers.add_parser("commit")
    commit_parser.set_defaults(func=commit)

    githubrelease_parser = subparsers.add_parser("githubrelease")
    githubrelease_parser.set_defaults(func=githubrelease)

    deploy_parser = subparsers.add_parser("deploy")
    deploy_parser.set_defaults(func=deploy)

    arguments = parser.parse_args()

    return arguments


def main():
    arguments = parse_arguments()
    arguments.func(arguments)
