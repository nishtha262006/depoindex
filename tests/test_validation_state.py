from app.validation_state import (
    is_validation_current,
    mark_validation_pending,
    record_validation,
    topic_fingerprint,
)


def make_topic():
    return {
        "topic": "ITT student loan practices",
        "start_page": 20,
        "start_line": 1,
        "end_page": 25,
        "end_line": 10,
        "evidence": "ITT discussed student loan practices.",
        "semantic_supported": True,
        "semantic_score": 90,
        "semantic_reason": "The topic is directly supported.",
    }


def test_same_topic_has_current_validation():
    topic = make_topic()

    validated = record_validation(
        topic,
        "VALID",
        "Initial validation passed.",
    )

    assert is_validation_current(validated)
    assert validated["validation_status"] == "VALID"


def test_changed_evidence_invalidates_validation():
    topic = make_topic()

    validated = record_validation(
        topic,
        "VALID",
        "Initial validation passed.",
    )

    validated["evidence"] = (
        "Different supporting evidence."
    )

    assert not is_validation_current(
        validated
    )


def test_changed_boundary_invalidates_validation():
    topic = make_topic()

    validated = record_validation(
        topic,
        "VALID",
        "Initial validation passed.",
    )

    validated["end_line"] = 20

    assert not is_validation_current(
        validated
    )


def test_invalidation_records_original_failure():
    topic = make_topic()

    validated = record_validation(
        topic,
        "VALID",
        "Initial validation passed.",
    )

    invalidated = mark_validation_pending(
        validated,
        "Boundary changed.",
    )

    assert (
        invalidated["validation_status"]
        == "PENDING"
    )

    assert (
        invalidated["validated_fingerprint"]
        is None
    )

    assert (
        invalidated["validation_history"][-1][
            "event"
        ]
        == "VALIDATION_INVALIDATED"
    )


def test_semantic_change_invalidates_validation():
    topic = make_topic()

    validated = record_validation(
        topic,
        "VALID",
        "Initial validation passed.",
    )

    validated["semantic_score"] = 60

    assert not is_validation_current(
        validated
    )