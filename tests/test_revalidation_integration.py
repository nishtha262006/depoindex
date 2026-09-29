from app.validation_state import (
    is_validation_current,
    mark_validation_pending,
    record_validation,
)


def make_topic():
    return {
        "topic": "ITT student loan practices",
        "start_page": 20,
        "start_line": 1,
        "end_page": 25,
        "end_line": 10,
        "evidence": (
            "ITT discussed student loan practices."
        ),
        "semantic_supported": True,
        "semantic_score": 90,
        "semantic_reason": (
            "The topic is directly supported."
        ),
    }


def test_validated_topic_remains_current_without_change():
    topic = make_topic()

    validated = record_validation(
        topic,
        "VALID",
        "Initial validation passed.",
    )

    assert validated["validation_status"] == "VALID"
    assert is_validation_current(validated)


def test_boundary_change_requires_revalidation():
    topic = make_topic()

    validated = record_validation(
        topic,
        "VALID",
        "Initial validation passed.",
    )

    validated["end_line"] = 20

    assert not is_validation_current(validated)


def test_revalidation_accepts_new_version():
    topic = make_topic()

    validated = record_validation(
        topic,
        "VALID",
        "Initial validation passed.",
    )

    validated["end_line"] = 20

    assert not is_validation_current(validated)

    revalidated = record_validation(
        validated,
        "VALID",
        "Revalidation passed after boundary change.",
    )

    assert is_validation_current(revalidated)
    assert (
        revalidated["validation_status"]
        == "VALID"
    )


def test_invalidated_topic_is_not_current():
    topic = make_topic()

    validated = record_validation(
        topic,
        "VALID",
        "Initial validation passed.",
    )

    invalidated = mark_validation_pending(
        validated,
        "Evidence changed.",
    )

    assert (
        invalidated["validation_status"]
        == "PENDING"
    )

    assert not is_validation_current(
        invalidated
    )