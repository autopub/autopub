import dataclasses


@dataclasses.dataclass
class ReleaseInfo:
    """Release information."""

    release_type: str
    release_notes: str
    additional_info: dict[str, str] = dataclasses.field(default_factory=dict)
    version: str | None = None
