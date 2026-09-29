from app import indexer


def test_semantic_disagreement_marks_topic_for_review(
    monkeypatch,
):
    fake_chunk = [
        {
            "page": 20,
            "line": 1,
            "text": (
                "The company discussed its student loan "
                "servicing practices."
            ),
        }
    ]

    monkeypatch.setattr(
        indexer,
        "chunk_transcript",
        lambda *_: [fake_chunk],
    )

    monkeypatch.setattr(
        indexer,
        "extract_deposition",
        lambda *_: [],
    )

    monkeypatch.setattr(
        indexer,
        "extract_metadata",
        lambda *_: type(
            "Metadata",
            (),
            {
                "to_dict": lambda *self: {},
            },
        )(),
    )

    monkeypatch.setattr(
        indexer,
        "classify_chunk",
        lambda chunk, metadata: {
            "topic": "Student loan servicing",
            "summary": (
                "The company discussed "
                "student loan servicing."
            ),
            "evidence": (
                "The company discussed its student loan "
                "servicing practices."
            ),
        },
    )

    monkeypatch.setattr(
        indexer,
        "verify_topic_transcript_support",
        lambda chunk, topic, evidence: {
            "supported": True,
            "reason": "Evidence occurs in the transcript.",
        },
    )

    monkeypatch.setattr(
        indexer,
        "verify_topic_semantics",
        lambda chunk, topic, summary: {
            "semantic_supported": False,
            "transcript_supported": False,
            "topic_relevant": False,
            "topic_specific": False,
            "semantic_score": 40,
            "semantic_reason": (
                "The topic is not sufficiently "
                "supported by the full segment."
            ),
        },
    )

    topics = indexer.build_topic_index("dummy.pdf")

    assert len(topics) == 1

    topic = topics[0]

    assert topic.semantic_supported is False
    assert topic.semantic_score == 40

    assert (
        "semantic verifier did not confirm"
        in topic.semantic_reason.lower()
    )


def test_classification_failure_is_fail_closed(
    monkeypatch,
):
    fake_chunk = [
        {
            "page": 20,
            "line": 1,
            "text": "Transcript text.",
        }
    ]

    monkeypatch.setattr(
        indexer,
        "chunk_transcript",
        lambda *_: [fake_chunk],
    )

    monkeypatch.setattr(
        indexer,
        "extract_deposition",
        lambda *_: [],
    )

    monkeypatch.setattr(
        indexer,
        "extract_metadata",
        lambda *_: type(
            "Metadata",
            (),
            {
                "to_dict": lambda *self: {},
            },
        )(),
    )

    def fail_classifier(chunk, metadata):
        raise RuntimeError(
            "simulated Ollama failure"
        )

    monkeypatch.setattr(
        indexer,
        "classify_chunk",
        fail_classifier,
    )

    topics = indexer.build_topic_index("dummy.pdf")

    assert len(topics) == 1

    assert topics[0].llm_failure is True

    assert (
        topics[0].llm_failure_stage
        == "classification"
    )

    assert (
        topics[0].semantic_supported
        is False
    )

    assert topics[0].semantic_score == 0

    assert (
        "classification failed"
        in topics[0].semantic_reason.lower()
    )


def test_semantic_failure_is_fail_closed(
    monkeypatch,
):
    fake_chunk = [
        {
            "page": 20,
            "line": 1,
            "text": (
                "The company discussed its student "
                "loan servicing practices."
            ),
        }
    ]

    monkeypatch.setattr(
        indexer,
        "chunk_transcript",
        lambda *_: [fake_chunk],
    )

    monkeypatch.setattr(
        indexer,
        "extract_deposition",
        lambda *_: [],
    )

    monkeypatch.setattr(
        indexer,
        "extract_metadata",
        lambda *_: type(
            "Metadata",
            (),
            {
                "to_dict": lambda *self: {},
            },
        )(),
    )

    monkeypatch.setattr(
        indexer,
        "classify_chunk",
        lambda chunk, metadata: {
            "topic": "Student loan servicing",
            "summary": (
                "The company discussed "
                "student loan servicing."
            ),
            "evidence": (
                "The company discussed its student "
                "loan servicing practices."
            ),
        },
    )

    monkeypatch.setattr(
        indexer,
        "verify_topic_transcript_support",
        lambda chunk, topic, evidence: {
            "supported": True,
            "reason": "Evidence is grounded.",
        },
    )

    def fail_semantic(chunk, topic, summary):
        raise RuntimeError(
            "simulated semantic verifier failure"
        )

    monkeypatch.setattr(
        indexer,
        "verify_topic_semantics",
        fail_semantic,
    )

    topics = indexer.build_topic_index("dummy.pdf")

    assert len(topics) == 1

    assert topics[0].llm_failure is True

    assert (
        topics[0].llm_failure_stage
        == "semantic"
    )

    assert (
        topics[0].semantic_supported
        is False
    )

    assert topics[0].semantic_score == 0

    assert (
        "semantic validation failed"
        in topics[0].semantic_reason.lower()
    )