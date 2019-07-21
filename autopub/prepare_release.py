import os
import re
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from datetime import datetime

from base import (
    configure_git,
    get_release_info,
    run_process,
    CHANGELOG_FILE,
    CHANGELOG_HEADER,
    ROOT,
    VERSION_HEADER,
    VERSION_STRINGS,
)


def update_version_strings(file_path, new_version):
    version_regex = re.compile(r"(^_*?version_*?\s*=\s*['\"])(\d+\.\d+\.\d+)", re.M)
    with open(file_path, "r+") as f:
        content = f.read()
        f.seek(0)
        f.write(
            re.sub(
                version_regex,
                lambda match: "{}{}".format(match.group(1), new_version),
                content,
            )
        )
        f.truncate()


def prepare_release():
    configure_git()

    POETRY_DUMP_VERSION_OUTPUT = re.compile(
        r"Bumping version from \d+\.\d+\.\d+ to (?P<version>\d+\.\d+\.\d+)"
    )

    type_, release_changelog = get_release_info()

    output = run_process(["poetry", "version", type_])
    version_match = POETRY_DUMP_VERSION_OUTPUT.match(output)

    if not version_match:
        print("Unable to bump the project version using Poetry")
        sys.exit(1)

    new_version = version_match.group("version")

    if VERSION_STRINGS:
        for version_file in VERSION_STRINGS:
            file_path = ROOT / version_file
            update_version_strings(file_path, new_version)

    current_date = datetime.utcnow().strftime("%Y-%m-%d")

    old_changelog_data = ""
    header = ""

    with open(CHANGELOG_FILE, "r") as f:
        lines = f.readlines()

    for index, line in enumerate(lines):
        if CHANGELOG_HEADER != line.strip():
            continue

        old_changelog_data = lines[index + 1 :]
        header = lines[: index + 1]
        break

    with open(CHANGELOG_FILE, "w") as f:
        f.write("".join(header))

        new_version_header = f"{new_version} - {current_date}"

        f.write(f"\n{new_version_header}\n")
        f.write(f"{VERSION_HEADER * len(new_version_header)}\n\n")

        f.write(release_changelog)
        f.write("\n")

        f.write("".join(old_changelog_data))
