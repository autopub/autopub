import pytest
from pydantic import BaseModel

from autopub import Autopub, AutopubPlugin
from autopub.exceptions import InvalidConfiguration


def test_validate_config_nothing_to_do():
    class PluginWithConfig(AutopubPlugin):
        id: str = "plugin_with_config"

        class Config(BaseModel):
            my_config: str = "default"

    autopub = Autopub(plugins=[PluginWithConfig])

    autopub.config = {}

    autopub.validate_config()

    plugin = autopub.plugins[0]

    assert isinstance(plugin.config, PluginWithConfig.Config)
    assert plugin.config.my_config == "default"


def test_validate_config():
    class PluginWithConfig(AutopubPlugin):
        id: str = "plugin_with_config"

        class Config(BaseModel):
            my_config: str = "default"

    autopub = Autopub(plugins=[PluginWithConfig])

    autopub.config = {"plugin_with_config": {"my_config": "value"}}

    autopub.validate_config()

    plugin = autopub.plugins[0]

    assert isinstance(plugin.config, PluginWithConfig.Config)
    assert plugin.config.my_config == "value"


def test_validate_config_invalid():
    class PluginWithConfig(AutopubPlugin):
        id: str = "plugin_with_config"

        class Config(BaseModel):
            my_config: str = "default"

    autopub = Autopub(plugins=[PluginWithConfig])

    autopub.config = {"plugin_with_config": {"my_config": 123}}

    with pytest.raises(InvalidConfiguration) as e:
        autopub.validate_config()

    assert "plugin_with_config" in e.value.validation_errors
