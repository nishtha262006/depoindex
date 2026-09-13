import re

from app.provenance import get_provenance_text


def normalize_text(text: str) -> str:
    """
    Normalize transcript text for evidence comparison.

    This removes differences caused by PDF extraction such as:
    - line breaks
    - repeated whitespace
    - common hyphenation across line breaks
    """

    text = text.replace("-\n", "")
    text = text.replace("\n", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


def evidence_matches_text(
    evidence: str,
    transcript_text: str,
) -> bool:
    """
    Check whether evidence occurs in the cited transcript range.

    Exact normalized matching is preferred. If PDF extraction has
    introduced a minor spacing difference, a token-based comparison
    is used as a fallback.
    """

    normalized_evidence = normalize_text(evidence)
    normalized_text = normalize_text(transcript_text)

    if normalized_evidence in normalized_text:
        return True

    evidence_words = re.findall(
        r"\b[a-z0-9]+\b",
        normalized_evidence,
    )

    text_words = re.findall(
        r"\b[a-z0-9]+\b",
        normalized_text,
    )

    if not evidence_words:
        return False

    evidence_length = len(evidence_words)

    for start in range(
        0,
        len(text_words) - evidence_length + 1,
    ):
        window = text_words[
            start:start + evidence_length
        ]

        differences = sum(
            word_a != word_b
            for word_a, word_b in zip(
                evidence_words,
                window,
            )
        )

        # Allow at most one token difference.
        if differences <= 1:
            return True

    return False


def validate_topic_provenance(
    transcript: list[dict],
    topic: dict,
) -> dict:
    """
    Validate that a topic's page/line range exists,
    contains transcript text, and contains the supplied evidence.
    """

    required_fields = [
        "start_page",
        "start_line",
        "end_page",
        "end_line",
    ]

    for field in required_fields:
        if field not in topic:
            return {
                "valid": False,
                "reason": f"Missing field: {field}",
                "text": "",
            }

    if (
        topic["start_page"] > topic["end_page"]
        or (
            topic["start_page"] == topic["end_page"]
            and topic["start_line"] > topic["end_line"]
        )
    ):
        return {
            "valid": False,
            "reason": "Start position occurs after end position.",
            "text": "",
        }

    text = get_provenance_text(
        transcript,
        start_page=topic["start_page"],
        start_line=topic["start_line"],
        end_page=topic["end_page"],
        end_line=topic["end_line"],
    )

    if not text.strip():
        return {
            "valid": False,
            "reason": "No transcript text found for the specified range.",
            "text": "",
        }

    evidence = topic.get("evidence", "").strip()

    if not evidence:
        return {
            "valid": False,
            "reason": "Evidence is empty.",
            "text": text,
        }

    if not evidence_matches_text(
        evidence,
        text,
    ):
        return {
            "valid": False,
            "reason": "Evidence does not appear in the specified transcript range.",
            "text": text,
        }

    return {
        "valid": True,
        "reason": "Provenance range and evidence are valid.",
        "text": text,
    }


def validate_all_topics(
    transcript: list[dict],
    topics: list[dict],
) -> list[dict]:
    """
    Validate provenance for every topic in a Topic Index.

    Returns one validation result for each topic.
    """

    results = []

    for index, topic in enumerate(topics, start=1):
        result = validate_topic_provenance(
            transcript,
            topic,
        )

        results.append(
            {
                "topic_number": index,
                "topic": topic.get("topic", ""),
                **result,
            }
        )

    return results