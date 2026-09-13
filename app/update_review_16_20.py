import json


PATH = "data/manual_review.json"


REVIEWS = {
    16: {
        "topic_relevance": "PASS",
        "boundary_quality": "FAIL",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "The disclosure-requirements topic is relevant, but the segment begins in the middle of the preceding answer rather than at the substantive disclosure question.",
    },
    17: {
        "topic_relevance": "PASS",
        "boundary_quality": "FAIL",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "The enforceability topic is relevant, but the segment begins in the middle of the preceding disclosure-related answer.",
    },
    18: {
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "The segment transitions into discussion of the CFPB settlement and remains substantively coherent around the settlement and government-loan discussion.",
    },
    19: {
        "topic_relevance": "PASS",
        "boundary_quality": "FAIL",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "The ITT-related topic is relevant, but the segment begins in the middle of a continuing hypothetical/question sequence.",
    },
    20: {
        "topic_relevance": "FAIL",
        "boundary_quality": "FAIL",
        "coverage": "FAIL",
        "redundancy": "PASS",
        "notes": "The segment begins with CFPB findings and only later reaches the SEC investigation, so the SEC-only topic label does not accurately represent the full segment.",
    },
}


def main():
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)

    for entry in data["entries"]:
        number = entry["topic_number"]

        if number in REVIEWS:
            entry.update(REVIEWS[number])

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("Updated manual review entries 16-20.")


if __name__ == "__main__":
    main()