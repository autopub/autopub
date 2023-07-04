from typing import Protocol, runtime_checkable

from autopub.exceptions import AutopubException
from autopub.types import ReleaseInfo


class AutopubPlugin:
    data: dict[str, object] = {}

    def validate_release_notes(self, release_info: ReleaseInfo):
        ...

    def on_release_notes_valid(self, release_info: ReleaseInfo):
        ...

    def on_release_notes_invalid(self, exception: AutopubException):
        ...


@runtime_checkable
class AutopubPackageManagerPlugin(Protocol):
    def build(self) -> None:
        ...
