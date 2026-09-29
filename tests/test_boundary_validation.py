from app.semantic_boundary import (
    evaluate_boundary_proposal,
)


def test_strong_new_topic_boundary_is_accepted():
    result = evaluate_boundary_proposal(
        {
            "decision": "NEW_TOPIC",
            "confidence": 90,
            "reason": (
                "The discussion changes from loan "
                "servicing to an SEC investigation."
            ),
        }
    )

    assert result["status"] == "ACCEPTED"
    assert result["accepted"] is True


def test_low_confidence_boundary_requires_review():
    result = evaluate_boundary_proposal(
        {
            "decision": "NEW_TOPIC",
            "confidence": 60,
            "reason": "Possible topic transition.",
        }
    )

    assert result["status"] == "REVIEW"
    assert result["accepted"] is False


def test_same_topic_boundary_is_rejected():
    result = evaluate_boundary_proposal(
        {
            "decision": "SAME_TOPIC",
            "confidence": 95,
            "reason": (
                "The discussion remains on "
                "the same subject."
            ),
        }
    )

    assert result["status"] == "REJECTED"
    assert result["accepted"] is False


def test_boundary_without_reason_requires_review():
    result = evaluate_boundary_proposal(
        {
            "decision": "NEW_TOPIC",
            "confidence": 90,
            "reason": "",
        }
    )

    assert result["status"] == "REVIEW"
    assert result["accepted"] is False


def test_invalid_confidence_fails_closed():
    result = evaluate_boundary_proposal(
        {
            "decision": "NEW_TOPIC",
            "confidence": "not-a-number",
            "reason": "Possible topic transition.",
        }
    )

    assert result["status"] == "REVIEW"
    assert result["accepted"] is False