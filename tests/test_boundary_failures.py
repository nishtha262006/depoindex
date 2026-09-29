from app.semantic_boundary import (
    evaluate_boundary_proposal,
    evaluate_segmentation_change,
)


def test_false_split_is_rejected():
    proposal = {
        "decision": "SAME_TOPIC",
        "confidence": 95,
        "reason": (
            "Both windows continue discussing "
            "student loan servicing."
        ),
    }

    result = evaluate_boundary_proposal(proposal)

    assert result["status"] == "REJECTED"
    assert result["accepted"] is False


def test_low_confidence_possible_split_requires_review():
    proposal = {
        "decision": "NEW_TOPIC",
        "confidence": 55,
        "reason": (
            "The discussion may be moving "
            "to a different subject."
        ),
    }

    result = evaluate_boundary_proposal(proposal)

    assert result["status"] == "REVIEW"
    assert result["accepted"] is False


def test_missed_transition_does_not_claim_improvement():
    original = [
        [
            {
                "page": 20,
                "line": 1,
                "text": (
                    "The company discussed "
                    "student loan servicing."
                ),
            },
            {
                "page": 20,
                "line": 2,
                "text": (
                    "The SEC investigation examined "
                    "securities reporting."
                ),
            },
        ]
    ]

    proposed = original

    result = evaluate_segmentation_change(
        original,
        proposed,
    )

    assert result["status"] == "REVIEW"
    assert result["improved"] is False