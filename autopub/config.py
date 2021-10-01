import os
import sys

sys.path.append(os.path.dirname(__file__))  # noqa

from plugins import plugin_manager, NAMESPACE


def init():
    init_plugins()


def init_plugins():
    plugin_manager.load_setuptools_entrypoints(NAMESPACE)
