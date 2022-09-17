from autopub.plugins import AutopubPackageManagerPlugin, AutopubPlugin


class PoetryPlugin(AutopubPlugin, AutopubPackageManagerPlugin):
    def build(self) -> None:
        print("building with poetry")

        # TODO: actual build and test
