from pytest_mock import MockerFixture

from autopub.plugins.git import GitPlugin
from autopub.types import ReleaseInfo


def test_post_publish(mocker: MockerFixture) -> None:
    git_plugin = GitPlugin()

    mock_run_command = mocker.patch.object(git_plugin, "run_command")

    release_info = ReleaseInfo(
        release_notes="",
        release_type="major",
        additional_info={"new_version": "v1.0.0"},
        version="v1.0.0",
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
    mock_run_command.assert_any_call(["git", "add", "--all", "--", ":!main/.autopub"])
    mock_run_command.assert_any_call(["git", "commit", "-m", "🤖 autopub publish"])
    mock_run_command.assert_any_call(["git", "push"])
    mock_run_command.assert_any_call(["git", "push", "origin", "v1.0.0"])
