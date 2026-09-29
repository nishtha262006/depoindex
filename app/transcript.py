from app.extractor import extract_deposition
from app.provenance import parse_transcript_line
from app.speaker_context import resolve_speaker_context


TESTIMONY_START_PAGE = 7
TESTIMONY_END_PAGE = 88
TESTIMONY_END_LINE = 13


def _build_transcript_with_audit(pdf_path: str):
    """
    Build the structured transcript and collect parser audit information.

    The transcript output remains compatible with the existing pipeline.
    The audit also records speaker-context resolution without inferring
    a speaker when the transcript does not provide one.
    """
    pages = extract_deposition(pdf_path)

    transcript = []

    audit = {
        "pages_processed": 0,
        "pages_with_empty_extraction": [],
        "raw_lines": 0,
        "parsed_lines": 0,
        "ignored_formatting_lines": 0,
        "unparsed_lines": [],
        "duplicate_coordinates": [],
        "ordering_issues": [],
        "line_gaps": [],
        "speaker_context": {
            "resolved": 0,
            "unresolved": 0,
            "records": [],
        },
    }

    seen_coordinates = set()
    previous_line_by_page = {}

    for page in pages:
        page_number = page["pdf_page"]

        if not (
            TESTIMONY_START_PAGE
            <= page_number
            <= TESTIMONY_END_PAGE
        ):
            continue

        audit["pages_processed"] += 1

        if not page["text"].strip():
            audit["pages_with_empty_extraction"].append(
                page_number
            )

        for raw_line_index, raw_line in enumerate(
            page["lines"],
            start=1,
        ):
            audit["raw_lines"] += 1

            parsed = parse_transcript_line(raw_line)

            if parsed["line_number"] is None:
                stripped = raw_line.strip()

                if (
                    not stripped
                    or stripped.isdigit()
                    or stripped.startswith("Page ")
                ):
                    audit["ignored_formatting_lines"] += 1
                else:
                    audit["unparsed_lines"].append(
                        {
                            "page": page_number,
                            "raw_line_index": raw_line_index,
                            "text": stripped,
                        }
                    )

                continue

            line_number = parsed["line_number"]

            if (
                page_number == TESTIMONY_END_PAGE
                and line_number > TESTIMONY_END_LINE
            ):
                continue

            coordinate = (page_number, line_number)

            if coordinate in seen_coordinates:
                audit["duplicate_coordinates"].append(
                    {
                        "page": page_number,
                        "line": line_number,
                    }
                )
            else:
                seen_coordinates.add(coordinate)

            previous_line = previous_line_by_page.get(
                page_number
            )

            if previous_line is not None:
                if line_number <= previous_line:
                    audit["ordering_issues"].append(
                        {
                            "page": page_number,
                            "previous_line": previous_line,
                            "current_line": line_number,
                        }
                    )

                elif line_number > previous_line + 1:
                    audit["line_gaps"].append(
                        {
                            "page": page_number,
                            "from_line": previous_line,
                            "to_line": line_number,
                        }
                    )

            previous_line_by_page[page_number] = line_number

            record = {
                "page": page_number,
                "line": line_number,
                "text": parsed["text"],
            }

            transcript.append(record)

            # Speaker resolution is deliberately separate from
            # static deposition metadata.
            speaker_context = resolve_speaker_context(
                record
            )

            if speaker_context.status == "RESOLVED":
                audit["speaker_context"]["resolved"] += 1
            else:
                audit["speaker_context"]["unresolved"] += 1

            audit["speaker_context"]["records"].append(
                {
                    "page": page_number,
                    "line": line_number,
                    **speaker_context.to_dict(),
                }
            )

            audit["parsed_lines"] += 1

    return transcript, audit


def build_transcript(pdf_path: str) -> list[dict]:
    """
    Build a structured transcript containing only
    the substantive deposition testimony.

    This function keeps the original public interface so
    existing code continues to work.
    """
    transcript, _ = _build_transcript_with_audit(pdf_path)
    return transcript


def audit_transcript(pdf_path: str) -> dict:
    """
    Return parser, extraction, and speaker-context audit information.
    """
    _, audit = _build_transcript_with_audit(pdf_path)
    return audit