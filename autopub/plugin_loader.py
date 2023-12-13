from __future__ import annotations

import os
import sys
from importlib import import_module

from autopub.plugins import AutopubPlugin


class PluginNotFoundError(Exception):
    ...


def _is_autopub_plugin(obj: object) -> bool:
    if (
        isinstance(obj, type)
        and issubclass(obj, AutopubPlugin)
        and obj is not AutopubPlugin
    ):
        return True

    return False


def _find_plugin(plugin: str) -> type[AutopubPlugin] | None:
    module_name = plugin
    symbol_name: str | None = None

    if ":" in plugin:
        module_name, symbol_name = plugin.split(":", 1)

    try:
        module = import_module(module_name)
    except ModuleNotFoundError:
        return None

    if symbol_name:
        obj = getattr(module, symbol_name)

        assert _is_autopub_plugin(obj)
        return obj
    else:
        symbols = {
            key: value
            for key, value in module.__dict__.items()
            if not key.startswith("__")
        }

        if "__all__" in module.__dict__:
            symbols = {
                name: symbol
                for name, symbol in symbols.items()
                if name in module.__dict__["__all__"]
            }

        for obj in symbols.values():
            if _is_autopub_plugin(obj):
                return obj

    return None


def load_plugins(names: list[str]) -> list[type[AutopubPlugin]]:
    sys.path.append(os.getcwd())

    plugins: list[type] = []

    for plugin_name in names:
        plugin_class = _find_plugin(f"{plugin_name}")

        if plugin_class is None:
            plugin_class = _find_plugin(f"autopub.plugins.{plugin_name}")

        if plugin_class is None:
            raise PluginNotFoundError(f"Could not find plugin {plugin_name}")

        plugins.append(plugin_class)

    return plugins
