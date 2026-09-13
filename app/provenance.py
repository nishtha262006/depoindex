import re


LINE_NUMBER_PATTERN = re.compile(r"^\s*(\d{1,3})\s+(.*)$")
TIMESTAMP_PATTERN = re.compile(r"\s+\d{2}:\d{2}\s*$")


def parse_transcript_line(line: str) -> dict:
    """
    Parse a single extracted deposition line.

    Returns the original transcript line number and cleaned text.
    """

    line = line.strip()

    if not line:
        return {
            "line_number": None,
            "text": "",
        }

    if line.isdigit():
        return {
            "line_number": None,
            "text": "",
        }

    if line.startswith("Page "):
        return {
            "line_number": None,
            "text": "",
        }

    match = LINE_NUMBER_PATTERN.match(line)

    if not match:
        return {
            "line_number": None,
            "text": line,
        }

    line_number = int(match.group(1))
    text = match.group(2).strip()

    text = TIMESTAMP_PATTERN.sub("", text).strip()

    return {
        "line_number": line_number,
        "text": text,
    }


def get_provenance_text(
    transcript: list[dict],
    start_page: int,
    start_line: int,
    end_page: int,
    end_line: int,
) -> str:
    """
    Return the exact cleaned transcript text within a page/line range.

    The range is inclusive.
    """

    selected = []

    for record in transcript:
        page = record["page"]
        line = record["line"]

        after_start = (
            page > start_page
            or (page == start_page and line >= start_line)
        )

        before_end = (
            page < end_page
            or (page == end_page and line <= end_line)
        )

        if after_start and before_end:
            selected.append(record["text"])

    return "\n".join(selected)