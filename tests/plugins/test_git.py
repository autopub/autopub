import subprocess

import pytest
from pytest_mock import MockerFixture

from autopub.exceptions import CommandFailed
from autopub.plugins.git import GitConfig, GitPlugin
from autopub.types import ReleaseInfo


def test_post_publish(mocker: MockerFixture) -> None:
    git_plugin = GitPlugin()

    mock_run_command = mocker.patch.object(git_plugin, "run_command")
    mock_is_autopub_ignored = mocker.patch.object(
        git_plugin, "_is_autopub_ignored", return_value=False
    )

    release_info = ReleaseInfo(
        release_notes="",
        release_type="major",
        additional_info={},
        version="v1.0.0",
        previous_version="v0.0.0",
    )

    git_plugin.post_publish(release_info)

    mock_is_autopub_ignored.assert_called_once_with()

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
    mocker.patch.object(git_plugin, "_is_autopub_ignored", return_value=False)

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
    mocker.patch.object(git_plugin, "_is_autopub_ignored", return_value=False)
    mocker.patch.dict(
        "os.environ",
        {"GIT_USERNAME": "env-user", "GIT_EMAIL": "env@example.com"},
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


def test_post_publish_when_autopub_is_ignored(mocker: MockerFixture) -> None:
    git_plugin = GitPlugin()

    mock_run_command = mocker.patch.object(git_plugin, "run_command")
    mocker.patch.object(git_plugin, "_is_autopub_ignored", return_value=True)

    release_info = ReleaseInfo(
        release_notes="",
        release_type="patch",
        additional_info={},
        version="v1.0.1",
        previous_version="v1.0.0",
    )

    git_plugin.post_publish(release_info)

    recorded_commands = [call.args[0] for call in mock_run_command.call_args_list]
    assert ["git", "add", "--all"] in recorded_commands
    assert ["git", "add", "--all", "--", ":!.autopub"] not in recorded_commands


def test_is_autopub_ignored(mocker: MockerFixture) -> None:
    git_plugin = GitPlugin()
    mocker.patch(
        "autopub.plugins.git.subprocess.run",
        return_value=subprocess.CompletedProcess(
            ["git", "check-ignore", "-q", ".autopub"], 0
        ),
    )

    assert git_plugin._is_autopub_ignored() is True


def test_is_autopub_not_ignored(mocker: MockerFixture) -> None:
    git_plugin = GitPlugin()
    mocker.patch(
        "autopub.plugins.git.subprocess.run",
        return_value=subprocess.CompletedProcess(
            ["git", "check-ignore", "-q", ".autopub"], 1
        ),
    )

    assert git_plugin._is_autopub_ignored() is False


def test_is_autopub_ignored_raises_on_git_error(mocker: MockerFixture) -> None:
    git_plugin = GitPlugin()
    mocker.patch(
        "autopub.plugins.git.subprocess.run",
        return_value=subprocess.CompletedProcess(
            ["git", "check-ignore", "-q", ".autopub"], 128
        ),
    )

    with pytest.raises(CommandFailed, match="git check-ignore -q .autopub"):
        git_plugin._is_autopub_ignored()


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
