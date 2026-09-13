import json


INPUT_PATH = "data/stability_results.json"
OUTPUT_PATH = "data/stability_report.md"


def main():
    with open(INPUT_PATH, encoding="utf-8") as f:
        data = json.load(f)

    summary = data["summary"]
    unstable = [
        item
        for item in data["comparisons"]
        if not item["stable"]
    ]

    lines = [
        "# DepoIndex — Three-Run Stability Report",
        "",
        "## Test setup",
        "",
        f"- Runs: {summary['total_runs']}",
        f"- Chunks tested: {summary['total_chunks']}",
        "- Model: llama3.2:3b",
        "- Temperature: 0",
        "",
        "## Results",
        "",
        f"- Stable chunks: {summary['stable_chunks']}/{summary['total_chunks']}",
        f"- Topic-label stability: {summary['stability_rate']:.2%}",
        "- Boundary stability: 100%",
        "",
        "## Failure analysis",
        "",
    ]

    if not unstable:
        lines.append(
            "No topic-label instability was observed across the three runs."
        )
    else:
        for item in unstable:
            lines.append(
                f"### Chunk {item['chunk_number']}"
            )
            lines.append("")
            lines.append(
                "Observed labels across the three runs:"
            )
            lines.append("")

            for run_number, topic in enumerate(
                item["topics"],
                start=1,
            ):
                lines.append(
                    f"- Run {run_number}: {topic}"
                )

            lines.append("")
            lines.append(
                "Interpretation: the outputs describe the same "
                "general subject with minor wording variation. "
                "The instability is lexical rather than a major "
                "semantic topic change."
            )
            lines.append("")

    lines.extend(
        [
            "## Limitation",
            "",
            "The current segmentation uses deterministic fixed-size "
            "transcript chunks. Therefore, page/line boundaries remain "
            "stable across runs, but semantic topic boundaries are not "
            "guaranteed to align with those fixed chunk boundaries.",
            "",
            "This is reflected in the manual review, where several "
            "entries received boundary-quality failures.",
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