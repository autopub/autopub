import os
import re
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from datetime import datetime

import tomlkit
from base import (
    CHANGELOG_FILE,
    CHANGELOG_HEADER,
    PYPROJECT_FILE,
    ROOT,
    VERSION_HEADER,
    VERSION_STRINGS,
    configure_git,
    dict_get,
    get_project_version,
    get_release_info,
)
from dunamai import Version
from github_contributor import append_github_contributor


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

    type_, release_changelog = get_release_info()

    version = Version(get_project_version())
    new_version = version.bump({"major": 0, "minor": 1, "patch": 2}[type_]).serialize()

    with open(PYPROJECT_FILE, "r") as f:
        config = tomlkit.load(f)

    poetry = dict_get(config, ["tool", "poetry", "version"])
    if poetry:
        config["tool"]["poetry"]["version"] = new_version
    else:
        config["project"]["version"] = new_version

    with open(PYPROJECT_FILE, "w") as f:
        config = tomlkit.dump(config, f)

    if VERSION_STRINGS:
        for version_file in VERSION_STRINGS:
            file_path = ROOT / version_file
            update_version_strings(file_path, new_version)

    current_date = datetime.utcnow().strftime("%Y-%m-%d")

    old_changelog_data = ""
    header = ""

    if not CHANGELOG_FILE.is_file():
        with open(CHANGELOG_FILE, "a+") as f:
            f.write(f"CHANGELOG\n{CHANGELOG_HEADER}\n\n")

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
        append_github_contributor(f)
        f.write("\n")

        f.write("".join(old_changelog_data))
