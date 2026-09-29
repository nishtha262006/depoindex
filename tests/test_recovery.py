from app.recovery import recover_validation_failure
from app.validation_pipeline import (
    create_validation_state,
    set_validation_level,
)


def make_trusted_state():
    state = create_validation_state()

    for level in (
        "extraction",
        "provenance",
        "semantic",
        "boundary",
    ):
        state = set_validation_level(
            state,
            level,
            "PASS",
            f"{level} passed",
        )

    return state


def test_recovery_preserves_original_failure():
    state = make_trusted_state()

    state["semantic"] = {
        "status": "REVIEW",
        "reason": "Semantic validation failed.",
    }
    state["final_status"] = "REVIEW"

    updated, audit = recover_validation_failure(
        state,
        level="semantic",
        fallback_action=(
            "Use deterministic transcript support."
        ),
        changed=False,
        more_permissive=False,
    )

    assert audit["events"][0]["original_status"] == "REVIEW"
    assert (
        audit["events"][0]["fallback_action"]
        == "Use deterministic transcript support."
    )


def test_changed_fallback_requires_revalidation():
    state = make_trusted_state()

    updated, audit = recover_validation_failure(
        state,
        level="provenance",
        fallback_action=(
            "Repair the evidence using transcript coordinates."
        ),
        changed=True,
        more_permissive=False,
    )

    assert updated["provenance"]["status"] == "REVIEW"
    assert updated["semantic"]["status"] == "REVIEW"
    assert updated["boundary"]["status"] == "REVIEW"

    assert (
        audit["final_status"]
        == "REVALIDATION_REQUIRED"
    )

    assert updated["final_status"] == "REVIEW"


def test_permissive_fallback_is_rejected():
    state = make_trusted_state()

    updated, audit = recover_validation_failure(
        state,
        level="semantic",
        fallback_action=(
            "Accept the topic without transcript support."
        ),
        changed=True,
        more_permissive=True,
    )

    assert updated["semantic"]["status"] == "REVIEW"

    assert (
        audit["events"][0]["status"]
        == "REJECTED"
    )

    assert updated["final_status"] == "REVIEW"


def test_non_permissive_unchanged_fallback_still_needs_no_repair():
    state = make_trusted_state()

    state["semantic"] = {
        "status": "REVIEW",
        "reason": "Semantic validation failed.",
    }
    state["final_status"] = "REVIEW"

    updated, audit = recover_validation_failure(
        state,
        level="semantic",
        fallback_action=(
            "Preserve the original transcript segment."
        ),
        changed=False,
        more_permissive=False,
    )

    assert updated["final_status"] == "REVIEW"
    assert audit["events"][0]["status"] == "RECORDED"