import json
from pathlib import Path


def save_json(
    topics: list[dict],
    output_path: str,
) -> None:
    """
    Save the Topic Index as structured JSON.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            topics,
            f,
            indent=2,
            ensure_ascii=False,
        )


def save_markdown(
    topics: list[dict],
    output_path: str,
) -> None:
    """
    Save a human-readable Topic Index as Markdown.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# DepoIndex — Deposition Topic Index",
        "",
        "Source: Persis Yu deposition",
        "",
        f"Total topics: {len(topics)}",
        "",
    ]

    for index, topic in enumerate(topics, start=1):
        lines.extend(
            [
                f"## {index}. {topic['topic']}",
                "",
                (
                    f"**Location:** "
                    f"Page {topic['start_page']}, Line {topic['start_line']} "
                    f"— "
                    f"Page {topic['end_page']}, Line {topic['end_line']}"
                ),
                "",
                f"**Evidence:** {topic['evidence']}",
                "",
                (
                    f"**Provenance validation:** "
                    f"{'PASS' if topic.get('provenance_valid') else 'FAIL'}"
                ),
                "",
                "---",
                "",
            ]
        )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(lines))