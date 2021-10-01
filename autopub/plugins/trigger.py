import os
import sys
from typing import Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # noqa

from dataclasses import dataclass

from base import get_project_version, get_release_info
from github_contributor import get_github_contributor
from .hookspec import plugin_manager


@dataclass
class AfterReleaseEvent:
    version: str
    bump_type: str
    changelog: str
    contributor_name: Optional[str]
    pr_number: Optional[str]


def trigger_after_release():
    bump_type, changelog = get_release_info()
    github_contributor = get_github_contributor()

    if github_contributor:
        contributor_name = github_contributor.name
        github_pr_number = github_contributor.pr_number
    else:
        contributor_name = None
        github_pr_number = None

    plugin_manager.hook.after_release(
        payload=AfterReleaseEvent(
            version=get_project_version(),
            bump_type=bump_type,
            changelog=changelog,
            contributor_name=contributor_name,
            pr_number=github_pr_number,
        )
    )
