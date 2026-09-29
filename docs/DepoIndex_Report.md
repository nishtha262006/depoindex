# DepoIndex — AI-Powered Deposition Topic Index

## 1. Abstract

DepoIndex is an AI-assisted system for automatically organizing deposition transcripts into meaningful topic segments. The system extracts deposition text from PDF documents, divides the transcript into manageable segments, generates topic labels and summaries, selects transcript evidence, and validates the resulting topic index.

Following the reviewer feedback, the system was extended with parser auditing, metadata provenance, speaker-context tracking, four-level validation, deterministic transcript-support checks, semantic validation, validation fingerprinting, downstream revalidation, fail-closed recovery, and validation fallback auditing.

The objective of these changes is to make the generated topic index more traceable, auditable, and resistant to invalid or stale validation results.

## 2. Introduction

Deposition transcripts contain large amounts of testimony that may cover multiple subjects, events, organizations, and investigations. Manually indexing such transcripts is time-consuming and can result in inconsistent topic boundaries and evidence selection.

DepoIndex uses a local language model together with deterministic validation mechanisms to generate a structured topic index from a deposition transcript.

The system is designed so that an AI-generated topic is not automatically treated as trusted output. Instead, the generated result passes through multiple validation levels before it can receive a trusted status.

## 3. Problem Statement

The initial version of DepoIndex had several limitations:

- Transcript parsing did not provide a complete extraction audit.
- Metadata did not explicitly record provenance and confidence.
- Speaker context was not represented separately from deposition-level metadata.
- Semantic validation relied on the same language model used for topic generation.
- Validation could become stale if validated fields were changed later.
- Boundary proposals did not have explicit acceptance and quality criteria.
- Recovery and fallback behavior required stronger fail-closed handling.
- The system needed clearer distinction between trusted, review, and fallback states.

These limitations motivated the validation and auditability improvements implemented in the revised system.

## 4. Objectives

The main objectives of the revised system are:

1. Audit transcript extraction before trusting downstream processing.
2. Record metadata values together with their source and confidence.
3. Track speaker context without making unsupported speaker identity assumptions.
4. Separate deterministic transcript grounding from semantic verification.
5. Require multiple validation levels before assigning trusted status.
6. Invalidate downstream validation when an upstream validated field changes.
7. Record fallback and recovery actions explicitly.
8. Ensure failures remain fail-closed rather than becoming more permissive.
9. Evaluate semantic boundary proposals using explicit acceptance criteria.
10. Provide tests covering validation and failure modes.

## 5. Original System and Weaknesses

The original implementation used fixed-size transcript chunking and language-model-based topic generation.

The baseline system produced topic segments from transcript chunks and performed provenance and semantic checks. However, several parts of the pipeline required stronger guarantees.

### 5.1 Fixed-size chunking

The transcript was divided into fixed-size chunks. This provides predictable processing but does not guarantee that every chunk corresponds to a natural semantic topic.

### 5.2 Limited parser auditing

The parser extracted transcript records but did not provide a complete structured audit of issues such as unparsed lines, duplicate coordinates, ordering problems, or line gaps.

### 5.3 Limited metadata provenance

Metadata values were extracted without consistently exposing where each field came from or how confident the extraction was.

### 5.4 Validation staleness

A topic could be validated and later modified. Without an explicit validation fingerprint, it was difficult to determine whether the stored validation still applied to the current topic contents.

### 5.5 Semantic validation independence

The semantic verifier uses the same local Llama 3.2 3B model family as the topic-generation stage. Therefore, it should not be treated as an independent ground-truth source.

The revised design adds deterministic transcript grounding and separates semantic validation as a distinct stage, but a genuinely independent stronger-model or human-grounded comparison remains future work.

## 6. Proposed Improvements

### 6.1 Parser Audit

The transcript parser now records an extraction audit containing information such as:

- Pages processed
- Raw transcript lines
- Successfully parsed lines
- Unparsed lines
- Ignored formatting lines
- Duplicate coordinates
- Ordering issues
- Line gaps
- Speaker-context resolution status

The extraction audit is evaluated before the topic index can receive a trusted status.

### 6.2 Metadata Provenance

Metadata fields are represented using structured values containing:

- Value
- Source
- Confidence

The implementation avoids inferring missing metadata.

### 6.3 Speaker Context

Speaker context is maintained separately from static deposition metadata.

When an explicit speaker marker is available, the speaker can be represented with high confidence.

When the transcript position does not provide sufficient information to identify a speaker, the system records an unresolved speaker context rather than guessing.

### 6.4 Four-Level Validation

The revised pipeline contains four validation levels:

1. Extraction
2. Provenance
3. Semantic
4. Boundary

A topic can receive `TRUSTED` status only when the required validation levels pass and the fallback audit does not prevent trust.

Otherwise, the topic remains in `REVIEW`.

### 6.5 Deterministic Transcript Support

Before semantic verification, the system performs deterministic transcript-support validation.

The deterministic check verifies that:

- Evidence is present in the transcript segment.
- Evidence has meaningful lexical overlap with the transcript.
- The proposed topic has meaningful support from the evidence.
- The evidence is not simply unrelated text.

If deterministic support fails, the semantic verifier is not required to run and the topic remains in review.

### 6.6 Semantic Validation

The semantic verifier evaluates whether the generated topic is actually supported by the transcript segment.

The verifier considers:

- Transcript support
- Topic relevance
- Topic specificity
- Semantic support
- Semantic confidence score

The system combines the semantic result with deterministic transcript support.

#### Independence limitation

The semantic verifier currently uses Llama 3.2 3B, the same model family used for topic generation.

Therefore, the semantic verifier is not fully independent ground truth.

A stronger independent model, external API, or human-annotated validation set would be required to establish stronger semantic independence. This remains a future improvement rather than an implemented claim.

### 6.7 Boundary Detection

A semantic boundary module was implemented to experimentally evaluate whether a chunk contains an internal topic transition.

A proposed boundary is considered for acceptance only when:

- The semantic classifier identifies `NEW_TOPIC`.
- The confidence meets the configured threshold.
- A non-empty explanation is provided.
- The resulting segmentation demonstrates an improvement in the segmentation-quality metric.

The production validated-index pipeline currently retains the fixed validated segments rather than automatically applying experimental semantic boundary splits.

Therefore, semantic boundary detection is implemented as an experimental capability and is not presented as a fully calibrated production segmentation system.

### 6.8 Fail-Closed Recovery

Validation failures are represented explicitly rather than being silently converted into successful output.

The fallback system records:

- Validation level
- Original failure state
- Recovery action
- Whether data changed
- Whether the fallback became more permissive
- Whether revalidation is required

A fallback that would make validation more permissive is rejected.

When a repair changes validated information, downstream validation levels are invalidated and must be re-established.

### 6.9 Revalidation

Each validated topic receives a validation fingerprint based on its validation-relevant fields.

If those fields change after validation, the stored fingerprint no longer matches the current topic.

The system can therefore detect stale validation.

Downstream validation levels are also invalidated when an upstream validation stage changes.

## 7. System Architecture

The processing pipeline can be summarized as:

```text
Deposition PDF
      |
      v
Transcript Extraction
      |
      v
Parser Audit
      |
      v
Transcript Chunking
      |
      v
Metadata Extraction
      |
      v
Topic Classification
      |
      v
Deterministic Transcript Support
      |
      v
Semantic Validation
      |
      v
Four-Level Validation
      |
      +----------------------+
      |                      |
      v                      v
Trusted                  Review
      |
      v
Validated Topic Index

The experimental boundary pipeline is evaluated separately:

Transcript Chunk
      |
      v
Boundary Proposal
      |
      v
NEW_TOPIC + Confidence
      |
      v
Segmentation Quality
      |
      v
Experimental Boundary Decision
8. Implementation
8.1 Transcript Extraction

The transcript parser processes the relevant deposition pages and converts transcript lines into structured records containing page, line, and text information.

The parser audit records extraction problems instead of silently ignoring them.

8.2 Metadata Layer

Metadata is represented using structured fields containing provenance and confidence information.

The current extractor avoids inventing values when the source document does not explicitly provide the required information.

8.3 Validation State

Each topic maintains a validation state containing the four validation levels:

extraction
provenance
semantic
boundary

Each level can contain states such as:

PASS
REVIEW

The overall topic status is derived from these validation states.

8.4 Validation Fingerprinting

Validation-relevant topic fields are serialized deterministically and hashed.

The resulting fingerprint is stored when validation occurs.

A later modification changes the fingerprint and causes the stored validation to become stale.

8.5 Recovery and Fallback

The recovery system preserves the original validation failure and records the recovery action.

The design intentionally avoids treating fallback as automatic success.

If a recovery changes validated content, revalidation is required before the result can become trusted.

8.6 LLM Failure Handling

Language-model failures are treated as validation failures.

Classification failure produces an unresolved topic state rather than fabricated topic information.

Semantic-verifier failure results in a review state rather than allowing the topic to pass semantic validation.

These behaviors are covered by automated tests.

9. Testing and Failure Modes

The current automated test suite contains 72 tests.

The latest test run completed successfully:

72 passed in 22.25s

The tests cover:

Transcript parsing
Parser audit
Metadata extraction
Metadata provenance
Speaker context
Semantic validation
Deterministic transcript support
Semantic disagreement
Topic/evidence mismatch
Boundary proposal handling
Segmentation quality
Validation state
Validation fingerprints
Downstream invalidation
Fallback auditing
Recovery behavior
LLM classification failure
LLM semantic-validation failure
10. End-to-End Results

This section will be completed after the final end-to-end generation finishes.

Final Index
Number of generated topics: TBD
Trusted topics: TBD
Review topics: TBD
Provenance-valid topics: TBD
Pages covered: TBD
Stability
Number of chunks: TBD
Number of repeated runs: TBD
Stable chunks: TBD
Stability percentage: TBD
Boundary Analysis
Number of analyzed transitions: TBD
SAME_TOPIC transitions: TBD
NEW_TOPIC transitions: TBD
Accepted experimental boundaries: TBD

These values will be populated from the final end-to-end run rather than estimated from intermediate runs.

11. Before/After Comparison
Original weakness	Implemented change	Evidence
Validation could become stale after changes	Validation fingerprints and downstream invalidation	Validation tests
Metadata provenance was not explicit	Metadata fields include source and confidence	Metadata tests
Speaker identity could be inferred incorrectly	Separate speaker-context state with unresolved handling	Speaker-context implementation
Transcript support depended heavily on model judgment	Deterministic transcript-support validation	Semantic validation tests
Semantic validation needed clearer separation	Separate semantic verification stage	Semantic tests
Boundary proposals lacked explicit acceptance rules	Confidence, NEW_TOPIC, explanation and quality checks	Boundary tests
Fallback behavior needed stronger guarantees	Fail-closed fallback audit	Fallback/recovery tests
LLM failures needed explicit handling	Classification and semantic failures remain review states	LLM failure tests
Parser issues were not fully auditable	Structured extraction audit	Parser audit tests
12. Limitations
12.1 Fixed-size chunking

The production pipeline continues to use fixed-size transcript chunking. Semantic boundary detection is implemented experimentally but is not automatically replacing the production chunking strategy.

12.2 Model limitations

The local Llama 3.2 3B model is relatively small and may produce incorrect topic labels, summaries, or semantic judgments.

12.3 Semantic independence

The semantic verifier uses the same model family as topic generation. Therefore, the verifier is not independent ground truth.

A stronger model, external model, or human-annotated evaluation set would provide stronger validation independence.

12.4 Boundary calibration

The semantic boundary system has explicit acceptance criteria, but a large manually labeled boundary evaluation dataset has not yet been used to calibrate false-split and missed-transition rates.

12.5 Speaker information

The current transcript parser does not consistently expose explicit speaker markers at every transcript position. When speaker identity cannot be established, the system records an unresolved state rather than making an unsupported inference.

12.6 PDF extraction

The quality of the final index remains dependent on the quality of the source PDF extraction.

13. Future Work

Potential future improvements include:

Replacing fixed-size chunking with calibrated semantic segmentation.
Building a manually labeled boundary evaluation dataset.
Measuring false-positive and false-negative boundary rates.
Comparing semantic validation against a stronger independent model.
Adding human review workflows for unresolved topics.
Improving speaker attribution when transcript speaker markers are available.
Adding larger-scale deposition evaluation.
Measuring topic coverage and segmentation quality against human annotations.
Evaluating multiple language models for semantic validation independence.
14. Conclusion

The revised DepoIndex implementation introduces stronger validation, provenance, auditability, and failure-handling mechanisms.

The system now separates extraction, provenance, semantic, and boundary validation and prevents invalid or stale validation states from being treated as trusted output.

The implementation also explicitly records metadata provenance, unresolved speaker context, fallback actions, and language-model failures.

Semantic boundary detection has been implemented as an experimental capability with explicit acceptance and quality criteria, while the production pipeline remains conservative and does not automatically apply experimental boundary changes.

The remaining limitations, particularly semantic-model independence and boundary calibration, are explicitly identified rather than presented as solved problems.