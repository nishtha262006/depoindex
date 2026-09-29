from copy import deepcopy

from app.fallback import (
    fallback_allows_trust,
)


VALIDATION_LEVELS = (
    "extraction",
    "provenance",
    "semantic",
    "boundary",
)


def create_validation_state() -> dict:
    """
    Create a fail-closed validation state.

    Every level starts as REVIEW because no validation
    result should be assumed automatically.
    """
    return {
        "extraction": {
            "status": "REVIEW",
            "reason": "Extraction has not been validated.",
        },
        "provenance": {
            "status": "REVIEW",
            "reason": "Provenance has not been validated.",
        },
        "semantic": {
            "status": "REVIEW",
            "reason": "Semantic support has not been validated.",
        },
        "boundary": {
            "status": "REVIEW",
            "reason": "Boundary validation has not been completed.",
        },
        "final_status": "REVIEW",
        "fallback_audit": {
            "events": [],
            "final_status": "NO_FALLBACK",
        },
    }


def set_validation_level(
    state: dict,
    level: str,
    status: str,
    reason: str,
) -> dict:
    """
    Update one validation level.

    Only known validation levels and explicit statuses
    are accepted. Invalid input fails closed.
    """
    updated = deepcopy(state)

    if level not in VALIDATION_LEVELS:
        raise ValueError(
            f"Unknown validation level: {level}"
        )

    if status not in {"PASS", "REVIEW", "FAIL"}:
        status = "REVIEW"

    updated[level] = {
        "status": status,
        "reason": reason,
    }

    updated["final_status"] = calculate_final_status(
        updated
    )

    return updated


def attach_fallback_audit(
    state: dict,
    fallback_audit: dict,
) -> dict:
    """
    Attach a fallback audit trail to the validation state.

    A fallback can never bypass validation.
    """
    updated = deepcopy(state)

    updated["fallback_audit"] = deepcopy(
        fallback_audit
    )

    updated["final_status"] = calculate_final_status(
        updated
    )

    return updated


def calculate_final_status(
    state: dict,
) -> str:
    """
    Calculate the trusted final state.

    The output is trusted only when every validation
    level has explicitly passed and the fallback audit
    does not block trust.
    """
    for level in VALIDATION_LEVELS:
        if state.get(level, {}).get("status") != "PASS":
            return "REVIEW"

    fallback_audit = state.get(
        "fallback_audit",
        {},
    )

    if fallback_audit and not fallback_allows_trust(
        fallback_audit
    ):
        return "REVIEW"

    return "TRUSTED"


def invalidate_downstream_levels(
    state: dict,
    changed_level: str,
    reason: str,
) -> dict:
    """
    Invalidate the changed level and every downstream
    validation level.

    This prevents an older validation result from being
    trusted after a mutation.
    """
    updated = deepcopy(state)

    if changed_level not in VALIDATION_LEVELS:
        raise ValueError(
            f"Unknown validation level: {changed_level}"
        )

    start_index = VALIDATION_LEVELS.index(
        changed_level
    )

    for level in VALIDATION_LEVELS[start_index:]:
        updated[level] = {
            "status": "REVIEW",
            "reason": reason,
        }

    updated["final_status"] = "REVIEW"

    return updated


def is_trusted(
    state: dict,
) -> bool:
    """
    Return True only when all four validation levels
    have explicitly passed and no fallback condition
    blocks trust.
    """
    return (
        calculate_final_status(state)
        == "TRUSTED"
    )