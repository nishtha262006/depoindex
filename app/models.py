from dataclasses import dataclass, asdict


@dataclass
class TopicSegment:
    topic: str
    start_page: int
    start_line: int
    end_page: int
    end_line: int
    evidence: str

    def to_dict(self) -> dict:
        return asdict(self)