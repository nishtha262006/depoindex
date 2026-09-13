import json


INPUT_PATH = "data/boundary_analysis.json"
OUTPUT_PATH = "data/boundary_report.md"


def main():
    with open(INPUT_PATH, encoding="utf-8") as f:
        data = json.load(f)

    total = data["total_boundaries"]
    same_topic = data["same_topic"]
    new_topic = data["new_topic"]

    lines = [
        "# DepoIndex — Boundary Analysis Report",
        "",
        "## Results",
        "",
        f"- Boundaries analyzed: {total}",
        f"- SAME_TOPIC: {same_topic}",
        f"- NEW_TOPIC: {new_topic}",
        f"- Detected transition rate: {new_topic / total:.2%}",
        "",
        "## Detected substantive transitions",
        "",
    ]

    for item in data["results"]:
        if item["decision"] == "NEW_TOPIC":
            lines.extend(
                [
                    f"### Boundary {item['boundary_number']}",
                    "",
                    f"- Previous topic: {item['previous_topic']}",
                    f"- Current topic: {item['current_topic']}",
                    f"- Reason: {item['reason']}",
                    "",
                ]
            )

    lines.extend(
        [
            "## Interpretation",
            "",
            "The boundary classifier provides a second-stage semantic "
            "check over the deterministic chunk boundaries. It identified "
            "two boundaries as substantive topic transitions.",
            "",
            "The current implementation retains the original deterministic "
            "segments rather than automatically merging or splitting them. "
            "This avoids introducing unsupported boundary changes solely "
            "from an additional LLM judgment.",
            "",
        ]
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(lines))

    print(f"Created {OUTPUT_PATH}")


if __name__ == "__main__":
    main()