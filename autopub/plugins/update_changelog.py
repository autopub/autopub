from __future__ import annotations

from datetime import date
from pathlib import Path

from autopub.plugins import AutopubPlugin
from autopub.types import ReleaseInfo

# TODO: from config
CHANGELOG_HEADER = "========="
VERSION_HEADER = "-"


class UpdateChangelogPlugin(AutopubPlugin):
    @property
    def changelog_file(self) -> Path:
        return Path("CHANGELOG.md")

    def post_prepare(self, release_info: ReleaseInfo) -> None:
        if not self.changelog_file.exists():
            self.changelog_file.write_text(f"CHANGELOG\n{CHANGELOG_HEADER}\n\n")

        current_date = date.today().strftime("%Y-%m-%d")

        old_changelog_data = ""
        header = ""

        lines = self.changelog_file.read_text().splitlines()

        for index, line in enumerate(lines):
            if CHANGELOG_HEADER != line.strip():
                continue

            old_changelog_data = lines[index + 1 :]
            header = lines[: index + 1]
            break

        new_version = release_info.version

        assert new_version is not None

        with self.changelog_file.open("w") as f:
            f.write("\n".join(header))
            f.write("\n")

            new_version_header = f"{new_version} - {current_date}"

            f.write(f"\n{new_version_header}\n")
            f.write(f"{VERSION_HEADER * len(new_version_header)}\n\n")
            f.write(release_info.release_notes)

            for line in release_info.additional_release_notes:
                f.write(f"\n\n{line}")

            f.write("\n")
            f.write("\n".join(old_changelog_data))
