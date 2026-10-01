import json
import re

import ollama

from app.fallback import create_fallback_audit


MODEL_NAME = "llama3.2:3b"


def get_fallback_evidence(chunk: list[dict]) -> str:
    """
    Select deterministic evidence directly from the transcript.

    Evidence is never generated or paraphrased by the LLM.
    """

    # Prefer an explicit witness answer.
    for record in chunk:
        text = record["text"].strip()

        if text.startswith("THE WITNESS:"):
            return text

    # Otherwise prefer an attorney statement.
    for record in chunk:
        text = record["text"].strip()

        if text.startswith("A    "):
            return text

    # Final fallback: first non-empty transcript line.
    for record in chunk:
        text = record["text"].strip()

        if text:
            return text

    return ""


def format_metadata_for_prompt(metadata: dict) -> str:
    """
    Format metadata while preserving value, source and confidence.

    Even when a metadata value is unavailable, its source/status
    is preserved so that the LLM does not infer missing information.
    """

    if not metadata:
        return "No metadata was explicitly identified."

    fields = []

    for key, value in metadata.items():

        if isinstance(value, dict):
            field_value = value.get("value")
            source = value.get("source", "Not identified")
            confidence = value.get("confidence", 0)

            display_value = (
                field_value
                if field_value
                else "Not identified"
            )

            fields.append(
                f"{key}: {display_value} "
                f"(source={source}, confidence={confidence})"
            )

        else:
            fields.append(
                f"{key}: {value}"
            )

    if not fields:
        return "No metadata was explicitly identified."

    return "\n".join(fields)


def classify_chunk(
    chunk: list[dict],
    metadata: dict | None = None,
) -> dict:
    """
    Classify one transcript chunk.

    The LLM generates only the topic and summary.

    Evidence is selected deterministically from the original
    transcript so that provenance can be independently verified.
    """

    transcript_text = "\n".join(
        record["text"]
        for record in chunk
    )

    metadata_text = format_metadata_for_prompt(
        metadata or {}
    )

    prompt = f"""
You are classifying a section of a legal deposition transcript.

Identify the main topic discussed in this transcript section
and provide a short factual summary.

Deposition metadata:
{metadata_text}

Transcript section:
{transcript_text}

Rules:
1. Identify the main topic actually discussed.
2. Keep the topic specific and concise.
3. The summary must be factual and grounded only in the transcript.
4. Do not invent facts.
5. Do not infer information that is not stated.
6. Do not provide evidence.
7. Do not provide page numbers or line numbers.
8. Do not include additional commentary.

Return JSON only:

{{
  "topic": "short specific topic title",
  "summary": "short factual summary"
}}
"""

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            format="json",
        )

        content = response["message"]["content"]
        data = json.loads(content)

    except Exception as exc:
        return {
            "topic": "",
            "summary": "",
            "evidence": get_fallback_evidence(chunk),
            "error": f"LLM classification failed: {exc}",
        }

    return {
        "topic": str(
            data.get("topic", "")
        ).strip(),

        "summary": str(
            data.get("summary", "")
        ).strip(),

        # Evidence MUST come from the transcript.
        "evidence": get_fallback_evidence(chunk),
    }


def verify_topic_semantics(
    chunk: list[dict],
    topic: str,
    summary: str,
) -> dict:
    """
    Verify topic and summary against the transcript.

    The returned structure preserves the existing validation API.
    """

    transcript_text = "\n".join(
        record["text"]
        for record in chunk
    )

    prompt = f"""
You are validating a topic classification for a legal deposition.

Transcript:
{transcript_text}

Generated topic:
{topic}

Generated summary:
{summary}

Evaluate the following:

1. semantic_supported:
   Is the topic and summary supported by the transcript?

2. transcript_supported:
   Does the transcript directly support the claims?

3. topic_relevant:
   Is the topic relevant to the transcript section?

4. topic_specific:
   Is the topic specific enough to describe the section?

5. semantic_score:
   Give a score from 0 to 100.

Return JSON only:

{{
  "semantic_supported": true,
  "transcript_supported": true,
  "topic_relevant": true,
  "topic_specific": true,
  "semantic_score": 90,
  "semantic_reason": "short factual reason"
}}

Rules:
- Use only the supplied transcript.
- Do not use outside knowledge.
- Do not infer facts not present.
- A broad or vague topic should receive topic_specific=false.
- A topic unrelated to the transcript should receive topic_relevant=false.
- A topic should only be supported when the transcript actually discusses
  the subject described by the topic.
- Short evidence such as "Yes", "Okay", or "I'm sorry" may still be valid
  provenance evidence, but it is not by itself sufficient to establish
  semantic support for the topic.
"""

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            format="json",
        )

        content = response["message"]["content"]
        data = json.loads(content)

    except Exception as exc:
        return {
            "semantic_supported": False,
            "transcript_supported": False,
            "topic_relevant": False,
            "topic_specific": False,
            "semantic_score": 0,
            "semantic_reason": (
                f"Semantic validation failed: {exc}"
            ),

            "supported": False,
        }

    semantic_supported = bool(
        data.get(
            "semantic_supported",
            data.get("supported", False),
        )
    )

    transcript_supported = bool(
        data.get(
            "transcript_supported",
            semantic_supported,
        )
    )

    topic_relevant = bool(
        data.get(
            "topic_relevant",
            semantic_supported,
        )
    )

    topic_specific = bool(
        data.get(
            "topic_specific",
            semantic_supported,
        )
    )

    try:
        semantic_score = int(
            data.get("semantic_score", 0)
        )
    except (TypeError, ValueError):
        semantic_score = 0

    semantic_score = max(
        0,
        min(100, semantic_score),
    )

    reason = str(
        data.get("semantic_reason", "")
    ).strip()

    if not reason:
        reason = (
            "No semantic validation reason was provided."
        )

    return {
        "semantic_supported": semantic_supported,
        "transcript_supported": transcript_supported,
        "topic_relevant": topic_relevant,
        "topic_specific": topic_specific,
        "semantic_score": semantic_score,
        "semantic_reason": reason,
        "supported": semantic_supported,
    }


def _normalize_text(text: str) -> str:
    """
    Normalize text for deterministic evidence comparison.
    """

    text = text.replace("-\n", "")
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


def _token_overlap(
    evidence: str,
    transcript_text: str,
) -> float:
    """
    Calculate how much of the evidence is represented
    in the transcript.

    This is used only as a transcript-support sanity check.
    Exact provenance remains the responsibility of validator.py.
    """

    evidence_words = re.findall(
        r"\b[a-z0-9]+\b",
        _normalize_text(evidence),
    )

    transcript_words = set(
        re.findall(
            r"\b[a-z0-9]+\b",
            _normalize_text(transcript_text),
        )
    )

    if not evidence_words:
        return 0.0

    matches = sum(
        word in transcript_words
        for word in evidence_words
    )

    return matches / len(evidence_words)


def _topic_is_obviously_unrelated(
    topic: str,
    transcript_text: str,
) -> bool:
    """
    Detect an obviously unrelated topic without requiring
    general topic/evidence word overlap.

    This is intentionally conservative.

    It only rejects a topic when there is clear lexical evidence
    that the topic belongs to a completely different subject area.

    Normal semantic relevance remains the responsibility of the
    semantic verifier.
    """

    topic_words = set(
        re.findall(
            r"\b[a-z0-9]+\b",
            _normalize_text(topic),
        )
    )

    transcript_words = set(
        re.findall(
            r"\b[a-z0-9]+\b",
            _normalize_text(transcript_text),
        )
    )

    if not topic_words or not transcript_words:
        return False

    # Terms that strongly indicate a distinct subject domain.
    domain_groups = [
        {
            "cryptocurrency",
            "crypto",
            "bitcoin",
            "ethereum",
            "blockchain",
            "trading",
        },
        {
            "football",
            "soccer",
            "basketball",
            "baseball",
            "tennis",
        },
        {
            "cooking",
            "recipe",
            "restaurant",
            "cuisine",
        },
        {
            "weather",
            "forecast",
            "temperature",
            "hurricane",
        },
        {
            "stock",
            "stocks",
            "equity",
            "equities",
            "trading",
            "forex",
        },
    ]

    for group in domain_groups:
        topic_domain_terms = topic_words & group

        if not topic_domain_terms:
            continue

        transcript_domain_terms = transcript_words & group

        if not transcript_domain_terms:
            return True

    return False


def verify_topic_transcript_support(
    chunk: list[dict],
    topic: str,
    evidence: str,
) -> dict:
    """
    Verify whether evidence is supported by the transcript.

    This function performs deterministic transcript-support checks.

    Semantic topic relevance is handled separately by
    verify_topic_semantics(), except for an intentionally conservative
    obvious-unrelated-topic guard used to fail closed on clearly
    incompatible subject domains.

    Exact page/line provenance is independently checked by validator.py.
    """

    transcript_text = "\n".join(
        record["text"]
        for record in chunk
    )

    # Missing evidence must always fail closed.
    if not evidence or not evidence.strip():
        return {
            "supported": False,
            "reason": "Evidence is empty.",
        }

    # Clearly unrelated domain should fail closed.
    if _topic_is_obviously_unrelated(
        topic,
        transcript_text,
    ):
        return {
            "supported": False,
            "reason": (
                "The supplied topic is obviously unrelated "
                "to the transcript subject."
            ),
        }

    normalized_evidence = _normalize_text(evidence)
    normalized_transcript = _normalize_text(
        transcript_text
    )

    # Exact normalized match.
    if (
        normalized_evidence
        and normalized_evidence in normalized_transcript
    ):
        return {
            "supported": True,
            "reason": (
                "Evidence occurs in the transcript."
            ),
        }

    # Token overlap allows minor PDF extraction differences.
    overlap = _token_overlap(
        evidence,
        transcript_text,
    )

    if overlap >= 0.80:
        return {
            "supported": True,
            "reason": (
                "Evidence is substantially supported "
                "by the transcript."
            ),
        }

    # Use the LLM only when deterministic matching is inconclusive.
    prompt = f"""
You are validating evidence for a legal deposition topic.

Transcript:
{transcript_text}

Topic:
{topic}

Evidence:
{evidence}

Determine whether the evidence is actually supported by the transcript.

Return JSON only:

{{
  "supported": true,
  "reason": "short factual reason"
}}

Rules:
- supported=true only when the transcript supports the evidence.
- Do not invent facts.
- Do not rewrite the evidence.
- Do not use outside knowledge.
- Do not decide topic relevance solely from the topic wording.
- Topic relevance is evaluated by a separate semantic validator.
"""

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            format="json",
        )

        content = response["message"]["content"]
        data = json.loads(content)

    except Exception:
        return {
            "supported": False,
            "reason": (
                "Deterministic transcript support failed "
                "and semantic verification was unavailable."
            ),
        }

    return {
        "supported": bool(
            data.get("supported", False)
        ),
        "reason": str(
            data.get("reason", "")
        ).strip()
        or "No transcript support reason was provided.",
    }


def combine_semantic_validation(
    support: dict,
    semantic: dict,
) -> dict:
    """
    Combine transcript-support and semantic validation.

    SUPPORTED requires:
    - transcript support
    - semantic_supported
    - transcript_supported
    - topic_relevant
    - topic_specific
    - semantic score >= 70
    """

    support_passed = bool(
        support.get("supported", False)
    )

    semantic_supported = bool(
        semantic.get(
            "semantic_supported",
            semantic.get("supported", False),
        )
    )

    transcript_supported = bool(
        semantic.get(
            "transcript_supported",
            semantic_supported,
        )
    )

    topic_relevant = bool(
        semantic.get(
            "topic_relevant",
            semantic_supported,
        )
    )

    topic_specific = bool(
        semantic.get(
            "topic_specific",
            semantic_supported,
        )
    )

    try:
        semantic_score = int(
            semantic.get("semantic_score", 0)
        )
    except (TypeError, ValueError):
        semantic_score = 0

    all_checks_pass = (
        support_passed
        and semantic_supported
        and transcript_supported
        and topic_relevant
        and topic_specific
        and semantic_score >= 70
    )

    if all_checks_pass:
        status = "SUPPORTED"
    else:
        status = "REVIEW"

    reasons = []

    if not support_passed:
        reasons.append(
            "Deterministic transcript support failed."
        )

    if not semantic_supported:
        reasons.append(
            "Semantic verifier did not confirm the topic."
        )

    if not transcript_supported:
        reasons.append(
            "Semantic verifier did not confirm transcript support."
        )

    if not topic_relevant:
        reasons.append(
            "Semantic verifier found the topic insufficiently relevant."
        )

    if not topic_specific:
        reasons.append(
            "Semantic verifier found the topic insufficiently specific."
        )

    if semantic_score < 70:
        reasons.append(
            f"Semantic score {semantic_score} is below the 70 threshold."
        )

    if not reasons:
        reasons.append(
            "Topic and evidence passed semantic validation."
        )

    return {
        "status": status,
        "supported": all_checks_pass,

        "semantic_supported": semantic_supported,
        "transcript_supported": transcript_supported,
        "topic_relevant": topic_relevant,
        "topic_specific": topic_specific,
        "semantic_score": semantic_score,

        "reason": " ".join(reasons),
    }