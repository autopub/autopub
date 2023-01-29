import pluggy

NAMESPACE = "autopub"

hookspec = pluggy.HookspecMarker(NAMESPACE)
hookimpl = pluggy.HookimplMarker(NAMESPACE)

plugin_manager = pluggy.PluginManager(NAMESPACE)
