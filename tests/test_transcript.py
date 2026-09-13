from app.transcript import build_transcript
from app.provenance import get_provenance_text


PDF_PATH = r"data\Persis_Yu_Deposition.pdf"


def test_transcript_page_boundaries():
    transcript = build_transcript(PDF_PATH)

    assert len(transcript) > 0

    pages = [record["page"] for record in transcript]

    assert min(pages) == 7
    assert max(pages) == 88


def test_first_transcript_record():
    transcript = build_transcript(PDF_PATH)

    first = transcript[0]

    assert first["page"] == 7
    assert first["line"] == 11
    assert "BY MR. PURCELL" in first["text"]


def test_transcript_has_valid_provenance():
    transcript = build_transcript(PDF_PATH)

    for record in transcript:
        assert isinstance(record["page"], int)
        assert isinstance(record["line"], int)
        assert record["page"] >= 7
        assert record["page"] <= 88
        assert record["line"] >= 1
        assert isinstance(record["text"], str)


def test_provenance_lookup_returns_exact_range():
    transcript = build_transcript(PDF_PATH)

    text = get_provenance_text(
        transcript,
        start_page=87,
        start_line=20,
        end_page=88,
        end_line=3,
    )

    assert "You've reviewed a lot of investigations relating" in text
    assert "Vervent did the servicing" in text
    assert "I do not recall" in text