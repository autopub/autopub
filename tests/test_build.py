import pytest

from autopub import Autopub
from autopub.exceptions import NoPackageManagerPluginFound
from autopub.plugins import AutopubPlugin


def test_fails_without_any_build_plugin():
    autopub = Autopub()

    with pytest.raises(
        NoPackageManagerPluginFound, match="No package manager plugin found"
    ):
        autopub.build()


def test_works_with_build_plugin():
    built = False

    class ABuildPlugin(AutopubPlugin):
        def build(self):
            nonlocal built
            built = True

        def publish(self, **kwargs: str):  # pragma: no cover
            ...

    autopub = Autopub(plugins=[ABuildPlugin])
    autopub.build()

    assert built


def test_works_with_build_plugin_and_other_plugin():
    built = False

    class ANonBuildPlugin(AutopubPlugin): ...

    class ABuildPlugin(AutopubPlugin):
        def build(self):
            nonlocal built
            built = True

        def publish(self, **kwargs: str):  # pragma: no cover
            ...

    autopub = Autopub(plugins=[ANonBuildPlugin, ABuildPlugin])
    autopub.build()

    assert built
