import subprocess

from autopub.plugins import AutopubPackageManagerPlugin, AutopubPlugin


class PDMPlugin(AutopubPlugin, AutopubPackageManagerPlugin):
    def build(self) -> None:
        subprocess.run(["pdm", "build"], check=True)

    def publish(self, **kwargs: str) -> None:
        additional_args = []

        if kwargs.get("repository"):
            additional_args += ["--repository", kwargs["repository"]]

        subprocess.run(["pdm", "publish", *additional_args], check=True)
