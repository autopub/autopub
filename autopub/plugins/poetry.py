import subprocess

from autopub.plugins import AutopubPackageManagerPlugin, AutopubPlugin


class PoetryPlugin(AutopubPlugin, AutopubPackageManagerPlugin):
    def build(self) -> None:
        subprocess.run(["poetry", "build"], check=True)

    def publish(self, **kwargs: str) -> None:
        additional_args = []

        if kwargs.get("repository"):
            additional_args += ["--repository", kwargs["repository"]]

        subprocess.run(["poetry", "publish", *additional_args], check=True)
