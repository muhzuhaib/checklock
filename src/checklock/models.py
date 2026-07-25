from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class RequiredCheck:
    name: str
    source: str | None = None


@dataclass(frozen=True)
class Workflow:
    path: Path
    triggers: frozenset[str]
    has_skip_filter: bool
    filter_line: int | None
    job_names: frozenset[str]


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    required_check: str
    path: str | None = None
    line: int | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
