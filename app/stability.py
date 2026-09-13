import json
from collections import Counter

from app.chunker import chunk_transcript
from app.llm import classify_chunk


PDF_PATH = "data/Persis_Yu_Deposition.pdf"
OUTPUT_PATH = "data/stability_results.json"

RUNS = 3


def normalize_topic(topic):
    return " ".join(topic.lower().split())


def main():
    chunks = chunk_transcript(PDF_PATH)

    all_runs = []

    for run_number in range(1, RUNS + 1):
        print(f"\nStarting run {run_number}/{RUNS}...")

        run_results = []

        for chunk_number, chunk in enumerate(chunks, start=1):
            print(
                f"Run {run_number}: "
                f"chunk {chunk_number}/{len(chunks)}..."
            )

            result = classify_chunk(chunk)

            run_results.append(
                {
                    "chunk_number": chunk_number,
                    "start_page": chunk[0]["page"],
                    "start_line": chunk[0]["line"],
                    "end_page": chunk[-1]["page"],
                    "end_line": chunk[-1]["line"],
                    "topic": result["topic"],
                }
            )

        all_runs.append(run_results)

    comparisons = []

    stable_count = 0

    for chunk_number in range(1, len(chunks) + 1):
        topics = [
            run[chunk_number - 1]["topic"]
            for run in all_runs
        ]

        normalized = [
            normalize_topic(topic)
            for topic in topics
        ]

        stable = len(set(normalized)) == 1

        if stable:
            stable_count += 1

        comparisons.append(
            {
                "chunk_number": chunk_number,
                "topics": topics,
                "stable": stable,
            }
        )

    result = {
        "runs": all_runs,
        "summary": {
            "total_chunks": len(chunks),
            "total_runs": RUNS,
            "stable_chunks": stable_count,
            "stability_rate": stable_count / len(chunks),
            "boundary_stability": True,
            "boundary_reason": (
                "Chunk boundaries are deterministic because they are "
                "derived directly from the ordered transcript records."
            ),
        },
        "comparisons": comparisons,
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("Stability test complete.")
    print(f"Chunks: {len(chunks)}")
    print(f"Runs: {RUNS}")
    print(f"Stable chunks: {stable_count}")
    print(
        f"Stability rate: "
        f"{stable_count / len(chunks):.2%}"
    )
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()