import os
import re
import subprocess
import sys
from pathlib import Path

from tomlkit import parse


def dict_get(_dict, keys, default=None):
    """Query nested dictionary with list of keys, returning None if not found."""
    for key in keys:
        if isinstance(_dict, dict):
            _dict = _dict.get(key, default)
        else:
            return default
    return _dict


# Determine CI/CD environment

if os.environ.get("CIRCLECI"):
    CI_SYSTEM = "circleci"
    CIRCLE_PROJECT_USERNAME = os.environ.get("CIRCLE_PROJECT_USERNAME")
    CIRCLE_PROJECT_REPONAME = os.environ.get("CIRCLE_PROJECT_REPONAME")
    REPO_SLUG = f"{CIRCLE_PROJECT_USERNAME}/{CIRCLE_PROJECT_REPONAME}"
elif os.environ.get("GITHUB_ACTIONS") == "true":
    CI_SYSTEM = "github"
    REPO_SLUG = os.environ.get("GITHUB_REPOSITORY")
elif os.environ.get("TRAVIS"):
    CI_SYSTEM = "travis"
    REPO_SLUG = os.environ.get("TRAVIS_REPO_SLUG")
else:
    CI_SYSTEM = os.environ.get("CI_SYSTEM", None)
    REPO_SLUG = os.environ.get("REPO_SLUG", None)

# Project root and file name configuration

PROJECT_ROOT = os.environ.get("PROJECT_ROOT")
PYPROJECT_FILE_NAME = os.environ.get("PYPROJECT_FILE_NAME", "pyproject.toml")

if PROJECT_ROOT:
    ROOT = Path(PROJECT_ROOT)
else:
    ROOT = Path(
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
        .decode("ascii")
        .strip()
    )

PYPROJECT_FILE = ROOT / PYPROJECT_FILE_NAME

# Retrieve configuration from pyproject file

if os.path.exists(PYPROJECT_FILE):
    config = parse(open(PYPROJECT_FILE).read())
else:
    print(f"Could not find pyproject file at: {PYPROJECT_FILE}")
    sys.exit(1)

PROJECT_NAME = dict_get(config, ["tool", "autopub", "project-name"])
if not PROJECT_NAME:
    PROJECT_NAME = dict_get(config, ["tool", "poetry", "name"])
if not PROJECT_NAME:
    PROJECT_NAME = dict_get(config, ["project", "name"])
if not PROJECT_NAME:
    print(
        "Could not determine project name. Under the pyproject file's "
        '[tool.autopub] header, add:\nproject-name = "YourProjectName"'
    )
    sys.exit(1)

RELEASE_FILE_NAME = dict_get(
    config, ["tool", "autopub", "release-file"], default="RELEASE.md"
)
RELEASE_FILE = ROOT / RELEASE_FILE_NAME

CHANGELOG_FILE_NAME = dict_get(
    config, ["tool", "autopub", "changelog-file"], default="CHANGELOG.md"
)
CHANGELOG_FILE = ROOT / CHANGELOG_FILE_NAME

CHANGELOG_HEADER = dict_get(
    config, ["tool", "autopub", "changelog-header"], default="========="
)

VERSION_HEADER = dict_get(config, ["tool", "autopub", "version-header"], default="-")
VERSION_STRINGS = dict_get(config, ["tool", "autopub", "version-strings"], default=[])

TAG_PREFIX = dict_get(config, ["tool", "autopub", "tag-prefix"], default="")

PYPI_URL = dict_get(config, ["tool", "autopub", "pypi-url"])

# Git configuration

GIT_USERNAME = dict_get(config, ["tool", "autopub", "git-username"])
GIT_EMAIL = dict_get(config, ["tool", "autopub", "git-email"])

# GitHub

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", None)
APPEND_GITHUB_CONTRIBUTOR = dict_get(
    config, ["tool", "autopub", "append-github-contributor"], False
)


def run_process(popenargs, encoding="utf-8", env=None):
    if env is not None:
        env = {**os.environ, **env}
    try:
        return subprocess.check_output(popenargs, encoding=encoding, env=env).strip()
    except subprocess.CalledProcessError as e:
        print(e.output, file=sys.stderr)
        sys.exit(1)


def git(popenargs):
    # Do not decode ASCII for commit messages so emoji are preserved
    return subprocess.check_output(["git", *popenargs])


def check_exit_code(popenargs):
    return subprocess.call(popenargs, shell=True)


def get_project_version():
    # Backwards compat: Try poetry first and then fall "back" to standards
    version = dict_get(config, ["tool", "poetry", "version"])
    if version is None:
        return dict_get(config, ["project", "version"])
    else:
        return version


def get_release_info():
    RELEASE_TYPE_REGEX = re.compile(r"^[Rr]elease [Tt]ype: (major|minor|patch)$")

    with open(RELEASE_FILE, "r") as f:
        line = f.readline()
        match = RELEASE_TYPE_REGEX.match(line)

        if not match:
            print(
                "The RELEASE file should start with 'Release type' and "
                "specify one of the following values: major, minor, or patch."
            )
            sys.exit(1)

        type_ = match.group(1)
        changelog = "".join([l for l in f.readlines()]).strip()

    return type_, changelog


def configure_git():
    if not GIT_USERNAME or not GIT_EMAIL:
        print("git-username and git-email must be defined in the pyproject file")
        sys.exit(1)
    git(["config", "user.name", GIT_USERNAME])
    git(["config", "user.email", GIT_EMAIL])
