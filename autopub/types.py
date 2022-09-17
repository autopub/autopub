import dataclasses
from typing import Dict


@dataclasses.dataclass
class ReleaseInfo:
    """Release information."""

    release_type: str
    release_notes: str
    additional_info: Dict[str, str] = dataclasses.field(default_factory=dict)
