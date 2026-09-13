from app.indexer import build_validated_index
from app.output import save_json, save_markdown


PDF_PATH = "data/Persis_Yu_Deposition.pdf"
JSON_OUTPUT = "data/final_topic_index.json"
MARKDOWN_OUTPUT = "data/final_topic_index.md"


def main():
    print("Building validated Topic Index...")

    topics = build_validated_index(PDF_PATH)

    save_json(
        topics,
        JSON_OUTPUT,
    )

    save_markdown(
        topics,
        MARKDOWN_OUTPUT,
    )

    valid_count = sum(
        topic["provenance_valid"]
        for topic in topics
    )

    print()
    print(f"Topics generated: {len(topics)}")
    print(f"Valid provenance: {valid_count}/{len(topics)}")
    print(f"JSON saved to: {JSON_OUTPUT}")
    print(f"Markdown saved to: {MARKDOWN_OUTPUT}")


if __name__ == "__main__":
    main()