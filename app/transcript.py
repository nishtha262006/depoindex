from app.extractor import extract_deposition
from app.provenance import parse_transcript_line


TESTIMONY_START_PAGE = 7
TESTIMONY_END_PAGE = 88
TESTIMONY_END_LINE = 13


def build_transcript(pdf_path: str) -> list[dict]:
    """
    Build a structured transcript containing only
    the substantive deposition testimony.

    Each record contains:
    - page: original PDF page number
    - line: original deposition line number
    - text: cleaned transcript text
    """

    pages = extract_deposition(pdf_path)

    transcript = []

    for page in pages:
        page_number = page["pdf_page"]

        if not (TESTIMONY_START_PAGE <= page_number <= TESTIMONY_END_PAGE):
            continue

        for raw_line in page["lines"]:
            parsed = parse_transcript_line(raw_line)

            if parsed["line_number"] is None:
                continue

            # Stop at the end of the actual testimony.
            if (
                page_number == TESTIMONY_END_PAGE
                and parsed["line_number"] > TESTIMONY_END_LINE
            ):
                continue

            transcript.append(
                {
                    "page": page_number,
                    "line": parsed["line_number"],
                    "text": parsed["text"],
                }
            )

    return transcript