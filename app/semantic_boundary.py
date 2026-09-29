import json

import ollama


MODEL_NAME = "llama3.2:3b"


def _format_records(
    records: list[dict],
) -> str:
    return "\n".join(
        f"[Page {record['page']}, Line {record['line']}] "
        f"{record['text']}"
        for record in records
    )


def detect_internal_boundary(
    left_window: list[dict],
    right_window: list[dict],
) -> dict:
    """
    Determine whether the discussion changes to a
    meaningfully different topic between two transcript windows.
    """
    prompt = f"""
You are analyzing a legal deposition transcript.

Determine whether the discussion changes to a meaningfully
different topic between the two transcript windows.

Return JSON only:

{{
  "decision": "SAME_TOPIC" or "NEW_TOPIC",
  "confidence": 0,
  "reason": "short explanation"
}}

Rules:
- NEW_TOPIC only when there is a meaningful change in subject.
- Do not create a boundary merely because a new question starts.
- Do not create a boundary for minor details within the same subject.
- Confidence must be an integer from 0 to 100.

LEFT WINDOW:
{_format_records(left_window)}

RIGHT WINDOW:
{_format_records(right_window)}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format="json",
        options={"temperature": 0},
    )

    data = json.loads(
        response["message"]["content"]
    )

    decision = str(
        data.get(
            "decision",
            "SAME_TOPIC",
        )
    ).upper()

    if decision not in {
        "SAME_TOPIC",
        "NEW_TOPIC",
    }:
        decision = "SAME_TOPIC"

    try:
        confidence = int(
            data.get(
                "confidence",
                0,
            )
        )
    except (TypeError, ValueError):
        confidence = 0

    confidence = max(
        0,
        min(100, confidence),
    )

    return {
        "decision": decision,
        "confidence": confidence,
        "reason": str(
            data.get(
                "reason",
                "",
            )
        ),
    }


def evaluate_boundary_proposal(
    proposal: dict,
) -> dict:
    """
    Decide whether a proposed semantic boundary has enough
    evidence to be considered for acceptance.

    A boundary must:
    - be classified as NEW_TOPIC
    - have sufficiently high confidence
    - provide a non-empty explanation
    """
    decision = str(
        proposal.get(
            "decision",
            "",
        )
    ).upper()

    confidence = proposal.get(
        "confidence",
        0,
    )

    reason = str(
        proposal.get(
            "reason",
            "",
        )
    ).strip()

    try:
        confidence = int(confidence)
    except (TypeError, ValueError):
        confidence = 0

    if decision != "NEW_TOPIC":
        return {
            "status": "REJECTED",
            "accepted": False,
            "reason": (
                "Boundary was not classified as "
                "a new topic."
            ),
        }

    if confidence < 70:
        return {
            "status": "REVIEW",
            "accepted": False,
            "reason": (
                "Boundary confidence is below "
                "the acceptance threshold."
            ),
        }

    if not reason:
        return {
            "status": "REVIEW",
            "accepted": False,
            "reason": (
                "Boundary proposal does not contain "
                "an explanation."
            ),
        }

    return {
        "status": "ACCEPTED",
        "accepted": True,
        "reason": (
            "Boundary has a NEW_TOPIC decision, "
            "sufficient confidence, and an explanation."
        ),
    }


def propose_boundaries(
    chunk: list[dict],
    window_size: int = 20,
) -> list[dict]:
    """
    Propose possible semantic boundaries inside a chunk.

    Only strong NEW_TOPIC proposals are returned.
    """
    if len(chunk) <= window_size:
        return []

    proposals = []

    for start in range(
        0,
        len(chunk) - window_size,
        window_size,
    ):
        left_start = start
        left_end = start + window_size

        right_start = left_end
        right_end = min(
            right_start + window_size,
            len(chunk),
        )

        left_window = chunk[
            left_start:left_end
        ]

        right_window = chunk[
            right_start:right_end
        ]

        result = detect_internal_boundary(
            left_window,
            right_window,
        )

        proposal = {
            "boundary_index": right_start,
            "page": chunk[right_start]["page"],
            "line": chunk[right_start]["line"],
            "decision": result["decision"],
            "confidence": result["confidence"],
            "reason": result["reason"],
        }

        evaluation = evaluate_boundary_proposal(
            proposal
        )

        if evaluation["accepted"]:
            proposals.append(
                {
                    **proposal,
                    "acceptance_status": (
                        evaluation["status"]
                    ),
                    "acceptance_reason": (
                        evaluation["reason"]
                    ),
                }
            )

    return proposals


def split_chunk_at_boundaries(
    chunk: list[dict],
    boundaries: list[dict],
) -> list[list[dict]]:
    """
    Split a transcript chunk only at explicitly accepted
    semantic boundaries.
    """
    if not boundaries:
        return [chunk]

    valid_indices = sorted(
        {
            boundary["boundary_index"]
            for boundary in boundaries
            if (
                boundary.get(
                    "acceptance_status"
                )
                == "ACCEPTED"
                and 0
                < boundary["boundary_index"]
                < len(chunk)
            )
        }
    )

    segments = []

    start = 0

    for boundary_index in valid_indices:
        segment = chunk[
            start:boundary_index
        ]

        if segment:
            segments.append(segment)

        start = boundary_index

    final_segment = chunk[start:]

    if final_segment:
        segments.append(final_segment)

    return segments


def semantically_segment_chunk(
    chunk: list[dict],
) -> list[list[dict]]:
    """
    Detect accepted semantic boundaries and split the
    chunk accordingly.
    """
    boundaries = propose_boundaries(
        chunk
    )

    return split_chunk_at_boundaries(
        chunk,
        boundaries,
    )


def segmentation_quality(
    segments: list[list[dict]],
) -> float:
    """
    Measure whether segments are internally coherent.

    A segment is considered coherent when its records share
    meaningful words.

    The score is the average proportion of records that
    overlap with the segment's common vocabulary.

    Empty or single-record segments receive a perfect score.
    """
    if not segments:
        return 0.0

    scores = []

    for segment in segments:
        if len(segment) <= 1:
            scores.append(1.0)
            continue

        record_words = []

        for record in segment:
            words = {
                word.strip(
                    ".,:;!?()[]{}\"'-"
                ).lower()
                for word in record["text"].split()
                if len(
                    word.strip(
                        ".,:;!?()[]{}\"'-"
                    )
                ) >= 4
            }

            record_words.append(words)

        common_words = set.intersection(
            *record_words
        )

        if not common_words:
            scores.append(0.0)
            continue

        matching_records = sum(
            1
            for words in record_words
            if words & common_words
        )

        scores.append(
            matching_records
            / len(record_words)
        )

    return sum(scores) / len(scores)


def evaluate_segmentation_change(
    original_segments: list[list[dict]],
    proposed_segments: list[list[dict]],
) -> dict:
    """
    Determine whether a proposed segmentation improves
    internal coherence.

    A boundary is not accepted merely because it creates
    additional segments.

    The proposed segmentation must have strictly higher
    coherence than the original segmentation.
    """
    original_quality = segmentation_quality(
        original_segments
    )

    proposed_quality = segmentation_quality(
        proposed_segments
    )

    if proposed_quality > original_quality:
        return {
            "status": "ACCEPTED",
            "improved": True,
            "original_quality": original_quality,
            "proposed_quality": proposed_quality,
            "reason": (
                "Proposed segmentation improves "
                "internal topic coherence."
            ),
        }

    return {
        "status": "REVIEW",
        "improved": False,
        "original_quality": original_quality,
        "proposed_quality": proposed_quality,
        "reason": (
            "Proposed segmentation does not improve "
            "internal topic coherence."
        ),
    }