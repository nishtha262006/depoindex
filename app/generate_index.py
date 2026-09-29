from app.indexer import build_validated_index
from app.output import save_json, save_markdown


PDF_PATH = "data/Persis_Yu_Deposition.pdf"
JSON_OUTPUT = "data/final_topic_index.json"
MARKDOWN_OUTPUT = "data/final_topic_index.md"


def main():
    print("Building validated Topic Index...")

    topics = build_validated_index(
        PDF_PATH
    )

    save_json(
        topics,
        JSON_OUTPUT,
    )

    save_markdown(
        topics,
        MARKDOWN_OUTPUT,
    )

    trusted_count = sum(
        topic.get(
            "validation_status"
        ) == "TRUSTED"
        for topic in topics
    )

    review_count = sum(
        topic.get(
            "validation_status"
        ) == "REVIEW"
        for topic in topics
    )

    provenance_count = sum(
        topic.get(
            "provenance_valid",
            False,
        )
        for topic in topics
    )

    print()
    print(
        f"Topics generated: "
        f"{len(topics)}"
    )
    print(
        f"Trusted topics: "
        f"{trusted_count}/{len(topics)}"
    )
    print(
        f"Topics requiring review: "
        f"{review_count}/{len(topics)}"
    )
    print(
        f"Valid provenance: "
        f"{provenance_count}/{len(topics)}"
    )
    print(
        f"JSON saved to: "
        f"{JSON_OUTPUT}"
    )
    print(
        f"Markdown saved to: "
        f"{MARKDOWN_OUTPUT}"
    )


if __name__ == "__main__":
    main()