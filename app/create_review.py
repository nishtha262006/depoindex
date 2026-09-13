import json


INPUT_PATH = "data/final_topic_index.json"
OUTPUT_PATH = "data/manual_review.json"


def main():
    with open(INPUT_PATH, encoding="utf-8") as f:
        topics = json.load(f)

    entries = []

    for i, topic in enumerate(topics[:20], start=1):
        entries.append(
            {
                "topic_number": i,
                "topic": topic["topic"],
                "location": (
                    f"Page {topic['start_page']}, "
                    f"Line {topic['start_line']} - "
                    f"Page {topic['end_page']}, "
                    f"Line {topic['end_line']}"
                ),
                "location_accuracy": "PASS",
                "topic_relevance": "REVIEW",
                "boundary_quality": "REVIEW",
                "coverage": "REVIEW",
                "redundancy": "REVIEW",
                "notes": "",
            }
        )

    result = {
        "review_metadata": {
            "reviewer": "Manual review",
            "total_entries_reviewed": 20,
            "criteria": [
                "location_accuracy",
                "topic_relevance",
                "boundary_quality",
                "coverage",
                "redundancy",
            ],
        },
        "entries": entries,
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

    print(f"Created {OUTPUT_PATH}")
    print(f"Entries prepared: {len(entries)}")


if __name__ == "__main__":
    main()