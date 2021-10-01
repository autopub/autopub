from dataclasses import dataclass
import os
import subprocess
import sys
from typing import Optional

sys.path.append(os.path.dirname(__file__))  # noqa

from base import GITHUB_TOKEN, REPO_SLUG, APPEND_GITHUB_CONTRIBUTOR


@dataclass
class GitHubContributor:
    pr_number: str
    author_username: str
    author_fullname: str

    @property
    def name(self) -> str:
        return self.author_fullname or self.author_username


def get_github_contributor() -> Optional[GitHubContributor]:
    if not APPEND_GITHUB_CONTRIBUTOR:
        return None

    try:
        import httpx
    except ModuleNotFoundError:
        return None

    org, repo = REPO_SLUG.split("/")
    current_commit = (
        subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
    )

    response = httpx.post(
        "https://api.github.com/graphql",
        json={
            "query": """query Contributor(
                $owner: String!
                $name: String!
                $commit: GitObjectID!
            ) {
                repository(owner: $owner, name: $name) {
                    object(oid: $commit) {
                        __typename
                        ... on Commit {
                            associatedPullRequests(first: 1) {
                                nodes {
                                    number
                                    author {
                                        __typename
                                        login
                                        ... on User {
                                            name
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }""",
            "variables": {"owner": org, "name": repo, "commit": current_commit},
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
        },
    )

    payload = response.json()
    commit = payload["data"]["repository"]["object"]

    if not commit:
        return

    prs = commit["associatedPullRequests"]["nodes"]

    if not prs:
        return

    pr = prs[0]

    pr_number = pr["number"]
    pr_author_username = pr["author"]["login"]
    pr_author_fullname = pr["author"].get("name", "")

    return GitHubContributor(
        pr_number=pr_number,
        pr_author_username=pr_author_username,
        pr_author_fullname=pr_author_fullname,
    )


def append_github_contributor(file):
    if not APPEND_GITHUB_CONTRIBUTOR:
        return

    try:
        import httpx
    except ModuleNotFoundError:
        print("Cannot append the GitHub contributor due to missing dependency: httpx")
        sys.exit(1)

    github_contributor = get_github_contributor()

    if not github_contributor:
        return

    name = github_contributor.name
    username = github_contributor.author_username
    pr_number = github_contributor.pr_number

    file.write("\n")
    file.write("\n")
    file.write(
        f"Contributed by [{name}](https://github.com/{username}) via [PR #{pr_number}](https://github.com/{REPO_SLUG}/pull/{pr_number}/)"
    )
    file.write("\n")
