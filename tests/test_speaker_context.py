from app.speaker_context import (
    resolve_speaker_context,
)


def test_missing_speaker_is_unresolved():
    record = {
        "page": 20,
        "line": 5,
        "text": "I remember that transaction.",
    }

    result = resolve_speaker_context(
        record,
        witness_name="PERSIS YU",
    )

    assert result.speaker is None
    assert result.role is None
    assert result.status == "UNRESOLVED"
    assert result.confidence == 0.0


def test_explicit_speaker_is_resolved():
    record = {
        "page": 20,
        "line": 5,
        "text": "I remember that transaction.",
        "speaker": "PERSIS YU",
        "speaker_role": "WITNESS",
    }

    result = resolve_speaker_context(record)

    assert result.speaker == "PERSIS YU"
    assert result.role == "WITNESS"
    assert result.status == "RESOLVED"
    assert result.confidence == 1.0


def test_unresolved_context_does_not_infer_witness():
    record = {
        "page": 20,
        "line": 5,
        "text": "I remember that transaction.",
    }

    result = resolve_speaker_context(
        record,
        witness_name="PERSIS YU",
    )

    assert result.speaker is None
    assert result.status == "UNRESOLVED"


def test_speaker_context_to_dict():
    record = {
        "page": 20,
        "line": 5,
        "text": "Yes.",
        "speaker": "ATTORNEY",
        "speaker_role": "EXAMINING_ATTORNEY",
    }

    result = resolve_speaker_context(record)

    data = result.to_dict()

    assert data["speaker"] == "ATTORNEY"
    assert data["role"] == "EXAMINING_ATTORNEY"
    assert data["status"] == "RESOLVED"
    assert data["confidence"] == 1.0