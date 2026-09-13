import json

import ollama

from app.chunker import chunk_transcript


MODEL_NAME = "llama3.2:3b"

PDF_PATH = "data/Persis_Yu_Deposition.pdf"
INPUT_PATH = "data/final_topic_index.json"
OUTPUT_PATH = "data/boundary_analysis.json"


def classify_boundary(previous_topic, current_topic, previous_chunk, current_chunk):
    previous_context = "\n".join(
        f"[Page {r['page']}, Line {r['line']}] {r['text']}"
        for r in previous_chunk[-10:]
    )

    current_context = "\n".join(
        f"[Page {r['page']}, Line {r['line']}] {r['text']}"
        for r in current_chunk[:10]
    )

    prompt = f"""
You are analyzing topic boundaries in a legal deposition transcript.

The previous segment has this topic:
{previous_topic}

The next segment has this topic:
{current_topic}

Compare the transcript immediately before and after the boundary.

Return ONLY valid JSON:

{{
  "decision": "SAME_TOPIC",
  "reason": "short explanation"
}}

The decision must be exactly one of:
- SAME_TOPIC
- NEW_TOPIC

Use SAME_TOPIC when the discussion continues the same substantive subject.
Use NEW_TOPIC when the discussion clearly transitions to a different substantive subject.

Do not base the decision only on the topic labels.
Use the transcript context.

PREVIOUS SEGMENT END:

{previous_context}

CURRENT SEGMENT START:

{current_context}
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
        options={
            "temperature": 0,
        },
    )

    result = json.loads(
        response["message"]["content"]
    )

    decision = str(
        result.get("decision", "NEW_TOPIC")
    ).strip().upper()

    if decision not in {"SAME_TOPIC", "NEW_TOPIC"}:
        decision = "NEW_TOPIC"

    return {
        "decision": decision,
        "reason": str(
            result.get("reason", "")
        ).strip(),
    }


def main():
    chunks = chunk_transcript(PDF_PATH)

    with open(INPUT_PATH, encoding="utf-8") as f:
        topics = json.load(f)

    results = []

    for i in range(len(chunks) - 1):
        print(
            f"Analyzing boundary {i + 1}/{len(chunks) - 1}..."
        )

        result = classify_boundary(
            topics[i]["topic"],
            topics[i + 1]["topic"],
            chunks[i],
            chunks[i + 1],
        )

        results.append(
            {
                "boundary_number": i + 1,
                "previous_topic": topics[i]["topic"],
                "current_topic": topics[i + 1]["topic"],
                **result,
            }
        )

    same_topic = sum(
        result["decision"] == "SAME_TOPIC"
        for result in results
    )

    output = {
        "total_boundaries": len(results),
        "same_topic": same_topic,
        "new_topic": len(results) - same_topic,
        "results": results,
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("Boundary analysis complete.")
    print(f"Boundaries analyzed: {len(results)}")
    print(f"SAME_TOPIC: {same_topic}")
    print(f"NEW_TOPIC: {len(results) - same_topic}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()