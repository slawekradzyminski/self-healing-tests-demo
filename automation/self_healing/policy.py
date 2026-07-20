from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Iterable


CLASSIFICATIONS = {
    "PRODUCT_BUG",
    "TEST_DEFECT",
    "CI_ENVIRONMENT",
    "INCONCLUSIVE",
}
REPAIR_CONFIDENCE = 0.90
ALLOWED_DIRECTORIES = {"tests", "pages", "fixtures", "components", "config"}
ALLOWED_SUFFIXES = {".ts", ".tsx"}


@dataclass(frozen=True)
class TriageResult:
    classification: str
    confidence: float
    affected_repository: str
    fix_applied: bool
    changed_files: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "TriageResult":
        classification = value.get("classification")
        if classification not in CLASSIFICATIONS:
            raise ValueError(f"Unsupported classification: {classification!r}")

        confidence = value.get("confidence")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0 <= float(confidence) <= 1:
            raise ValueError("confidence must be between 0 and 1")

        changed_files = value.get("changed_files")
        if not isinstance(changed_files, list) or not all(
            isinstance(item, str) and item for item in changed_files
        ):
            raise ValueError("changed_files must be a list of non-empty strings")

        affected_repository = value.get("affected_repository")
        if not isinstance(affected_repository, str):
            raise ValueError("affected_repository must be a string")

        fix_applied = value.get("fix_applied")
        if not isinstance(fix_applied, bool):
            raise ValueError("fix_applied must be a boolean")

        return cls(
            classification=classification,
            confidence=float(confidence),
            affected_repository=affected_repository,
            fix_applied=fix_applied,
            changed_files=tuple(changed_files),
        )

    def satisfies_repair_gate(self, repository: str) -> bool:
        return (
            self.classification == "TEST_DEFECT"
            and self.confidence >= REPAIR_CONFIDENCE
            and self.affected_repository == repository
            and self.fix_applied
        )


def validate_changed_files(reported: Iterable[str], actual: Iterable[str]) -> tuple[str, ...]:
    reported_files = tuple(sorted(set(reported)))
    actual_files = tuple(sorted(set(actual)))

    if not actual_files:
        raise ValueError("Claude reported a repair but produced no tracked diff")
    if reported_files != actual_files:
        raise ValueError(
            f"Reported changed files {reported_files!r} do not match the diff {actual_files!r}"
        )

    for filename in actual_files:
        path = PurePosixPath(filename)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Repair path escapes the repository: {filename}")
        if len(path.parts) < 2 or path.parts[0] not in ALLOWED_DIRECTORIES:
            raise ValueError(f"Repair touched a disallowed path: {filename}")
        if path.suffix not in ALLOWED_SUFFIXES:
            raise ValueError(f"Repair touched a disallowed file type: {filename}")

    return actual_files
