from app.semantic_boundary import (
    segmentation_quality,
    split_chunk_at_boundaries,
)


def test_accepted_boundary_improves_segmentation_quality():
    chunk = [
        {
            "page": 20,
            "line": 1,
            "text": (
                "The company discussed student loan "
                "servicing practices."
            ),
        },
        {
            "page": 20,
            "line": 2,
            "text": (
                "The witness explained student loan "
                "servicing procedures."
            ),
        },
        {
            "page": 20,
            "line": 3,
            "text": (
                "The SEC investigation examined "
                "securities reporting."
            ),
        },
        {
            "page": 20,
            "line": 4,
            "text": (
                "The SEC reviewed securities reporting "
                "and investigation records."
            ),
        },
    ]

    unsplit = [chunk]

    accepted_boundary = {
        "boundary_index": 2,
        "decision": "NEW_TOPIC",
        "confidence": 95,
        "reason": (
            "The subject changes from loan servicing "
            "to an SEC investigation."
        ),
        "acceptance_status": "ACCEPTED",
    }

    split = split_chunk_at_boundaries(
        chunk,
        [accepted_boundary],
    )

    unsplit_quality = segmentation_quality(unsplit)
    split_quality = segmentation_quality(split)

    assert len(split) == 2
    assert split_quality > unsplit_quality


def test_rejected_same_topic_boundary_does_not_split():
    chunk = [
        {
            "page": 20,
            "line": 1,
            "text": (
                "The company discussed student loan "
                "servicing practices."
            ),
        },
        {
            "page": 20,
            "line": 2,
            "text": (
                "The witness explained student loan "
                "servicing procedures."
            ),
        },
    ]

    unsplit = [chunk]

    rejected_boundary = {
        "boundary_index": 1,
        "decision": "SAME_TOPIC",
        "confidence": 95,
        "reason": (
            "The discussion remains about student "
            "loan servicing."
        ),
        "acceptance_status": "REJECTED",
    }

    accepted_boundaries = [
        boundary
        for boundary in [rejected_boundary]
        if boundary["acceptance_status"] == "ACCEPTED"
    ]

    split = split_chunk_at_boundaries(
        chunk,
        accepted_boundaries,
    )

    assert len(split) == 1

    assert segmentation_quality(split) == segmentation_quality(
        unsplit
    )