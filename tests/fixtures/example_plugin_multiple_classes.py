from __future__ import annotations

from autopub.plugins import AutopubPlugin


class BasePlugin(AutopubPlugin):
    """This should NOT be loaded - it's just a base class."""

    ...


class ActualPlugin(AutopubPlugin):
    """This SHOULD be loaded - it's the actual plugin."""

    ...


__all__ = ["ActualPlugin"]
