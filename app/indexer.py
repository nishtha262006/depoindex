import json

from app.chunker import chunk_transcript
from app.extractor import extract_deposition
from app.llm import (
    classify_chunk,
    combine_semantic_validation,
    verify_topic_semantics,
    verify_topic_transcript_support,
)
from app.metadata import extract_metadata
from app.models import TopicSegment
from app.recovery import recover_validation_failure
from app.transcript import (
    audit_transcript,
    build_transcript,
)
from app.validation_pipeline import (
    create_validation_state,
    set_validation_level,
)
from app.validation_state import (
    is_validation_current,
    record_validation,
)
from app.validator import validate_all_topics


def build_topic_index(
    pdf_path: str,
) -> list[TopicSegment]:
    """
    Build an initial Topic Index.

    Deterministic transcript/evidence validation is performed
    before semantic validation so that unnecessary LLM calls
    are avoided.

    LLM failures are fail-closed:
    the affected topic is marked unresolved and can never
    become TRUSTED without later revalidation.
    """
    chunks = chunk_transcript(pdf_path)

    pages = extract_deposition(pdf_path)
    metadata = extract_metadata(pages).to_dict()

    topics = []

    for chunk_number, chunk in enumerate(
        chunks,
        start=1,
    ):
        print(
            f"Processing chunk "
            f"{chunk_number}/{len(chunks)}..."
        )

        start = chunk[0]
        end = chunk[-1]

        # -----------------------------------------------------
        # Topic classification
        # -----------------------------------------------------
        try:
            result = classify_chunk(
                chunk,
                metadata,
            )
        except Exception as exc:
            error_message = (
                f"Topic classification failed: "
                f"{type(exc).__name__}: {exc}"
            )

            print(
                f"  WARNING: {error_message}"
            )

            topic = TopicSegment(
                topic="UNRESOLVED TOPIC",
                start_page=start["page"],
                start_line=start["line"],
                end_page=end["page"],
                end_line=end["line"],
                evidence="",
                semantic_supported=False,
                semantic_score=0,
                semantic_reason=error_message,
                llm_failure=True,
                llm_failure_stage="classification",
            )

            topics.append(topic)
            continue

        # -----------------------------------------------------
        # Deterministic transcript/evidence validation
        # -----------------------------------------------------
        support = verify_topic_transcript_support(
            chunk,
            result["topic"],
            result["evidence"],
        )

        # -----------------------------------------------------
        # Independent semantic validation
        # -----------------------------------------------------
        if support["supported"]:
            try:
                semantic = verify_topic_semantics(
                    chunk,
                    result["topic"],
                    result["summary"],
                )

                semantic_validation = (
                    combine_semantic_validation(
                        support,
                        semantic,
                    )
                )

                llm_failure = False
                llm_failure_stage = ""

            except Exception as exc:
                error_message = (
                    f"Semantic validation failed: "
                    f"{type(exc).__name__}: {exc}"
                )

                print(
                    f"  WARNING: {error_message}"
                )

                semantic = {
                    "semantic_supported": False,
                    "transcript_supported": False,
                    "topic_relevant": False,
                    "topic_specific": False,
                    "semantic_score": 0,
                    "semantic_reason": error_message,
                }

                semantic_validation = {
                    "status": "REVIEW",
                    "supported": False,
                    "reason": (
                        "Semantic validation failed; "
                        "topic remains in REVIEW."
                    ),
                }

                llm_failure = True
                llm_failure_stage = "semantic"

        else:
            semantic = {
                "semantic_supported": False,
                "transcript_supported": False,
                "topic_relevant": False,
                "topic_specific": False,
                "semantic_score": 0,
                "semantic_reason": (
                    "Semantic verification was not run "
                    "because deterministic transcript "
                    "support failed."
                ),
            }

            semantic_validation = {
                "status": "REVIEW",
                "supported": False,
                "reason": (
                    "Deterministic transcript support failed."
                ),
            }

            llm_failure = False
            llm_failure_stage = ""

        topic = TopicSegment(
            topic=result["topic"],
            start_page=start["page"],
            start_line=start["line"],
            end_page=end["page"],
            end_line=end["line"],
            evidence=result["evidence"],
            semantic_supported=semantic_validation[
                "supported"
            ],
            semantic_score=semantic[
                "semantic_score"
            ],
            semantic_reason=(
                semantic["semantic_reason"]
                + " "
                + semantic_validation["reason"]
            ).strip(),
            llm_failure=llm_failure,
            llm_failure_stage=llm_failure_stage,
        )

        topics.append(topic)

    return topics


def build_validated_index(
    pdf_path: str,
) -> list[dict]:
    """
    Build and validate the Topic Index through four levels:

    1. extraction
    2. provenance
    3. semantic
    4. boundary

    Any unresolved failure remains REVIEW.
    """
    transcript = build_transcript(pdf_path)

    # ---------------------------------------------------------
    # Level 1: Extraction validation
    # ---------------------------------------------------------
    extraction_audit = audit_transcript(pdf_path)

    extraction_passed = (
        extraction_audit["parsed_lines"] > 0
        and not extraction_audit["unparsed_lines"]
        and not extraction_audit["duplicate_coordinates"]
        and not extraction_audit["ordering_issues"]
    )

    topics = build_topic_index(pdf_path)

    topic_dicts = [
        topic.to_dict()
        for topic in topics
    ]

    validation_results = validate_all_topics(
        transcript,
        topic_dicts,
    )

    validated_topics = []

    for topic, validation in zip(
        topic_dicts,
        validation_results,
    ):
        state = create_validation_state()

        # -----------------------------------------------------
        # Level 1: Extraction
        # -----------------------------------------------------
        if extraction_passed:
            state = set_validation_level(
                state,
                "extraction",
                "PASS",
                "Transcript extraction audit passed.",
            )
        else:
            state = set_validation_level(
                state,
                "extraction",
                "REVIEW",
                "Transcript extraction audit found unresolved issues.",
            )

        # -----------------------------------------------------
        # Level 2: Provenance
        # -----------------------------------------------------
        if validation["valid"]:
            state = set_validation_level(
                state,
                "provenance",
                "PASS",
                validation["reason"],
            )
        else:
            state = set_validation_level(
                state,
                "provenance",
                "REVIEW",
                validation["reason"],
            )

            state, _ = recover_validation_failure(
                state,
                level="provenance",
                fallback_action=(
                    "Preserve the original transcript coordinates "
                    "and require provenance review."
                ),
                changed=False,
                more_permissive=False,
            )

        # -----------------------------------------------------
        # Level 3: Semantic validation
        # -----------------------------------------------------
        if topic["llm_failure"]:
            state = set_validation_level(
                state,
                "semantic",
                "REVIEW",
                topic["semantic_reason"],
            )

            state, _ = recover_validation_failure(
                state,
                level="semantic",
                fallback_action=(
                    "Preserve the original LLM failure and "
                    "retain the topic in REVIEW until semantic "
                    "validation succeeds."
                ),
                changed=False,
                more_permissive=False,
            )

        elif topic["semantic_supported"]:
            state = set_validation_level(
                state,
                "semantic",
                "PASS",
                topic["semantic_reason"],
            )

        else:
            state = set_validation_level(
                state,
                "semantic",
                "REVIEW",
                topic["semantic_reason"],
            )

            state, _ = recover_validation_failure(
                state,
                level="semantic",
                fallback_action=(
                    "Retain the topic in REVIEW until "
                    "semantic support is revalidated."
                ),
                changed=False,
                more_permissive=False,
            )

        # -----------------------------------------------------
        # Level 4: Boundary validation
        # -----------------------------------------------------
        state = set_validation_level(
            state,
            "boundary",
            "PASS",
            (
                "No semantic boundary mutation was applied; "
                "the validated fixed segment was retained."
            ),
        )

        # -----------------------------------------------------
        # Record final validation state
        # -----------------------------------------------------
        validated = record_validation(
            topic,
            state["final_status"],
            "Four-level validation completed.",
        )

        validated["validation_state"] = state

        validated["provenance_valid"] = (
            validation["valid"]
        )

        validated["validation_reason"] = (
            validation["reason"]
        )

        # -----------------------------------------------------
        # Final fail-closed check
        # -----------------------------------------------------
        if state["final_status"] != "TRUSTED":
            validated["validation_status"] = "REVIEW"

        if not is_validation_current(
            validated
        ):
            validated["validation_status"] = (
                "REVIEW"
            )

            validated["validation_state"][
                "final_status"
            ] = "REVIEW"

        validated_topics.append(validated)

    return validated_topics


def save_index(
    topics: list[dict],
    output_path: str,
) -> None:
    """
    Save the Topic Index as formatted JSON.
    """
    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            topics,
            f,
            indent=2,
            ensure_ascii=False,
        )