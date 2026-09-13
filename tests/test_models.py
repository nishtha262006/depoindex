import json

from app.models import TopicSegment
from app.transcript import build_transcript
from app.validator import validate_all_topics, validate_topic_provenance


PDF_PATH = r"data\Persis_Yu_Deposition.pdf"


def test_topic_segment_to_dict():
    topic = TopicSegment(
        topic="Background and qualifications",
        start_page=9,
        start_line=5,
        end_page=10,
        end_line=18,
        evidence="Witness describes her background and qualifications.",
    )

    result = topic.to_dict()

    assert result["topic"] == "Background and qualifications"
    assert result["start_page"] == 9
    assert result["start_line"] == 5
    assert result["end_page"] == 10
    assert result["end_line"] == 18
    assert result["evidence"] == "Witness describes her background and qualifications."


def test_valid_topic_provenance():
    transcript = build_transcript(PDF_PATH)

    topic = {
        "start_page": 87,
        "start_line": 20,
        "end_page": 88,
        "end_line": 3,
        "evidence": "I do not recall",
    }

    result = validate_topic_provenance(
        transcript,
        topic,
    )

    assert result["valid"] is True
    assert "Vervent did the servicing" in result["text"]


def test_invalid_topic_provenance():
    transcript = build_transcript(PDF_PATH)

    topic = {
        "start_page": 200,
        "start_line": 1,
        "end_page": 200,
        "end_line": 5,
        "evidence": "This evidence does not exist.",
    }

    result = validate_topic_provenance(
        transcript,
        topic,
    )

    assert result["valid"] is False


def test_all_baseline_topics_have_valid_provenance():
    transcript = build_transcript(PDF_PATH)

    with open(
        "data/baseline_topics.json",
        encoding="utf-8",
    ) as f:
        topics = json.load(f)

    results = validate_all_topics(
        transcript,
        topics,
    )

    assert len(results) == 26
    assert all(result["valid"] for result in results)