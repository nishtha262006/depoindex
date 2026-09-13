import json


PATH = "data/manual_review.json"


REVIEWS = {
    11: {
        "topic_relevance": "PASS",
        "boundary_quality": "FAIL",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "The topic is relevant to the ITT student outcomes discussion, but the segment ends during the transition into the Vervent/PEAKS discussion.",
    },
    12: {
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "Begins with the direct discussion of Vervent defendants' involvement in the PEAKS loans and remains substantively coherent.",
    },
    13: {
        "topic_relevance": "PASS",
        "boundary_quality": "FAIL",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "Relevant to the legal analysis of PEAKS loans, but the start includes a reporter interruption and the segment ends while the witness is responding to an enforceability question.",
    },
    14: {
        "topic_relevance": "PASS",
        "boundary_quality": "FAIL",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "The topic concerns testimony about potential misstatements, but the segment starts after an attorney objection and ends during a reporter interruption rather than a substantive transition.",
    },
    15: {
        "topic_relevance": "PASS",
        "boundary_quality": "FAIL",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "The topic is related to Vervent's knowledge and access to loan information, but the segment begins during a reporter interruption, making the start boundary weak.",
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

    print("Updated manual review entries 11-15.")


if __name__ == "__main__":
    main()