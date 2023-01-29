from .hookspec import plugin_manager, hookspec


@hookspec
def after_release(self, version: str):
    pass


plugin_manager.add_hookspecs(after_release)
