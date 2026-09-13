import json


PATH = "data/manual_review.json"


REVIEWS = {
    1: {
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "Covers deposition instructions and introductory procedure; boundary is appropriate before continued deposition instructions.",
    },
    2: {
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "Covers the witness's introduction to the Student Borrower Protection Center and its work; boundary follows the introductory organization discussion.",
    },
    3: {
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "Covers advocacy, research, policy work, and student-loan servicing policy activity; transition occurs before the next servicing-focused discussion.",
    },
    4: {
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "Covers the witness's expertise and participation concerning student-loan servicing; boundary leads into concrete servicing changes.",
    },
    5: {
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "coverage": "PASS",
        "redundancy": "PASS",
        "notes": "Covers changes and transfers among federal student-loan servicers; boundary is appropriate before the question about regulations governing data transfer.",
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

    print("Updated manual review entries 1-5.")


if __name__ == "__main__":
    main()