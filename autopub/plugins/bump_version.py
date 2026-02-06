from __future__ import annotations

import pathlib
import re

import tomlkit
from dunamai import Version

from autopub.plugins import AutopubPlugin
from autopub.types import ReleaseInfo


class BumpVersionPlugin(AutopubPlugin):
    @property
    def pyproject_config(self) -> tomlkit.TOMLDocument:
        content = pathlib.Path("pyproject.toml").read_text()

        return tomlkit.parse(content)

    def _get_version(self, config: tomlkit.TOMLDocument) -> str:
        try:
            return config["tool"]["poetry"]["version"]  # type: ignore
        except KeyError:
            return config["project"]["version"]  # type: ignore

    def _update_version(self, config: tomlkit.TOMLDocument, new_version: str) -> None:
        try:
            config["tool"]["poetry"]["version"] = new_version  # type: ignore
        except KeyError:
            config["project"]["version"] = new_version  # type: ignore

    def post_check(self, release_info: ReleaseInfo) -> None:
        config = self.pyproject_config

        bump_type = {"major": 0, "minor": 1, "patch": 2}[release_info.release_type]

        version = Version(self._get_version(config))

        release_info.previous_version = str(version)
        release_info.version = version.bump(bump_type).serialize()

    def _get_package_name(self, config: tomlkit.TOMLDocument) -> str | None:
        """Get the package name from pyproject.toml."""
        try:
            return config["tool"]["poetry"]["name"]  # type: ignore
        except KeyError:
            try:
                return config["project"]["name"]  # type: ignore
            except KeyError:
                return None

    def _find_package_init(self, package_name: str) -> pathlib.Path | None:
        """Find the package's __init__.py file.

        Tries multiple common layouts:
        - src/package_name/__init__.py
        - package_name/__init__.py
        - src/__init__.py (for single-module packages)
        """
        # Convert package name with hyphens to underscores for directory name
        package_dir = package_name.replace("-", "_")

        possible_paths = [
            pathlib.Path("src") / package_dir / "__init__.py",
            pathlib.Path(package_dir) / "__init__.py",
            pathlib.Path("src") / "__init__.py",
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def _update_init_version(self, new_version: str) -> None:
        """Update __version__ in the package's __init__.py file if it exists."""
        config = self.pyproject_config
        package_name = self._get_package_name(config)

        if not package_name:
            return

        init_file = self._find_package_init(package_name)

        if not init_file:
            return

        content = init_file.read_text()

        # Regex pattern to match __version__ = "x.y.z" or __version__ = 'x.y.z'
        pattern = r'__version__\s*=\s*["\'][\d.]+["\']'

        # Check if __version__ exists in the file
        if not re.search(pattern, content):
            return

        # Replace the version
        new_content = re.sub(pattern, f'__version__ = "{new_version}"', content)

        init_file.write_text(new_content)

    def post_prepare(self, release_info: ReleaseInfo) -> None:
        config = self.pyproject_config

        assert release_info.version is not None

        self._update_version(config, release_info.version)

        pathlib.Path("pyproject.toml").write_text(tomlkit.dumps(config))  # type: ignore

        # Update __version__ in __init__.py if it exists
        self._update_init_version(release_info.version)
