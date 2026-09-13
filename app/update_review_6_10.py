import json


PATH = "data/manual_review.json"


REVIEWS = {
    6: {
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "Covers state laws and requirements governing transfer of student-loan servicing data; transition from servicing changes is appropriate.",
    },
    7: {
        "topic_relevance": "PASS",
        "boundary_quality": "FAIL",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "Topic is relevant to the subsequent for-profit-college discussion, but the segment starts during a discussion of report paragraph numbering, producing a weak start boundary.",
    },
    8: {
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "Covers economic outcomes of ITT students and naturally follows the discussion of ITT and for-profit colleges.",
    },
    9: {
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "Covers the transition from ITT student outcomes to representations and potential misrepresentation; the topic remains substantively coherent.",
    },
    10: {
        "topic_relevance": "PASS",
        "boundary_quality": "FAIL",
        "coverage": "PASS",
        "redundancy": "REVIEW",
        "notes": "The segment continues the misrepresentation discussion from Topic 9 and ends during a reporter interruption, rather than at a substantive topic transition.",
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

    print("Updated manual review entries 6-10.")


if __name__ == "__main__":
    main()