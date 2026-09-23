from dataclasses import dataclass, asdict


@dataclass
class TopicSegment:
    topic: str

    start_page: int
    start_line: int

    end_page: int
    end_line: int

    evidence: str

    # Semantic validation fields
    semantic_supported: bool = False
    semantic_score: int = 0
    semantic_reason: str = ""
    supporting_quote: str = ""
    supporting_quote_valid: bool = False

    def to_dict(self) -> dict:
        return asdict(self)