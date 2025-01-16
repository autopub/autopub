import json
import os
import pathlib
import textwrap
from functools import cached_property
from typing import Optional, TypedDict

from github import Github
from github.PullRequest import PullRequest
from github.Repository import Repository
from pydantic import BaseModel

from autopub.exceptions import AutopubException
from autopub.plugins import AutopubPlugin
from autopub.types import ReleaseInfo


class PRContributors(TypedDict):
    pr_author: str
    additional_contributors: set[str]
    reviewers: set[str]


class Sponsors(TypedDict):
    sponsors: set[str]
    private_sponsors: int


class GithubConfig(BaseModel):
    comment_template_success: str = textwrap.dedent(
        """
        Thanks for adding the `RELEASE.md` file!

        Here's a preview of the changelog:

        {changelog}
        """,
    )

    comment_template_error: str = textwrap.dedent(
        """
        Something went wrong while checking the release file.

        Here's the error:

        {error}
        """,
    )

    comment_template_missing_release: str = textwrap.dedent("""
        Hi, thanks for contributing to this project!

        We noticed that this PR is missing a `RELEASE.md` file. We use that to automatically do releases here on GitHub and, most importantly, to PyPI!

        So as soon as this PR is merged, a release will be made 🚀.

        Here's an example of `RELEASE.md`:

        ```markdown
        ---
        release type: patch
        ---

        Description of the changes, ideally with some examples, if adding a new feature.

        Release type can be one of patch, minor or major. We use [semver](https://semver.org/), so make sure to pick the appropriate type. If in doubt feel free to ask :)
        ```
        """)

    include_sponsors: bool = True
    create_discussions: bool = True
    discussion_category: str = "Announcements"


class GithubPlugin(AutopubPlugin):
    id = "github"
    Config = GithubConfig

    def __init__(self) -> None:
        super().__init__()

        self.github_token = os.environ.get("GITHUB_TOKEN")

        if not self.github_token:
            raise AutopubException("GITHUB_TOKEN environment variable is required")

        self.repository_name = os.environ.get("GITHUB_REPOSITORY")

    @cached_property
    def _github(self) -> Github:
        return Github(self.github_token)

    @cached_property
    def _event_data(self) -> Optional[dict]:
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        if not event_path:
            return None

        with open(event_path) as f:
            return json.load(f)

    @cached_property
    def repository(self) -> Repository:
        return self._github.get_repo(self.repository_name)

    @cached_property
    def pull_request(self) -> Optional[PullRequest]:
        pr_number = self._get_pr_number()

        if pr_number is None:
            return None

        return self.repository.get_pull(pr_number)

    def _get_pr_number(self) -> Optional[int]:
        if not self._event_data:
            return None

        if self._event_data.get("event_name") in [
            "pull_request",
            "pull_request_target",
        ]:
            return self._event_data["pull_request"]["number"]

        if self._event_data.get("pull_request"):
            return self._event_data["pull_request"]["number"]

        sha = self._event_data["commits"][0]["id"]

        commit = self.repository.get_commit(sha)

        pulls = commit.get_pulls()

        try:
            first_pr = pulls[0]
        except IndexError:
            return None

        return first_pr.number

    def _update_or_create_comment(
        self, text: str, marker: str = "<!-- autopub-comment -->"
    ) -> None:
        """Update or create a comment on the current PR with the given text."""
        print(
            f"Updating or creating comment on PR {self.pull_request} in {self.repository}"
        )

        # Look for existing autopub comment
        comment_body = f"{marker}\n{text}"

        # Search for existing comment
        for comment in self.pull_request.get_issue_comments():
            if marker in comment.body:
                # Update existing comment
                comment.edit(comment_body)
                return

        # Create new comment if none exists
        self.pull_request.create_issue_comment(comment_body)

    def _get_sponsors(self) -> Sponsors:
        query_organisation = """
            query GetSponsors($organization: String!) {
                organization(login: $organization) {
                    sponsorshipsAsMaintainer(
                        first: 100
                        includePrivate: true
                        activeOnly: true
                    ) {
                        nodes {
                            privacyLevel
                            sponsorEntity {
                                __typename
                                ... on User {
                                login
                            }
                            ... on Organization {
                                login
                                }
                            }
                        }
                    }
                }
            }
        """

        query_user = """
            query GetSponsors($user: String!) {
                user(login: $user) {
                    sponsorshipsAsMaintainer(
                        first: 100
                        includePrivate: true
                        activeOnly: true
                    ) {
                        nodes {
                            privacyLevel
                            sponsorEntity {
                                __typename
                                ... on User {
                                login
                            }
                            ... on Organization {
                                login
                                }
                            }
                        }
                    }
                }
            }
        """

        # TODO: there might be some permission issues in some cases
        # TODO: this needs a PAT (check security implications)
        if self.repository.organization:
            _, response = self._github.requester.graphql_query(
                query_organisation, {"organization": self.repository.organization.login}
            )

            data = response["data"]["organization"]["sponsorshipsAsMaintainer"]["nodes"]
        else:
            _, response = self._github.requester.graphql_query(
                query_user, {"user": self.repository.owner.login}
            )

            data = response["data"]["user"]["sponsorshipsAsMaintainer"]["nodes"]

        sponsors = set()
        private_sponsors = 0

        for node in data:
            if node["privacyLevel"] == "PUBLIC":
                sponsors.add(node["sponsorEntity"]["login"])
            else:
                private_sponsors += 1

        return Sponsors(
            sponsors=sponsors,
            private_sponsors=private_sponsors,
        )

    def _get_discussion_category_id(self) -> str:
        query = """
            query GetDiscussionCategoryId($owner: String!, $repositoryName: String!) {
                repository(owner: $owner, name: $repositoryName) {
                    discussionCategories(first:100) {
                        nodes {
                            name
                            id
                        }
                    }
                }
            }
        """

        _, response = self._github.requester.graphql_query(
            query,
            {
                "owner": self.repository.owner.login,
                "repositoryName": self.repository.name,
            },
        )

        for node in response["data"]["repository"]["discussionCategories"]["nodes"]:
            if node["name"] == self.config.discussion_category:
                return node["id"]

        raise AutopubException(
            f"Discussion category {self.config.discussion_category} not found"
        )

    def _create_discussion(self, release_info: ReleaseInfo) -> str:
        mutation = """
        mutation CreateDiscussion($repositoryId: ID!, $categoryId: ID!, $body: String!, $title: String!) {
            createDiscussion(input: {repositoryId: $repositoryId, categoryId: $categoryId, body: $body, title: $title}) {
                discussion {
                    id
                    url
                }
            }
        }
        """

        _, response = self._github.requester.graphql_query(
            mutation,
            {
                # TODO: repo.node_id is not yet been published to pypi
                "repositoryId": self.repository.raw_data["node_id"],
                "categoryId": self._get_discussion_category_id(),
                "body": self._get_release_message(release_info),
                "title": f"Release {release_info.version}",
            },
        )

        return response["data"]["createDiscussion"]["discussion"]["url"]

    def _get_pr_contributors(self) -> PRContributors:
        pr: PullRequest = self.pull_request

        pr_author = pr.user.login
        pr_contributors = PRContributors(
            pr_author=pr_author,
            additional_contributors=set(),
            reviewers=set(),
        )

        for commit in pr.get_commits():
            if commit.author.login != pr_author:
                pr_contributors["additional_contributors"].add(commit.author.login)

            for commit_message in commit.commit.message.split("\n"):
                if commit_message.startswith("Co-authored-by:"):
                    author = commit_message.split(":")[1].strip()
                    author_login = author.split(" ")[0]

                    if author_login != pr_author:
                        pr_contributors["additional_contributors"].add(author_login)

        for review in pr.get_reviews():
            if review.user.login != pr_author:
                pr_contributors["reviewers"].add(review.user.login)

        return pr_contributors

    def on_release_notes_valid(self, release_info: ReleaseInfo) -> None:
        assert self.pull_request is not None

        changelog = self._get_release_message(release_info)

        message = self.config.comment_template_success.format(
            changelog=changelog
        )

        self._update_or_create_comment(message)

    def on_release_file_not_found(self) -> None:
        message = self.config.comment_template_missing_release

        self._update_or_create_comment(message)

    def on_release_notes_invalid(self, exception: AutopubException) -> None:
        message = self.config.comment_template_error.format(error=str(exception))

        self._update_or_create_comment(message)

    def _get_release_message(
        self,
        release_info: ReleaseInfo,
        include_release_info: bool = False,
        discussion_url: Optional[str] = None,
    ) -> str:
        assert self.pull_request is not None

        contributors = self._get_pr_contributors()
        message = textwrap.dedent(
            f"""
            ## {release_info.version}

            {release_info.release_notes}
            """
        )

        if not include_release_info:
            return message

        message += f"This release was contributed by @{contributors['pr_author']} in #{self.pull_request.number}"

        if contributors["additional_contributors"]:
            additional_contributors = [
                f"@{contributor}"
                for contributor in contributors["additional_contributors"]
            ]
            message += (
                f"\n\nAdditional contributors: {', '.join(additional_contributors)}"
            )

        if contributors["reviewers"]:
            reviewers = [f"@{reviewer}" for reviewer in contributors["reviewers"]]
            message += f"\n\nReviewers: {', '.join(reviewers)}"

        if self.config.include_sponsors:
            sponsors = self._get_sponsors()
            if sponsors["sponsors"]:
                public_sponsors = [f"@{sponsor}" for sponsor in sponsors["sponsors"]]
                message += f"\n\nThanks to {', '.join(public_sponsors)}"

                if sponsors["private_sponsors"]:
                    message += (
                        f" and the {sponsors['private_sponsors']} private sponsor(s)"
                    )

                message += " for making this release possible ✨"

        if discussion_url:
            message += f"\n\nJoin the discussion: {discussion_url}"

        return message

    def _create_release(
        self, release_info: ReleaseInfo, discussion_url: Optional[str] = None
    ) -> None:
        message = self._get_release_message(release_info, discussion_url=discussion_url)

        release = self.repository.create_git_release(
            tag=release_info.version,
            name=release_info.version,
            message=message,
        )

        for asset in pathlib.Path("dist").glob("*"):
            if asset.suffix in [".tar.gz", ".whl"]:
                release.upload_asset(str(asset))

    def post_publish(self, release_info: ReleaseInfo) -> None:
        text = f"This PR was published as {release_info.version}"
        assert self.pull_request is not None

        self._update_or_create_comment(
            text, marker="<!-- autopub-comment-published -->"
        )

        discussion_url = None

        if self.config.create_discussions:
            discussion_url = self._create_discussion(release_info)

        self._create_release(release_info, discussion_url)
