from unittest.mock import MagicMock, patch

import pytest
from github import GithubException

from autopub.exceptions import AutopubException, AutopubWarning
from autopub.plugins.github import GithubPlugin
from autopub.types import ReleaseInfo


@pytest.fixture
def mock_env(monkeypatch):
    """Mock required environment variables."""
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")


@pytest.fixture
def github_plugin(mock_env):
    """Create a GithubPlugin instance with mocked dependencies."""
    with patch("autopub.plugins.github.Github"):
        plugin = GithubPlugin()
        # Initialize config with default values
        plugin.validate_config({})
        return plugin


def test_on_release_notes_valid_with_markdown_links(github_plugin):
    """Test that markdown links are added to CHANGELOG for contributors and PR."""
    # Mock pull request
    mock_pr = MagicMock()
    mock_pr.number = 123
    mock_pr.html_url = "https://github.com/owner/repo/pull/123"
    mock_pr.user.login = "contributor"
    mock_pr.get_commits.return_value = []
    mock_pr.get_issue_comments.return_value = []

    github_plugin.pull_request = mock_pr

    release_info = ReleaseInfo(
        release_type="minor",
        release_notes="Test release",
        version="1.0.0",
        previous_version="0.9.0",
    )

    github_plugin.on_release_notes_valid(release_info)

    # Verify markdown links were added to additional_release_notes
    assert len(release_info.additional_release_notes) == 1
    assert (
        "[@contributor](https://github.com/contributor)"
        in release_info.additional_release_notes[0]
    )
    assert (
        "[#123](https://github.com/owner/repo/pull/123)"
        in release_info.additional_release_notes[0]
    )


def test_on_release_notes_valid_with_additional_contributors(github_plugin):
    """Test that additional contributors are properly formatted with markdown links."""
    # Mock pull request with additional contributors
    mock_pr = MagicMock()
    mock_pr.number = 456
    mock_pr.html_url = "https://github.com/owner/repo/pull/456"
    mock_pr.user.login = "main-author"

    # Mock commit with different author
    mock_commit = MagicMock()
    mock_commit.author.login = "co-author"
    mock_commit.commit.message = "Some commit"
    mock_pr.get_commits.return_value = [mock_commit]
    mock_pr.get_issue_comments.return_value = []

    github_plugin.pull_request = mock_pr

    release_info = ReleaseInfo(
        release_type="patch",
        release_notes="Bug fix",
        version="1.0.1",
        previous_version="1.0.0",
    )

    github_plugin.on_release_notes_valid(release_info)

    # Verify both contributor line and additional contributors line
    assert len(release_info.additional_release_notes) == 2
    assert (
        "[@main-author](https://github.com/main-author)"
        in release_info.additional_release_notes[0]
    )
    assert "Additional contributors:" in release_info.additional_release_notes[1]
    assert (
        "[@co-author](https://github.com/co-author)"
        in release_info.additional_release_notes[1]
    )


def test_on_release_notes_valid_with_unlinked_commit_author(github_plugin):
    """Test that commits without linked GitHub authors do not crash."""
    mock_pr = MagicMock()
    mock_pr.number = 457
    mock_pr.html_url = "https://github.com/owner/repo/pull/457"
    mock_pr.user.login = "main-author"

    mock_commit = MagicMock()
    mock_commit.author = None
    mock_commit.commit.message = "Some commit"
    mock_pr.get_commits.return_value = [mock_commit]
    mock_pr.get_issue_comments.return_value = []

    github_plugin.pull_request = mock_pr

    release_info = ReleaseInfo(
        release_type="patch",
        release_notes="Bug fix",
        version="1.0.1",
        previous_version="1.0.0",
    )

    github_plugin.on_release_notes_valid(release_info)

    assert len(release_info.additional_release_notes) == 1
    assert (
        "[@main-author](https://github.com/main-author)"
        in release_info.additional_release_notes[0]
    )


def test_on_release_notes_valid_with_co_authored_by(github_plugin):
    """Test that Co-authored-by trailers are parsed correctly."""
    mock_pr = MagicMock()
    mock_pr.number = 789
    mock_pr.html_url = "https://github.com/owner/repo/pull/789"
    mock_pr.user.login = "author"

    # Mock commit with Co-authored-by trailer
    mock_commit = MagicMock()
    mock_commit.author.login = "author"
    mock_commit.commit.message = (
        "Fix bug\n\nCo-authored-by: Helpful Person <helper@example.com>"
    )
    mock_commit.raw_data = {"node_id": "commit-id"}
    mock_pr.get_commits.return_value = [mock_commit]
    mock_pr.get_issue_comments.return_value = []

    github_plugin.pull_request = mock_pr
    github_plugin.__dict__["_github"] = MagicMock()
    github_plugin._github.requester.graphql_query.return_value = (
        None,
        {
            "data": {
                "node": {
                    "authors": {
                        "nodes": [
                            {"user": {"login": "author"}},
                            {"user": {"login": "helper"}},
                        ]
                    }
                }
            }
        },
    )

    release_info = ReleaseInfo(
        release_type="patch",
        release_notes="Bug fix with co-author",
        version="1.0.2",
        previous_version="1.0.1",
    )

    github_plugin.on_release_notes_valid(release_info)

    # Verify co-author was picked up
    assert len(release_info.additional_release_notes) == 2
    assert (
        "[@helper](https://github.com/helper)"
        in release_info.additional_release_notes[1]
    )


def test_get_pr_contributors_does_not_treat_coauthor_name_as_login(github_plugin):
    mock_pr = MagicMock()
    mock_pr.user.login = "patrick91"

    mock_commit = MagicMock()
    mock_commit.author.login = "ampagent"
    mock_commit.commit.message = (
        "Fix bug\n\nCo-authored-by: Patrick Arminio <patrick.arminio@gmail.com>"
    )
    mock_commit.raw_data = {"node_id": "commit-id"}
    mock_pr.get_commits.return_value = [mock_commit]

    github_plugin.pull_request = mock_pr
    github_plugin.__dict__["_github"] = MagicMock()
    github_plugin._github.requester.graphql_query.return_value = (
        None,
        {
            "data": {
                "node": {
                    "authors": {
                        "nodes": [
                            {"user": {"login": "ampagent"}},
                            {"user": {"login": "patrick91"}},
                        ]
                    }
                }
            }
        },
    )

    contributors = github_plugin._get_pr_contributors()

    assert contributors == {
        "pr_author": "patrick91",
        "additional_contributors": {"ampagent"},
    }


def test_on_release_notes_valid_no_pr_context(github_plugin):
    """Test that no modifications are made when there's no PR context."""
    github_plugin.pull_request = None

    release_info = ReleaseInfo(
        release_type="minor",
        release_notes="Direct push release",
        version="2.0.0",
        previous_version="1.0.0",
    )

    github_plugin.on_release_notes_valid(release_info)

    # Verify no additional_release_notes were added
    assert len(release_info.additional_release_notes) == 0


def test_get_release_message_with_pr_context(github_plugin):
    """Test that _get_release_message includes contributor info with @ mentions (not markdown)."""
    mock_pr = MagicMock()
    mock_pr.number = 100
    mock_pr.html_url = "https://github.com/owner/repo/pull/100"
    mock_pr.user.login = "testuser"
    mock_pr.get_commits.return_value = []

    github_plugin.pull_request = mock_pr

    release_info = ReleaseInfo(
        release_type="major",
        release_notes="Major release",
        version="2.0.0",
        previous_version="1.0.0",
    )

    message = github_plugin._get_release_message(
        release_info, include_release_info=True
    )

    # For GitHub releases, use @ mentions, not markdown links
    assert "Major release" in message
    assert "@testuser" in message
    assert "https://github.com/owner/repo/pull/100" in message


def test_get_release_message_without_pr_context(github_plugin):
    """Test that _get_release_message returns just release notes when no PR context."""
    github_plugin.pull_request = None

    release_info = ReleaseInfo(
        release_type="minor",
        release_notes="No PR release",
        version="1.5.0",
        previous_version="1.4.0",
    )

    message = github_plugin._get_release_message(
        release_info, include_release_info=True
    )

    # Should return just the release notes
    assert message == "No PR release"


def test_get_release_message_without_include_release_info(github_plugin):
    """Test that _get_release_message returns just notes when include_release_info=False."""
    mock_pr = MagicMock()
    mock_pr.number = 200
    github_plugin.pull_request = mock_pr

    release_info = ReleaseInfo(
        release_type="patch",
        release_notes="Simple fix",
        version="1.0.1",
        previous_version="1.0.0",
    )

    message = github_plugin._get_release_message(
        release_info, include_release_info=False
    )

    # Should return just the release notes, no contributor info
    assert message == "Simple fix"
    assert "@" not in message


def test_update_or_create_comment_skips_without_pr(github_plugin):
    """Without a PR there's nothing to comment on, so it's a no-op."""
    github_plugin.pull_request = None

    # Should not raise.
    github_plugin._update_or_create_comment("hello")


def test_update_or_create_comment_creates_when_none_exists(github_plugin):
    """A new comment is created when no matching comment exists yet."""
    mock_pr = MagicMock()
    mock_pr.get_issue_comments.return_value = []
    github_plugin.pull_request = mock_pr

    github_plugin._update_or_create_comment("hello", marker="<!-- m -->")

    mock_pr.create_issue_comment.assert_called_once_with("<!-- m -->\nhello")


def test_update_or_create_comment_edits_existing(github_plugin):
    """An existing comment with the same marker is edited, not duplicated."""
    existing = MagicMock()
    existing.body = "<!-- m -->\nold"
    mock_pr = MagicMock()
    mock_pr.get_issue_comments.return_value = [existing]
    github_plugin.pull_request = mock_pr

    github_plugin._update_or_create_comment("new", marker="<!-- m -->")

    existing.edit.assert_called_once_with("<!-- m -->\nnew")
    mock_pr.create_issue_comment.assert_not_called()


@pytest.mark.parametrize(
    ("event_name", "expected_comment_count"),
    [
        ("push", 0),
        ("workflow_run", 0),
        ("pull_request", 3),
        ("pull_request_target", 3),
    ],
)
def test_release_validation_comments_follow_event_context(
    github_plugin, monkeypatch, event_name, expected_comment_count
):
    """Only pull request checks leave release validation feedback."""
    monkeypatch.setenv("GITHUB_EVENT_NAME", event_name)

    mock_pr = MagicMock()
    mock_pr.number = 123
    mock_pr.html_url = "https://github.com/owner/repo/pull/123"
    mock_pr.user.login = "contributor"
    mock_pr.get_commits.return_value = []
    github_plugin.pull_request = mock_pr
    github_plugin._update_or_create_comment = MagicMock()

    release_info = ReleaseInfo(
        release_type="patch",
        release_notes="Bug fix",
        version="1.0.1",
        previous_version="1.0.0",
    )

    github_plugin.on_release_notes_valid(release_info)
    github_plugin.on_release_file_not_found()
    github_plugin.on_release_notes_invalid(AutopubException("invalid release"))

    assert github_plugin._update_or_create_comment.call_count == expected_comment_count
    assert len(release_info.additional_release_notes) == 1


def test_update_or_create_comment_warns_on_api_error(github_plugin):
    """A GitHub API error (e.g. missing permissions) warns instead of raising."""
    mock_pr = MagicMock()
    mock_pr.number = 42
    mock_pr.get_issue_comments.return_value = []
    mock_pr.create_issue_comment.side_effect = GithubException(
        403, {"message": "Resource not accessible by integration"}, None
    )
    github_plugin.pull_request = mock_pr

    with pytest.warns(AutopubWarning, match="issues: write"):
        github_plugin._update_or_create_comment("hello")


def test_post_publish_creates_release_even_if_comment_fails(github_plugin, monkeypatch):
    """A failed publish comment must not stop the GitHub release from being created."""
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")

    mock_pr = MagicMock()
    mock_pr.number = 7
    mock_pr.get_issue_comments.return_value = []
    mock_pr.create_issue_comment.side_effect = GithubException(
        403, {"message": "Resource not accessible by integration"}, None
    )
    github_plugin.pull_request = mock_pr
    github_plugin.repository = MagicMock()
    github_plugin._create_release = MagicMock()

    release_info = ReleaseInfo(
        release_type="major",
        release_notes="Release",
        version="1.0.0",
        previous_version="0.1.0",
    )

    with pytest.warns(AutopubWarning, match="Could not post a comment"):
        github_plugin.post_publish(release_info)

    github_plugin._create_release.assert_called_once()


def _write_event(monkeypatch, tmp_path, payload):
    import json

    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps(payload))
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_path))


def test_get_pr_number_from_workflow_run_event(github_plugin, monkeypatch, tmp_path):
    """A workflow_run payload has no top-level commits/head_commit; the SHA
    comes from workflow_run.head_sha and must not raise KeyError."""
    _write_event(monkeypatch, tmp_path, {"workflow_run": {"head_sha": "abc123"}})

    mock_pr = MagicMock()
    mock_pr.number = 42
    mock_commit = MagicMock()
    mock_commit.get_pulls.return_value = [mock_pr]
    github_plugin.repository = MagicMock()
    github_plugin.repository.get_commit.return_value = mock_commit

    assert github_plugin._get_pr_number() == 42
    github_plugin.repository.get_commit.assert_called_once_with("abc123")


def test_get_pr_number_falls_back_to_github_sha(github_plugin, monkeypatch, tmp_path):
    """When the payload carries no commit info, fall back to $GITHUB_SHA."""
    _write_event(monkeypatch, tmp_path, {"action": "completed"})
    monkeypatch.setenv("GITHUB_SHA", "def456")

    mock_pr = MagicMock()
    mock_pr.number = 7
    mock_commit = MagicMock()
    mock_commit.get_pulls.return_value = [mock_pr]
    github_plugin.repository = MagicMock()
    github_plugin.repository.get_commit.return_value = mock_commit

    assert github_plugin._get_pr_number() == 7
    github_plugin.repository.get_commit.assert_called_once_with("def456")


def test_get_pr_number_returns_none_without_commit_info(
    github_plugin, monkeypatch, tmp_path
):
    """No commit info anywhere -> return None instead of raising."""
    _write_event(monkeypatch, tmp_path, {"action": "completed"})
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    github_plugin.repository = MagicMock()

    assert github_plugin._get_pr_number() is None
    github_plugin.repository.get_commit.assert_not_called()
