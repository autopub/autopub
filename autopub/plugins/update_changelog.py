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

        lines = self.changelog_file.read_text().splitlines()

        # Look for CHANGELOG header (e.g., "CHANGELOG\n=========")
        header = []
        old_changelog_data = []
        header_found = False

        for index, line in enumerate(lines):
            if CHANGELOG_HEADER == line.strip():
                old_changelog_data = lines[index + 1 :]
                header = lines[: index + 1]
                header_found = True
                break

        # If no header found, treat all existing content as old changelog data
        if not header_found:
            old_changelog_data = lines

        new_version = release_info.version

        assert new_version is not None

        with self.changelog_file.open("w") as f:
            # Write header if it exists
            if header:
                f.write("\n".join(header))
                f.write("\n\n")

            # Write new version entry
            new_version_header = f"{new_version} - {current_date}"
            f.write(f"{new_version_header}\n")
            f.write(f"{VERSION_HEADER * len(new_version_header)}\n\n")
            f.write(release_info.release_notes)

            for line in release_info.additional_release_notes:
                f.write(f"\n\n{line}")

            # Write old changelog data (skip if empty or only whitespace)
            old_content = "\n".join(old_changelog_data).strip()
            if old_content:
                f.write("\n\n")
                # Preserve the original formatting including any trailing newlines
                f.write("\n".join(old_changelog_data))
