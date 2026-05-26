"""Schema helpers for Memory Bridge profiles and evaluations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ProfileValidationError(ValueError):
    """Raised when a memory profile is unsafe or incomplete."""


REQUIRED_TOP_LEVEL_FIELDS = (
    "consent",
    "person",
    "contacts",
    "life_events",
    "daily_routine",
    "privacy_exclusions",
)

UNSAFE_MEDICAL_TERMS = (
    "diagnose",
    "diagnosis",
    "prognosis",
    "predict decline",
    "cognitive score",
    "screen for dementia",
    "medication dosage",
    "change medication",
    "stop medication",
    "emergency",
    "triage",
)


@dataclass(frozen=True)
class ValidationResult:
    """Result returned by low-level validation helpers."""

    passed: bool
    issues: list[str]


def as_list(value: Any) -> list[Any]:
    """Return a value as a list without splitting strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_string(value: Any) -> str:
    """Return a compact string representation for profile values."""
    return " ".join(str(value or "").split())
