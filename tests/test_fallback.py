from app.fallback import (
    create_fallback_audit,
    fallback_allows_trust,
    record_fallback,
)


def test_fallback_audit_starts_empty():
    audit = create_fallback_audit()

    assert audit["events"] == []
    assert audit["final_status"] == "NO_FALLBACK"


def test_non_permissive_fallback_is_recorded():
    audit = create_fallback_audit()

    updated = record_fallback(
        audit,
        level="extraction",
        original_status="REVIEW",
        fallback_action="Preserve original transcript records.",
        changed=False,
        more_permissive=False,
        revalidation_required=False,
    )

    assert updated["final_status"] == "RECORDED"
    assert len(updated["events"]) == 1
    assert updated["events"][0]["status"] == "RECORDED"
    assert fallback_allows_trust(updated) is True


def test_fallback_requiring_revalidation_cannot_be_trusted():
    audit = create_fallback_audit()

    updated = record_fallback(
        audit,
        level="provenance",
        original_status="REVIEW",
        fallback_action="Replace missing evidence with deterministic transcript lookup.",
        changed=True,
        more_permissive=False,
        revalidation_required=True,
    )

    assert updated["final_status"] == "REVALIDATION_REQUIRED"
    assert fallback_allows_trust(updated) is False


def test_more_permissive_fallback_is_rejected():
    audit = create_fallback_audit()

    updated = record_fallback(
        audit,
        level="semantic",
        original_status="REVIEW",
        fallback_action="Accept the LLM topic without transcript support.",
        changed=True,
        more_permissive=True,
        revalidation_required=True,
    )

    assert updated["final_status"] == "REVIEW"
    assert updated["events"][0]["status"] == "REJECTED"
    assert fallback_allows_trust(updated) is False


def test_fallback_preserves_original_failure():
    audit = create_fallback_audit()

    updated = record_fallback(
        audit,
        level="boundary",
        original_status="REVIEW",
        fallback_action="Retain the original fixed-size boundary.",
        changed=False,
        more_permissive=False,
        revalidation_required=True,
    )

    event = updated["events"][0]

    assert event["original_status"] == "REVIEW"
    assert event["fallback_action"] == (
        "Retain the original fixed-size boundary."
    )
    assert event["revalidation_required"] is True