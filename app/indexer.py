import json

from app.chunker import chunk_transcript
from app.llm import classify_chunk
from app.models import TopicSegment
from app.transcript import build_transcript
from app.validator import validate_all_topics


def build_topic_index(pdf_path: str) -> list[TopicSegment]:
    """
    Build an initial Topic Index from the deposition.

    Each transcript chunk is classified by the local LLM.
    The chunk boundaries preserve the original page/line
    provenance.
    """

    chunks = chunk_transcript(pdf_path)

    topics = []

    for chunk_number, chunk in enumerate(chunks, start=1):
        print(f"Processing chunk {chunk_number}/{len(chunks)}...")

        result = classify_chunk(chunk)

        start = chunk[0]
        end = chunk[-1]

        topic = TopicSegment(
            topic=result["topic"],
            start_page=start["page"],
            start_line=start["line"],
            end_page=end["page"],
            end_line=end["line"],
            evidence=result["evidence"],
        )

        topics.append(topic)

    return topics


def build_validated_index(pdf_path: str) -> list[dict]:
    """
    Build the Topic Index and validate every topic's provenance.

    Returns JSON-serializable dictionaries containing the
    topic information and provenance validation result.
    """

    transcript = build_transcript(pdf_path)

    topics = build_topic_index(pdf_path)

    topic_dicts = [
        topic.to_dict()
        for topic in topics
    ]

    validation_results = validate_all_topics(
        transcript,
        topic_dicts,
    )

    validated_topics = []

    for topic, validation in zip(
        topic_dicts,
        validation_results,
    ):
        validated_topics.append(
            {
                **topic,
                "provenance_valid": validation["valid"],
                "validation_reason": validation["reason"],
            }
        )

    return validated_topics


def save_index(
    topics: list[dict],
    output_path: str,
) -> None:
    """
    Save the Topic Index as formatted JSON.
    """

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            topics,
            f,
            indent=2,
            ensure_ascii=False,
        )