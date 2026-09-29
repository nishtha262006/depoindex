from app.llm import verify_topic_transcript_support


def make_chunk():
    return [
        {
            "page": 20,
            "line": 1,
            "text": (
                "The company discussed its student loan "
                "servicing practices and related policies."
            ),
        },
        {
            "page": 20,
            "line": 2,
            "text": (
                "The witness explained how the servicing "
                "process operated."
            ),
        },
    ]


def test_topic_has_direct_transcript_support():
    chunk = make_chunk()

    result = verify_topic_transcript_support(
        chunk,
        "student loan servicing practices",
        (
            "The company discussed its student loan "
            "servicing practices and related policies."
        ),
    )

    assert result["supported"] is True


def test_missing_evidence_fails_closed():
    chunk = make_chunk()

    result = verify_topic_transcript_support(
        chunk,
        "student loan servicing practices",
        "",
    )

    assert result["supported"] is False


def test_evidence_not_in_transcript_fails():
    chunk = make_chunk()

    result = verify_topic_transcript_support(
        chunk,
        "student loan servicing practices",
        "The company investigated securities fraud.",
    )

    assert result["supported"] is False


def test_unrelated_topic_fails():
    chunk = make_chunk()

    result = verify_topic_transcript_support(
        chunk,
        "cryptocurrency trading regulations",
        (
            "The company discussed its student loan "
            "servicing practices and related policies."
        ),
    )

    assert result["supported"] is False


def test_both_checks_support_topic():
    from app.llm import combine_semantic_validation

    result = combine_semantic_validation(
        {
            "supported": True,
        },
        {
            "semantic_supported": True,
            "transcript_supported": True,
            "topic_relevant": True,
            "topic_specific": True,
            "semantic_score": 90,
        },
    )

    assert result["status"] == "SUPPORTED"
    assert result["supported"] is True


def test_deterministic_support_failure_requires_review():
    from app.llm import combine_semantic_validation

    result = combine_semantic_validation(
        {
            "supported": False,
        },
        {
            "semantic_supported": True,
            "transcript_supported": True,
            "topic_relevant": True,
            "topic_specific": True,
            "semantic_score": 95,
        },
    )

    assert result["status"] == "REVIEW"
    assert result["supported"] is False


def test_semantic_disagreement_requires_review():
    from app.llm import combine_semantic_validation

    result = combine_semantic_validation(
        {
            "supported": True,
        },
        {
            "semantic_supported": False,
            "transcript_supported": False,
            "topic_relevant": False,
            "topic_specific": False,
            "semantic_score": 40,
        },
    )

    assert result["status"] == "REVIEW"
    assert result["supported"] is False


def test_low_semantic_score_requires_review():
    from app.llm import combine_semantic_validation

    result = combine_semantic_validation(
        {
            "supported": True,
        },
        {
            "semantic_supported": True,
            "transcript_supported": True,
            "topic_relevant": True,
            "topic_specific": True,
            "semantic_score": 65,
        },
    )

    assert result["status"] == "REVIEW"
    assert result["supported"] is False


def test_irrelevant_topic_requires_review():
    from app.llm import combine_semantic_validation

    result = combine_semantic_validation(
        {
            "supported": True,
        },
        {
            "semantic_supported": False,
            "transcript_supported": True,
            "topic_relevant": False,
            "topic_specific": True,
            "semantic_score": 85,
        },
    )

    assert result["status"] == "REVIEW"
    assert result["supported"] is False


def test_overly_broad_topic_requires_review():
    from app.llm import combine_semantic_validation

    result = combine_semantic_validation(
        {
            "supported": True,
        },
        {
            "semantic_supported": False,
            "transcript_supported": True,
            "topic_relevant": True,
            "topic_specific": False,
            "semantic_score": 85,
        },
    )

    assert result["status"] == "REVIEW"
    assert result["supported"] is False