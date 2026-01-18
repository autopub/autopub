from pytest_mock import MockerFixture

from autopub.plugins.git import GitConfig, GitPlugin
from autopub.types import ReleaseInfo


def test_post_publish(mocker: MockerFixture) -> None:
    git_plugin = GitPlugin()

    mock_run_command = mocker.patch.object(git_plugin, "run_command")

    release_info = ReleaseInfo(
        release_notes="",
        release_type="major",
        additional_info={},
        version="v1.0.0",
        previous_version="v0.0.0",
    )

    git_plugin.post_publish(release_info)

    mock_run_command.assert_any_call(
        ["git", "config", "--global", "user.email", "autopub@autopub"]
    )
    mock_run_command.assert_any_call(
        ["git", "config", "--global", "user.name", "autopub"]
    )
    mock_run_command.assert_any_call(["git", "tag", "v1.0.0"])
    mock_run_command.assert_any_call(["git", "rm", "RELEASE.md"])
    mock_run_command.assert_any_call(["git", "add", "--all", "--", ":!.autopub"])
    mock_run_command.assert_any_call(
        ["git", "commit", "-m", "🤖 Release v1.0.0\n\n\n\n[skip ci]\n"]
    )
    mock_run_command.assert_any_call(["git", "push"])
    mock_run_command.assert_any_call(["git", "push", "origin", "v1.0.0"])


def test_post_publish_with_config(mocker: MockerFixture) -> None:
    """Test git plugin with custom configuration."""
    git_plugin = GitPlugin()
    config = {
        "plugin_config": {
            "git": {"git-username": "release-bot", "git-email": "bot@example.com"}
        }
    }
    git_plugin.validate_config(config)

    mock_run_command = mocker.patch.object(git_plugin, "run_command")

    release_info = ReleaseInfo(
        release_notes="test release",
        release_type="minor",
        additional_info={},
        version="v1.1.0",
        previous_version="v1.0.0",
    )

    git_plugin.post_publish(release_info)

    mock_run_command.assert_any_call(
        ["git", "config", "--global", "user.email", "bot@example.com"]
    )
    mock_run_command.assert_any_call(
        ["git", "config", "--global", "user.name", "release-bot"]
    )


def test_post_publish_with_env_vars(mocker: MockerFixture) -> None:
    """Test git plugin with environment variables (takes precedence over config)."""
    git_plugin = GitPlugin()
    config = {
        "plugin_config": {
            "git": {"git-username": "config-user", "git-email": "config@example.com"}
        }
    }
    git_plugin.validate_config(config)

    mock_run_command = mocker.patch.object(git_plugin, "run_command")
    mocker.patch.dict(
        "os.environ",
        {"AUTOPUB_GIT_USERNAME": "env-user", "AUTOPUB_GIT_EMAIL": "env@example.com"},
    )

    release_info = ReleaseInfo(
        release_notes="test release",
        release_type="patch",
        additional_info={},
        version="v1.0.1",
        previous_version="v1.0.0",
    )

    git_plugin.post_publish(release_info)

    # Environment variables should take precedence
    mock_run_command.assert_any_call(
        ["git", "config", "--global", "user.email", "env@example.com"]
    )
    mock_run_command.assert_any_call(
        ["git", "config", "--global", "user.name", "env-user"]
    )


def test_git_config_validation() -> None:
    """Test GitConfig validation with both hyphenated and underscored keys."""
    # Test with hyphenated keys (expected format)
    config = GitConfig(**{"git-username": "testuser", "git-email": "test@example.com"})
    assert config.git_username == "testuser"
    assert config.git_email == "test@example.com"

    # Test with defaults
    config = GitConfig()
    assert config.git_username == "autopub"
    assert config.git_email == "autopub@autopub"
