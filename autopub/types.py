from __future__ import annotations

import dataclasses


@dataclasses.dataclass(kw_only=True)
class ReleaseInfo:
    """Release information."""

    release_type: str
    release_notes: str
    additional_info: dict[str, str] = dataclasses.field(default_factory=dict)

    def with_version(
        self, version: str, previous_version: str
    ) -> ReleaseInfoWithVersion:
        """Return a new ReleaseInfoWithVersion instance."""
        return ReleaseInfoWithVersion(
            release_type=self.release_type,
            release_notes=self.release_notes,
            additional_info=self.additional_info,
            version=version,
            previous_version=previous_version,
        )


@dataclasses.dataclass(kw_only=True)
class ReleaseInfoWithVersion(ReleaseInfo):
    """Release information with version."""

    version: str
    previous_version: str
