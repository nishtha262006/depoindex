import re

from app.models import TopicSegment


STOP_WORDS = {
    "the",
    "and",
    "of",
    "on",
    "in",
    "for",
    "to",
    "a",
    "an",
    "by",
    "with",
    "into",
    "regarding",
}


def normalize_topic(topic: str) -> set[str]:
    """
    Convert a topic name into a set of meaningful words.
    """

    words = re.findall(r"[a-zA-Z]+", topic.lower())

    return {
        word
        for word in words
        if word not in STOP_WORDS and len(word) > 2
    }


def topic_similarity(topic_a: str, topic_b: str) -> float:
    """
    Calculate Jaccard similarity between two topic names.
    """

    words_a = normalize_topic(topic_a)
    words_b = normalize_topic(topic_b)

    if not words_a or not words_b:
        return 0.0

    intersection = words_a & words_b
    union = words_a | words_b

    return len(intersection) / len(union)


def merge_adjacent_topics(
    topics: list[TopicSegment],
    threshold: float = 0.5,
) -> list[TopicSegment]:
    """
    Merge adjacent topics when their names are sufficiently similar.

    Only adjacent topics are considered. This prevents unrelated
    topics appearing elsewhere in the deposition from being merged.
    """

    if not topics:
        return []

    merged = [topics[0]]

    for current in topics[1:]:
        previous = merged[-1]

        similarity = topic_similarity(
            previous.topic,
            current.topic,
        )

        if similarity >= threshold:
            previous.end_page = current.end_page
            previous.end_line = current.end_line

            if current.evidence:
                previous.evidence += " " + current.evidence

        else:
            merged.append(current)

    return merged