import json
import ollama

MODEL_NAME = "llama3.2:3b"


def _format_records(records: list[dict]) -> str:
    return "\n".join(
        f"[Page {record['page']}, Line {record['line']}] {record['text']}"
        for record in records
    )


def detect_internal_boundary(
    left_window: list[dict],
    right_window: list[dict],
) -> dict:

    prompt = f"""
You are analyzing a legal deposition transcript.

Determine whether the discussion changes to a meaningfully different topic
between the two transcript windows.

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

    data = json.loads(response["message"]["content"])

    decision = str(data.get("decision", "SAME_TOPIC")).upper()

    if decision not in {"SAME_TOPIC", "NEW_TOPIC"}:
        decision = "SAME_TOPIC"

    try:
        confidence = int(data.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0

    confidence = max(0, min(100, confidence))

    return {
        "decision": decision,
        "confidence": confidence,
        "reason": str(data.get("reason", "")),
    }


def propose_boundaries(
    chunk: list[dict],
    window_size: int = 20,
) -> list[dict]:

    if len(chunk) <= window_size:
        return []

    proposals = []

    for start in range(0, len(chunk) - window_size, window_size):
        left_start = start
        left_end = start + window_size

        right_start = left_end
        right_end = min(right_start + window_size, len(chunk))

        left_window = chunk[left_start:left_end]
        right_window = chunk[right_start:right_end]

        result = detect_internal_boundary(
            left_window,
            right_window,
        )

        if (
            result["decision"] == "NEW_TOPIC"
            and result["confidence"] >= 70
        ):
            boundary_record = chunk[right_start]

            proposals.append(
                {
                    "boundary_index": right_start,
                    "page": boundary_record["page"],
                    "line": boundary_record["line"],
                    "decision": result["decision"],
                    "confidence": result["confidence"],
                    "reason": result["reason"],
                }
            )

    return proposals


def split_chunk_at_boundaries(
    chunk: list[dict],
    boundaries: list[dict],
) -> list[list[dict]]:

    if not boundaries:
        return [chunk]

    valid_indices = sorted(
        {
            boundary["boundary_index"]
            for boundary in boundaries
            if 0 < boundary["boundary_index"] < len(chunk)
        }
    )

    segments = []
    start = 0

    for boundary_index in valid_indices:
        segment = chunk[start:boundary_index]

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

    boundaries = propose_boundaries(chunk)

    return split_chunk_at_boundaries(
        chunk,
        boundaries,
    )