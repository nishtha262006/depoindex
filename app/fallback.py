from copy import deepcopy


FALLBACK_LEVELS = (
    "extraction",
    "provenance",
    "semantic",
    "boundary",
)


def create_fallback_audit() -> dict:
    """
    Create an empty fallback audit trail.

    No fallback is considered successful by default.
    """
    return {
        "events": [],
        "final_status": "NO_FALLBACK",
    }


def record_fallback(
    audit: dict,
    level: str,
    original_status: str,
    fallback_action: str,
    changed: bool,
    more_permissive: bool,
    revalidation_required: bool,
) -> dict:
    """
    Record a fallback attempt.

    Fallbacks fail closed if they are more permissive than
    the original validation rule.
    """
    updated = deepcopy(audit)

    if level not in FALLBACK_LEVELS:
        raise ValueError(
            f"Unknown fallback level: {level}"
        )

    event = {
        "level": level,
        "original_status": original_status,
        "fallback_action": fallback_action,
        "changed": changed,
        "more_permissive": more_permissive,
        "revalidation_required": revalidation_required,
    }

    if more_permissive:
        event["status"] = "REJECTED"
        event["reason"] = (
            "Fallback was more permissive than the "
            "original validation rule."
        )
    else:
        event["status"] = "RECORDED"
        event["reason"] = (
            "Fallback was recorded without weakening "
            "the validation rule."
        )

    updated["events"].append(event)

    if more_permissive:
        updated["final_status"] = "REVIEW"
    elif revalidation_required:
        updated["final_status"] = "REVALIDATION_REQUIRED"
    else:
        updated["final_status"] = "RECORDED"

    return updated


def fallback_allows_trust(
    audit: dict,
) -> bool:
    """
    Determine whether the fallback audit permits trust.

    No fallback is a valid state and does not block trust.

    A recorded fallback can permit trust only when it:
    - was not more permissive, and
    - did not require revalidation.
    """
    if not audit:
        return True

    if audit.get("final_status") == "NO_FALLBACK":
        return True

    if audit.get("final_status") != "RECORDED":
        return False

    for event in audit.get("events", []):
        if event.get("more_permissive"):
            return False

        if event.get("revalidation_required"):
            return False

    return True