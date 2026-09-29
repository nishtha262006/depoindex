from app.metadata import extract_metadata


def test_metadata_extracts_witness(monkeypatch):
    from app import metadata

    pages = [
        {
            "pdf_page": 1,
            "text": "DEPOSITION OF Persis Yu",
        }
    ]

    result = extract_metadata(pages)

    assert result.witness.value == "Persis Yu"
    assert result.witness.confidence == 1.0
    assert "DEPOSITION OF" in result.witness.source


def test_metadata_missing_fields_fail_closed():
    pages = [
        {
            "pdf_page": 1,
            "text": "Administrative information redacted",
        }
    ]

    result = extract_metadata(pages)

    assert result.case_matter.value is None
    assert result.examining_attorney.value is None
    assert result.deposition_date.value is None
    assert result.case_matter.confidence == 0.0
    assert result.examining_attorney.confidence == 0.0
    assert result.deposition_date.confidence == 0.0


def test_metadata_detects_redacted_administrative_information():
    pages = [
        {
            "pdf_page": 1,
            "text": "Administrative information redacted",
        }
    ]

    result = extract_metadata(pages)

    assert result.administrative_information_redacted is True


def test_metadata_to_dict_preserves_provenance():
    pages = [
        {
            "pdf_page": 1,
            "text": "DEPOSITION OF Persis Yu",
        }
    ]

    result = extract_metadata(pages).to_dict()

    assert result["witness"]["value"] == "Persis Yu"
    assert result["witness"]["source"] == (
        "Deposition header: 'DEPOSITION OF'"
    )
    assert result["witness"]["confidence"] == 1.0


def test_metadata_prompt_preserves_value_source_and_confidence():
    from app.llm import format_metadata_for_prompt

    metadata = {
        "witness": {
            "value": "Persis Yu",
            "source": "Deposition header",
            "confidence": 1.0,
        },
        "case_matter": {
            "value": None,
            "source": "Not identified",
            "confidence": 0.0,
        },
        "examining_attorney": {
            "value": None,
            "source": "Not identified",
            "confidence": 0.0,
        },
        "deposition_date": {
            "value": None,
            "source": "Not identified",
            "confidence": 0.0,
        },
    }

    formatted = format_metadata_for_prompt(metadata)

    assert "Persis Yu" in formatted
    assert "Deposition header" in formatted
    assert "confidence=1.0" in formatted
    assert "Not identified" in formatted