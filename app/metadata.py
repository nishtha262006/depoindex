import re
from dataclasses import asdict, dataclass


@dataclass
class MetadataField:
    value: str | None = None
    source: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DepositionMetadata:
    witness: MetadataField
    case_matter: MetadataField
    examining_attorney: MetadataField
    deposition_date: MetadataField

    administrative_information_redacted: bool = False

    def to_dict(self) -> dict:
        return {
            "witness": self.witness.to_dict(),
            "case_matter": self.case_matter.to_dict(),
            "examining_attorney": self.examining_attorney.to_dict(),
            "deposition_date": self.deposition_date.to_dict(),
            "administrative_information_redacted": (
                self.administrative_information_redacted
            ),
        }


def extract_metadata(
    pages: list[dict],
) -> DepositionMetadata:
    """
    Extract metadata explicitly supported by the deposition PDF.

    Each extracted field records:
    - its value
    - where it came from
    - extraction confidence

    Missing or redacted administrative fields remain None.
    No metadata is inferred when the PDF does not explicitly
    support it.
    """

    first_pages_text = "\n".join(
        page["text"]
        for page in pages[:5]
    )

    witness = MetadataField(
        value=None,
        source="Not identified in deposition header",
        confidence=0.0,
    )

    # Capture only the witness name on the same line as
    # "DEPOSITION OF".
    match = re.search(
        r"DEPOSITION\s+OF\s+([^\r\n]+)",
        first_pages_text,
        re.IGNORECASE,
    )

    if match:
        witness = MetadataField(
            value=match.group(1).strip(),
            source="Deposition header: 'DEPOSITION OF'",
            confidence=1.0,
        )

    redacted = (
        "Administrative information redacted"
        in first_pages_text
    )

    return DepositionMetadata(
        witness=witness,
        case_matter=MetadataField(
            value=None,
            source="Not explicitly identified by current extractor",
            confidence=0.0,
        ),
        examining_attorney=MetadataField(
            value=None,
            source="Not explicitly identified by current extractor",
            confidence=0.0,
        ),
        deposition_date=MetadataField(
            value=None,
            source="Not explicitly identified by current extractor",
            confidence=0.0,
        ),
        administrative_information_redacted=redacted,
    )