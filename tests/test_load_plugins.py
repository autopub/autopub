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


def test_all_selects_correct_plugin_when_multiple_classes(
    temporary_working_directory: Path,
):
    """Test that __all__ selects the correct plugin when multiple classes exist.

    This tests the bug fix where BumpVersionPlugin was being loaded instead
    of the actual package manager plugin (UvPlugin, PDMPlugin, PoetryPlugin)
    because it was imported at the module level.
    """
    plugin_code = Path(__file__).parent / "fixtures/example_plugin_multiple_classes.py"

    plugin_path = temporary_working_directory / "multiple.py"

    shutil.copy(plugin_code, plugin_path)

    plugins = load_plugins(["multiple"])

    assert len(plugins) == 1
    assert plugins[0].__name__ == "ActualPlugin", (
        "Should load ActualPlugin (specified in __all__), "
        "not BasePlugin (which is also in the module)"
    )


def test_package_manager_plugins_load_correctly():
    """Test that uv, pdm, and poetry plugins load correctly.

    This ensures that the __all__ fix works for the actual builtin plugins.
    Previously, BumpVersionPlugin would be loaded instead of the package
    manager plugin because it was imported at the module level.
    """
    # Test UV plugin
    uv_plugins = load_plugins(["autopub.plugins.uv"])
    assert len(uv_plugins) == 1
    assert uv_plugins[0].__name__ == "UvPlugin"

    # Test PDM plugin
    pdm_plugins = load_plugins(["autopub.plugins.pdm"])
    assert len(pdm_plugins) == 1
    assert pdm_plugins[0].__name__ == "PDMPlugin"

    # Test Poetry plugin
    poetry_plugins = load_plugins(["autopub.plugins.poetry"])
    assert len(poetry_plugins) == 1
    assert poetry_plugins[0].__name__ == "PoetryPlugin"
