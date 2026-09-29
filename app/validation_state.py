import hashlib
import json
from copy import deepcopy


VALIDATED_FIELDS = (
    "topic",
    "start_page",
    "start_line",
    "end_page",
    "end_line",
    "evidence",
    "semantic_supported",
    "semantic_score",
    "semantic_reason",
)


def topic_fingerprint(topic: dict) -> str:
    """
    Create a deterministic fingerprint for the fields that
    affect topic validation.
    """

    relevant_data = {
        field: topic.get(field)
        for field in VALIDATED_FIELDS
    }

    serialized = json.dumps(
        relevant_data,
        sort_keys=True,
        ensure_ascii=False,
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def mark_validation_pending(
    topic: dict,
    reason: str,
) -> dict:
    """
    Invalidate any previous validation result because
    the topic has changed.
    """

    updated = deepcopy(topic)

    previous_fingerprint = updated.get(
        "validated_fingerprint"
    )

    updated["validation_status"] = "PENDING"
    updated["validated_fingerprint"] = None

    history = updated.setdefault(
        "validation_history",
        [],
    )

    history.append(
        {
            "event": "VALIDATION_INVALIDATED",
            "reason": reason,
            "previous_fingerprint": previous_fingerprint,
        }
    )

    return updated


def record_validation(
    topic: dict,
    status: str,
    reason: str,
) -> dict:
    """
    Record validation against the current version of a topic.
    """

    updated = deepcopy(topic)

    fingerprint = topic_fingerprint(
        updated
    )

    updated["validation_status"] = status
    updated["validated_fingerprint"] = fingerprint

    history = updated.setdefault(
        "validation_history",
        [],
    )

    history.append(
        {
            "event": "VALIDATION",
            "status": status,
            "reason": reason,
            "fingerprint": fingerprint,
        }
    )

    return updated


def is_validation_current(
    topic: dict,
) -> bool:
    """
    Return True only if the stored validation belongs
    to the current topic contents.
    """

    stored_fingerprint = topic.get(
        "validated_fingerprint"
    )

    if not stored_fingerprint:
        return False

    return (
        stored_fingerprint
        == topic_fingerprint(topic)
    )