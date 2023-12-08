import textwrap
from pathlib import Path

import time_machine

from autopub.plugins.update_changelog import UpdateChangelogPlugin
from autopub.types import ReleaseInfo


@time_machine.travel("2021-08-02")
def test_creates_file(example_project_pdm: Path):
    changelog = example_project_pdm / "CHANGELOG.md"
    assert not changelog.exists()

    info = ReleaseInfo(
        release_type="minor",
        release_notes="This is some example :)",
        version="0.1.0",
        previous_version="0.0.9",
    )

    plugin = UpdateChangelogPlugin()
    plugin.post_prepare(info)

    assert changelog.exists()

    expected_changelog = textwrap.dedent(
        """
        CHANGELOG
        =========

        0.1.0 - 2021-08-02
        ------------------

        This is some example :)
        """
    ).strip()

    assert changelog.read_text().strip() == expected_changelog


@time_machine.travel("2021-08-02")
def test_updates_file(example_project_pdm: Path):
    changelog = example_project_pdm / "CHANGELOG.md"
    assert not changelog.exists()

    initial_changelog = textwrap.dedent(
        """
        CHANGELOG
        =========

        0.0.9 - 2021-08-01
        ------------------

        First version ✨
        """
    ).strip()

    changelog.write_text(initial_changelog)

    info = ReleaseInfo(
        release_type="minor",
        release_notes="This is some example :)",
        version="0.1.0",
        previous_version="0.0.9",
    )

    plugin = UpdateChangelogPlugin()
    plugin.post_prepare(info)

    assert changelog.exists()

    expected_changelog = textwrap.dedent(
        """
        CHANGELOG
        =========

        0.1.0 - 2021-08-02
        ------------------

        This is some example :)

        0.0.9 - 2021-08-01
        ------------------

        First version ✨
        """
    ).strip()

    assert changelog.read_text().strip() == expected_changelog


@time_machine.travel("2021-08-02")
def test_adds_additional_lines(example_project_pdm: Path):
    changelog = example_project_pdm / "CHANGELOG.md"
    assert not changelog.exists()

    initial_changelog = textwrap.dedent(
        """
        CHANGELOG
        =========

        0.0.9 - 2021-08-01
        ------------------

        First version ✨
        """
    ).strip()

    changelog.write_text(initial_changelog)

    info = ReleaseInfo(
        release_type="minor",
        release_notes="This is some example :)",
        version="0.1.0",
        previous_version="0.0.9",
        additional_release_notes=["- Some additional line"],
    )

    plugin = UpdateChangelogPlugin()
    plugin.post_prepare(info)

    assert changelog.exists()

    expected_changelog = textwrap.dedent(
        """
        CHANGELOG
        =========

        0.1.0 - 2021-08-02
        ------------------

        This is some example :)

        - Some additional line

        0.0.9 - 2021-08-01
        ------------------

        First version ✨
        """
    ).strip()

    assert changelog.read_text().strip() == expected_changelog
