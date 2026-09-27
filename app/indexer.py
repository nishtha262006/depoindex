import json

from app.chunker import chunk_transcript
from app.extractor import extract_deposition
from app.llm import (
    classify_chunk,
    verify_topic_semantics,
)
from app.metadata import extract_metadata
from app.models import TopicSegment
from app.transcript import build_transcript
from app.validator import validate_all_topics


def build_topic_index(
    pdf_path: str,
) -> list[TopicSegment]:
    """
    Build an initial Topic Index from the deposition.

    The LLM receives the transcript chunk together with
    explicitly extracted deposition metadata.

    Page/line provenance remains deterministic and is taken
    directly from the transcript records.
    """
    chunks = chunk_transcript(pdf_path)

    # Extract metadata once from the source PDF.
    pages = extract_deposition(pdf_path)
    metadata = extract_metadata(pages).to_dict()

    topics = []

    for chunk_number, chunk in enumerate(
        chunks,
        start=1,
    ):
        print(
            f"Processing chunk "
            f"{chunk_number}/{len(chunks)}..."
        )

        # Step 1: Generate the topic using transcript
        # plus deposition metadata as context.
        result = classify_chunk(
            chunk,
            metadata,
        )

        # Step 2: Verify semantic support.
        semantic = verify_topic_semantics(
            chunk,
            result["topic"],
            result["summary"],
        )

        start = chunk[0]
        end = chunk[-1]

        topic = TopicSegment(
            topic=result["topic"],
            start_page=start["page"],
            start_line=start["line"],
            end_page=end["page"],
            end_line=end["line"],
            evidence=result["evidence"],
            semantic_supported=semantic[
                "semantic_supported"
            ],
            semantic_score=semantic[
                "semantic_score"
            ],
            semantic_reason=semantic[
                "semantic_reason"
            ],
        )

        topics.append(topic)

    return topics


def build_validated_index(
    pdf_path: str,
) -> list[dict]:
    """
    Build the Topic Index and validate every topic's
    provenance.

    Returns JSON-serializable dictionaries containing
    the topic information, semantic validation result,
    and provenance validation result.
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
                "provenance_valid": validation[
                    "valid"
                ],
                "validation_reason": validation[
                    "reason"
                ],
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