from unittest.mock import MagicMock, patch

import pytest

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
        "Fix bug\n\nCo-authored-by: helper <helper@example.com>"
    )
    mock_pr.get_commits.return_value = [mock_commit]
    mock_pr.get_issue_comments.return_value = []

    github_plugin.pull_request = mock_pr

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
