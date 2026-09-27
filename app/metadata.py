import re
from dataclasses import asdict, dataclass


@dataclass
class DepositionMetadata:
    witness: str | None = None
    case_matter: str | None = None
    examining_attorney: str | None = None
    deposition_date: str | None = None
    administrative_information_redacted: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def extract_metadata(pages: list[dict]) -> DepositionMetadata:
    """
    Extract only metadata explicitly supported by the deposition PDF.

    Missing or redacted administrative fields remain None rather than
    being inferred.
    """
    first_pages_text = "\n".join(
        page["text"]
        for page in pages[:5]
    )

    witness = None

    # Capture only the witness name on the same line as
    # "DEPOSITION OF".
    match = re.search(
        r"DEPOSITION\s+OF\s+([^\r\n]+)",
        first_pages_text,
        re.IGNORECASE,
    )

    if match:
        witness = match.group(1).strip()

    redacted = (
        "Administrative information redacted"
        in first_pages_text
    )

    return DepositionMetadata(
        witness=witness,
        administrative_information_redacted=redacted,
    )