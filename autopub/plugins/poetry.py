import subprocess

from autopub.plugins import AutopubPackageManagerPlugin, AutopubPlugin


class PoetryPlugin(AutopubPlugin, AutopubPackageManagerPlugin):
    def build(self) -> None:
        subprocess.run(["poetry", "build"])
