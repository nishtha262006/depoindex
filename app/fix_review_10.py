import json


PATH = "data/manual_review.json"


def main():
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)

    for entry in data["entries"]:
        if entry["topic_number"] == 10:
            entry["redundancy"] = "PASS"
            entry["notes"] = (
                "The topic is related to Topic 9 but focuses more specifically "
                "on financing and accreditation practices, so it is not considered "
                "redundant. The main issue remains the weak boundary."
            )

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("Fixed Topic 10 redundancy review.")


if __name__ == "__main__":
    main()