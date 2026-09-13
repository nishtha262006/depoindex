import json

from app.transcript import build_transcript


PDF_PATH = "data/Persis_Yu_Deposition.pdf"
INDEX_PATH = "data/final_topic_index.json"
OUTPUT_PATH = "data/review_report.txt"


def main():
    transcript = build_transcript(PDF_PATH)

    with open(INDEX_PATH, encoding="utf-8") as f:
        topics = json.load(f)

    lines = []

    lines.append("DEPOINDEX — MANUAL REVIEW REPORT")
    lines.append("=" * 80)
    lines.append("")
    lines.append(
        "Review the first 20 topics for location accuracy, topic relevance, "
        "boundary quality, coverage, and redundancy."
    )
    lines.append("")

    for number, topic in enumerate(topics[:20], start=1):
        lines.append("=" * 80)
        lines.append(f"TOPIC {number}: {topic['topic']}")
        lines.append("-" * 80)
        lines.append(
            f"Range: Page {topic['start_page']}, Line {topic['start_line']} "
            f"- Page {topic['end_page']}, Line {topic['end_line']}"
        )
        lines.append("")
        lines.append(f"Evidence: {topic['evidence']}")
        lines.append("")

        # Show the first 5 records at the start boundary.
        lines.append("START BOUNDARY CONTEXT:")
        start_index = None

        for i, record in enumerate(transcript):
            if (
                record["page"] == topic["start_page"]
                and record["line"] == topic["start_line"]
            ):
                start_index = i
                break

        if start_index is not None:
            for record in transcript[
                max(0, start_index - 2):start_index + 5
            ]:
                lines.append(
                    f"[Page {record['page']}, Line {record['line']}] "
                    f"{record['text']}"
                )

        lines.append("")
        lines.append("END BOUNDARY CONTEXT:")

        end_index = None

        for i, record in enumerate(transcript):
            if (
                record["page"] == topic["end_page"]
                and record["line"] == topic["end_line"]
            ):
                end_index = i
                break

        if end_index is not None:
            for record in transcript[
                max(0, end_index - 4):end_index + 3
            ]:
                lines.append(
                    f"[Page {record['page']}, Line {record['line']}] "
                    f"{record['text']}"
                )

        lines.append("")
        lines.append("")

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(lines))

    print(f"Created {OUTPUT_PATH}")
    print("Topics included: 20")


if __name__ == "__main__":
    main()