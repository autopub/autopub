import shutil
from pathlib import Path

import pytest

from autopub.plugin_loader import PluginNotFoundError, load_plugins


def test_finds_builtin_by_short_name():
    plugins = load_plugins(["bump_version"])

    assert len(plugins) == 1
    assert plugins[0].__name__ == "BumpVersionPlugin"


def test_finds_builtin_plugin_via_extended_path():
    plugins = load_plugins(["autopub.plugins.bump_version"])

    assert len(plugins) == 1
    assert plugins[0].__name__ == "BumpVersionPlugin"


def test_finds_local_plugin(temporary_working_directory: Path):
    plugin_code = Path(__file__).parent / "fixtures/example_plugin.py"

    plugin_path = temporary_working_directory / "example.py"

    shutil.copy(plugin_code, plugin_path)

    plugins = load_plugins(["example"])

    assert len(plugins) == 1
    assert plugins[0].__name__ == "ExamplePlugin"


def tests_prefers_local_plugin_over_builtin(temporary_working_directory: Path):
    plugin_code = Path(__file__).parent / "fixtures/example_plugin.py"

    plugin_path = temporary_working_directory / "bump_version.py"

    shutil.copy(plugin_code, plugin_path)

    plugins = load_plugins(["bump_version"])

    assert len(plugins) == 1
    assert plugins[0].__name__ == "ExamplePlugin"


def test_raises_if_plugin_not_found_valid_module(temporary_working_directory: Path):
    plugin_path = temporary_working_directory / "example2.py"

    plugin_path.touch()

    with pytest.raises(PluginNotFoundError):
        load_plugins(["example2"])


def test_raises_if_plugin_not_found():
    with pytest.raises(PluginNotFoundError):
        load_plugins(["not_found"])


def test_supports_passing_plugin_class():
    plugins = load_plugins(["autopub.plugins.bump_version:BumpVersionPlugin"])

    assert len(plugins) == 1
    assert plugins[0].__name__ == "BumpVersionPlugin"


def test_finds_local_plugin_with_all(temporary_working_directory: Path):
    plugin_code = Path(__file__).parent / "fixtures/example_plugin_with_all.py"

    plugin_path = temporary_working_directory / "example3.py"

    shutil.copy(plugin_code, plugin_path)

    plugins = load_plugins(["example3"])

    assert len(plugins) == 1
    assert plugins[0].__name__ == "ExamplePlugin"
