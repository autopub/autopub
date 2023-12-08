import contextlib
import os
import sys
from importlib import import_module

from autopub.plugins import AutopubPlugin


def _find_plugin(module: object) -> type[AutopubPlugin] | None:
    for obj in module.__dict__.values():
        if (
            isinstance(obj, type)
            and issubclass(obj, AutopubPlugin)
            and obj is not AutopubPlugin
        ):
            return obj

    return None


def _get_plugin(name_or_path: str) -> type[AutopubPlugin] | None:
    with contextlib.suppress(ImportError):
        plugin_module = import_module(name_or_path)

        return _find_plugin(plugin_module)

    return None


def find_plugins(names: list[str]) -> list[type[AutopubPlugin]]:
    sys.path.append(os.getcwd())

    plugins: list[type] = []

    for plugin_name in names:
        plugin_class = _get_plugin(f"{plugin_name}")

        if plugin_class is None:
            plugin_class = _get_plugin(f"autopub.plugins.{plugin_name}")

        if plugin_class is None:
            raise ValueError(f"Could not find plugin {plugin_name}")

        plugins.append(plugin_class)

    return plugins
