from __future__ import annotations

import dataclasses
from typing import Any

from typing_extensions import Self


@dataclasses.dataclass(kw_only=True)
class ReleaseInfo:
    """Release information."""

    release_type: str
    release_notes: str
    additional_info: dict[str, Any] = dataclasses.field(default_factory=dict)
    additional_release_notes: list[str] = dataclasses.field(default_factory=list)
    version: str | None = None
    previous_version: str | None = None

    def dict(self) -> dict[str, Any]:
        """Return a dictionary representation of the release info."""
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            release_type=data["release_type"],
            release_notes=data["release_notes"],
            additional_info=data["additional_info"],
            additional_release_notes=data["additional_release_notes"],
            version=data["version"],
            previous_version=data["previous_version"],
        )
