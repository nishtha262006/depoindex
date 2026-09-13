import json

from app.chunker import chunk_transcript
from app.llm import classify_chunk


PDF_PATH = r"data\Persis_Yu_Deposition.pdf"
OUTPUT_PATH = r"data\baseline_topics.json"


def create_baseline():
    chunks = chunk_transcript(PDF_PATH)

    results = []

    for chunk_number, chunk in enumerate(chunks, start=1):
        print(f"Processing chunk {chunk_number}/{len(chunks)}...")

        result = classify_chunk(chunk)

        results.append(
            {
                "chunk_number": chunk_number,
                "start_page": chunk[0]["page"],
                "start_line": chunk[0]["line"],
                "end_page": chunk[-1]["page"],
                "end_line": chunk[-1]["line"],
                "topic": result["topic"],
                "summary": result["summary"],
                "evidence": result["evidence"],
            }
        )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Saved baseline results to {OUTPUT_PATH}")


if __name__ == "__main__":
    create_baseline()