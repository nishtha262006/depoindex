import json


PATH = "data/boundary_analysis.json"


def main():
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)

    for item in data["results"]:
        if item["decision"] == "NEW_TOPIC":
            print(f"Boundary {item['boundary_number']}")
            print(f"Previous: {item['previous_topic']}")
            print(f"Current:  {item['current_topic']}")
            print(f"Reason:   {item['reason']}")
            print()


if __name__ == "__main__":
    main()