from app.transcript import build_transcript

from app.provenance import get_provenance_text


PDF_PATH = r"data\Persis_Yu_Deposition.pdf"


def test_transcript_page_boundaries():
    transcript = build_transcript(PDF_PATH)

    assert len(transcript) > 0

    pages = [
        record["page"]
        for record in transcript
    ]

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
        assert isinstance(
            record["page"],
            int,
        )

        assert isinstance(
            record["line"],
            int,
        )

        assert record["page"] >= 7
        assert record["page"] <= 88
        assert record["line"] >= 1

        assert isinstance(
            record["text"],
            str,
        )


def test_provenance_lookup_returns_exact_range():
    transcript = build_transcript(PDF_PATH)

    text = get_provenance_text(
        transcript,
        start_page=87,
        start_line=20,
        end_page=88,
        end_line=3,
    )

    assert (
        "You've reviewed a lot of investigations relating"
        in text
    )

    assert (
        "Vervent did the servicing"
        in text
    )

    assert "I do not recall" in text


def test_audit_detects_unparsed_lines(
    monkeypatch,
):
    from app import transcript

    def fake_extract(*_):
        return [
            {
                "pdf_page": 7,
                "text": (
                    "1    Valid transcript line\n"
                    "Unparsed testimony line"
                ),
                "lines": [
                    "1    Valid transcript line",
                    "Unparsed testimony line",
                ],
            }
        ]

    monkeypatch.setattr(
        transcript,
        "extract_deposition",
        fake_extract,
    )

    audit = transcript.audit_transcript(
        "dummy.pdf"
    )

    assert len(
        audit["unparsed_lines"]
    ) == 1

    assert (
        audit["unparsed_lines"][0]["text"]
        == "Unparsed testimony line"
    )


def test_audit_detects_duplicate_coordinates(
    monkeypatch,
):
    from app import transcript

    def fake_extract(*_):
        return [
            {
                "pdf_page": 7,
                "text": (
                    "1    First\n"
                    "1    Duplicate"
                ),
                "lines": [
                    "1    First",
                    "1    Duplicate",
                ],
            }
        ]

    monkeypatch.setattr(
        transcript,
        "extract_deposition",
        fake_extract,
    )

    audit = transcript.audit_transcript(
        "dummy.pdf"
    )

    assert audit["duplicate_coordinates"] == [
        {
            "page": 7,
            "line": 1,
        }
    ]


def test_audit_detects_line_gaps(
    monkeypatch,
):
    from app import transcript

    def fake_extract(*_):
        return [
            {
                "pdf_page": 7,
                "text": (
                    "1    First\n"
                    "3    Third"
                ),
                "lines": [
                    "1    First",
                    "3    Third",
                ],
            }
        ]

    monkeypatch.setattr(
        transcript,
        "extract_deposition",
        fake_extract,
    )

    audit = transcript.audit_transcript(
        "dummy.pdf"
    )

    assert audit["line_gaps"] == [
        {
            "page": 7,
            "from_line": 1,
            "to_line": 3,
        }
    ]


def test_transcript_audit_records_unresolved_speaker_context(
    monkeypatch,
):
    from app import transcript

    def fake_extract(*_):
        return [
            {
                "pdf_page": 7,
                "text": "1    Q. What happened?",
                "lines": [
                    "1    Q. What happened?",
                ],
            }
        ]

    monkeypatch.setattr(
        transcript,
        "extract_deposition",
        fake_extract,
    )

    transcript_data, audit = (
        transcript._build_transcript_with_audit(
            "dummy.pdf"
        )
    )

    assert len(transcript_data) == 1

    assert (
        audit["speaker_context"]["unresolved"]
        == 1
    )

    assert (
        audit["speaker_context"]["resolved"]
        == 0
    )

    record = (
        audit["speaker_context"]["records"][0]
    )

    assert record["page"] == 7
    assert record["line"] == 1
    assert record["speaker"] is None
    assert record["status"] == "UNRESOLVED"
    assert record["confidence"] == 0.0


def test_transcript_output_does_not_add_speaker_fields(
    monkeypatch,
):
    from app import transcript

    def fake_extract(*_):
        return [
            {
                "pdf_page": 7,
                "text": "1    Q. What happened?",
                "lines": [
                    "1    Q. What happened?",
                ],
            }
        ]

    monkeypatch.setattr(
        transcript,
        "extract_deposition",
        fake_extract,
    )

    transcript_data, _ = (
        transcript._build_transcript_with_audit(
            "dummy.pdf"
        )
    )

    assert transcript_data == [
        {
            "page": 7,
            "line": 1,
            "text": "Q. What happened?",
        }
    ]