from dataclasses import asdict, dataclass


@dataclass
class SpeakerContext:
    speaker: str | None = None
    role: str | None = None
    source: str = ""
    confidence: float = 0.0
    status: str = "UNRESOLVED"

    def to_dict(self) -> dict:
        return asdict(self)


def resolve_speaker_context(
    record: dict,
    witness_name: str | None = None,
) -> SpeakerContext:
    """
    Resolve speaker information for one transcript record.

    The current transcript parser does not extract speaker labels.
    Therefore, this function fails closed instead of assuming that
    the witness is speaking at every transcript position.

    Explicit speaker information can be supplied by future parser
    improvements through the 'speaker' field in the record.
    """

    speaker = record.get("speaker")

    if speaker:
        role = record.get("speaker_role")

        return SpeakerContext(
            speaker=speaker,
            role=role,
            source="Explicit transcript speaker marker",
            confidence=1.0,
            status="RESOLVED",
        )

    return SpeakerContext(
        speaker=None,
        role=None,
        source=(
            "No speaker marker available at this "
            "transcript position"
        ),
        confidence=0.0,
        status="UNRESOLVED",
    )