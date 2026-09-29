from copy import deepcopy

from app.fallback import (
    create_fallback_audit,
    record_fallback,
)
from app.validation_pipeline import (
    invalidate_downstream_levels,
)


def recover_validation_failure(
    state: dict,
    level: str,
    fallback_action: str,
    changed: bool,
    more_permissive: bool,
) -> tuple[dict, dict]:
    """
    Apply a fail-closed recovery action after validation failure.

    The original validation state is preserved in the fallback
    audit trail. Any mutation requires downstream revalidation.
    A more-permissive fallback is rejected.
    """
    updated_state = deepcopy(state)

    original_status = updated_state.get(
        level,
        {},
    ).get(
        "status",
        "REVIEW",
    )

    audit = updated_state.get(
        "fallback_audit"
    )

    if not audit:
        audit = create_fallback_audit()

    revalidation_required = changed

    if changed:
        updated_state = invalidate_downstream_levels(
            updated_state,
            level,
            (
                f"Validation invalidated because fallback "
                f"changed data at the {level} level."
            ),
        )

    audit = record_fallback(
        audit,
        level=level,
        original_status=original_status,
        fallback_action=fallback_action,
        changed=changed,
        more_permissive=more_permissive,
        revalidation_required=revalidation_required,
    )

    updated_state["fallback_audit"] = audit

    # A permissive fallback must never restore the
    # validation level to PASS.
    if more_permissive:
        updated_state[level] = {
            "status": "REVIEW",
            "reason": (
                "Fallback was rejected because it "
                "would weaken validation."
            ),
        }

    updated_state["final_status"] = "REVIEW"

    return updated_state, audit