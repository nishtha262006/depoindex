# DepoIndex — AI-Powered Deposition Topic Index

DepoIndex is an AI-assisted system that converts a deposition transcript into a structured and verifiable Topic Index.

Each generated topic is associated with:

- Exact transcript page and line coordinates
- Transcript evidence
- Topic summary
- Semantic validation information
- Validation status
- Validation provenance and audit information

The system is designed to keep AI-generated results traceable to the source transcript and to fail closed when required validation cannot be established.

---

## Challenge

**AI/LLM Engineer Internship Program 2026–2027**

**Challenge:** DepoIndex — AI-Powered Deposition Topic Index

---

## Features

### Transcript Processing

- Extracts deposition text from PDF.
- Preserves transcript page and line coordinates.
- Splits testimony into deterministic transcript segments.
- Audits transcript extraction for parsing and ordering issues.

### AI Topic Generation

- Uses a local Llama 3.2 3B model for topic classification.
- Generates a topic, summary, and transcript evidence for each segment.
- Preserves uncertainty rather than intentionally inventing unsupported information.

### Metadata and Speaker Context

- Extracts available deposition metadata.
- Records metadata source and extraction confidence.
- Separates static deposition metadata from transcript-level speaker context.
- Records unresolved speaker context when local transcript evidence is insufficient.

### Validation

The system uses four validation levels:

1. **Extraction**
2. **Provenance**
3. **Semantic**
4. **Boundary**

A topic is considered `TRUSTED` only when the required validation conditions pass.

Otherwise, it remains in `REVIEW`.

### Deterministic Transcript Support

Before semantic validation, the system checks whether the proposed evidence and topic are grounded in the actual transcript segment.

This prevents semantic model agreement from being the only source of evidence.

### Semantic Validation

The semantic validation stage evaluates:

- Transcript support
- Topic relevance
- Topic specificity
- Semantic support
- Semantic confidence

The deterministic transcript-support check and semantic validation are treated as separate stages.

### Revalidation

Validated topics receive a validation fingerprint.

If validation-relevant fields change later, the stored validation becomes stale.

The validation pipeline can invalidate downstream validation levels and require them to be re-established.

### Fail-Closed Recovery

Validation failures are not silently converted into successful results.

Fallback actions record:

- Original validation state
- Recovery action
- Whether data changed
- Whether the fallback became more permissive
- Whether revalidation is required

A more-permissive fallback is rejected.

### LLM Failure Handling

LLM failures are handled conservatively.

- Classification failure produces an unresolved topic state.
- Semantic validation failure leaves the topic in `REVIEW`.
- Failed LLM stages cannot produce a trusted result.

### Semantic Boundary Analysis

The project includes an experimental semantic boundary module.

A proposed boundary requires:

- `NEW_TOPIC`
- Sufficient confidence
- A non-empty explanation
- Improved segmentation-quality measurement

The experimental boundary system is not currently used to automatically replace the production fixed-size segmentation.

---

## Architecture

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
   TRUSTED                REVIEW
      |
      v
Validated Topic Index
Validation Pipeline
Level 1 — Extraction

Checks the quality of transcript extraction, including:

Parsed records
Unparsed lines
Duplicate coordinates
Ordering issues
Line gaps
Level 2 — Provenance

Checks whether:

Page/line coordinates are valid.
Evidence is grounded in the corresponding transcript segment.
The generated topic has traceable transcript evidence.
Level 3 — Semantic

Checks whether the topic is meaningfully supported by the transcript segment.

The semantic stage is combined with deterministic transcript-support validation.

Level 4 — Boundary

Records the status of semantic boundary handling.

The current production pipeline does not automatically apply experimental semantic boundary changes.

Validation Freshness

The project uses validation fingerprints to prevent stale validation.

A fingerprint is generated from validation-relevant topic fields.

If these fields are changed after validation, the stored fingerprint no longer matches the current topic.

The result is therefore treated as requiring revalidation.

When an upstream validation level changes, downstream validation levels can also be invalidated.

Metadata Provenance

Metadata is represented using structured fields containing:

value
source
confidence

The implementation does not infer missing metadata.

For speaker context, the system distinguishes between:

Explicitly resolved speaker information
Unresolved speaker context

This prevents deposition-level metadata from automatically being treated as speaker identity at every transcript position.

Fail-Closed Design

The system follows a fail-closed approach.

If a required validation stage fails:

Failure
   |
   v
REVIEW
   |
   v
Recovery / Audit
   |
   v
Revalidation
   |
   v
TRUSTED only if all required checks pass

A fallback is not treated as successful validation.

Semantic Validation Independence

The semantic verifier currently uses the same Llama 3.2 3B model family used for topic generation.

Therefore, it is not claimed to be independent ground truth.

The project instead separates:

Deterministic transcript grounding.
Semantic model validation.

A stronger independent model, external API, or human-annotated validation set would be required for stronger semantic independence.

This is documented as a limitation and future improvement.

Experimental Features

The following functionality is implemented but should be considered experimental:

Semantic Boundary Detection

The system can propose internal topic boundaries using semantic classification.

Boundary acceptance requires:

NEW_TOPIC
Confidence threshold
Explanation
Improved segmentation-quality measurement

However, the production validated-index pipeline currently retains the deterministic fixed-size segments.

Boundary Calibration

A large manually labeled dataset for measuring false splits and missed transitions has not yet been established.

Testing

The current automated test suite contains:

72 tests
72 passed

The latest test run:

72 passed in 22.25s

Tests cover:

Transcript parsing
Parser auditing
Metadata extraction
Metadata provenance
Speaker context
Deterministic transcript support
Semantic validation
Semantic disagreement
Evidence mismatch
Boundary handling
Segmentation quality
Validation state
Validation fingerprints
Downstream invalidation
Fallback behavior
Recovery behavior
LLM classification failure
LLM semantic-validation failure
End-to-End Evaluation

The deposition used for evaluation is:

data/Persis_Yu_Deposition.pdf

The final end-to-end results are recorded after the final generation run.

The evaluation includes:

Number of generated topics
Trusted/review status
Provenance validation
Transcript page coverage
Multi-run stability
Boundary-transition analysis
Manual review results

Final numerical results are maintained in the project report.

Limitations
Fixed-Size Chunking

The production pipeline continues to use fixed-size transcript chunks.

Semantic boundary detection is implemented separately as an experimental capability.

Local Model

The project uses a local Llama 3.2 3B model. Smaller local models may produce incorrect topic labels, summaries, or semantic judgments.

Semantic Independence

The semantic verifier is not independent ground truth because it uses the same model family as topic generation.

Boundary Calibration

A large human-labeled boundary dataset has not yet been used to calibrate false-split and missed-transition rates.

Speaker Attribution

When local transcript evidence is insufficient to identify a speaker, the system records the speaker context as unresolved instead of making an unsupported inference.

PDF Extraction

The quality of the final index depends partly on the quality of the source PDF extraction.

Future Work

Potential future improvements include:

Calibrated semantic segmentation instead of fixed-size chunking.
A manually labeled boundary evaluation dataset.
False-split and missed-transition measurement.
Validation using a stronger independent model.
Human review workflows for unresolved topics.
Improved speaker attribution.
Evaluation on additional deposition transcripts.
Human-annotated topic coverage evaluation.
Comparison of multiple models for semantic validation.
Live Demo

Public demo:

https://nishtha262006.github.io/depoindex/

The demo provides an interactive view of the generated Topic Index, including topic labels, page/line provenance, evidence, and provenance validation results.

Running Locally

Create and activate the virtual environment, then install the project dependencies.

Start the application with:

uvicorn app.main:app --reload

The application can then be accessed through the local FastAPI server.

Project Structure
depoindex/
│
├── app/
│   ├── indexer.py
│   ├── llm.py
│   ├── metadata.py
│   ├── models.py
│   ├── recovery.py
│   ├── semantic_boundary.py
│   ├── speaker_context.py
│   ├── transcript.py
│   ├── validation_pipeline.py
│   ├── validation_state.py
│   └── ...
│
├── data/
│   └── Persis_Yu_Deposition.pdf
│
├── tests/
│   ├── test_indexer.py
│   ├── test_metadata.py
│   ├── test_validation.py
│   ├── test_fallback.py
│   └── ...
│
├── docs/
│   ├── DepoIndex_Report.md
│   └── reviewer_response.md
│
└── README.md
Status
Implemented
Transcript extraction
Parser audit
Metadata provenance
Speaker-context tracking
Deterministic transcript-support validation
Semantic validation
Four-level validation
Validation fingerprints
Downstream invalidation
Fail-closed recovery
Fallback audit trail
LLM failure handling
Automated validation tests
Experimental
Semantic boundary detection
Semantic boundary calibration
Independent stronger-model semantic verification
Author

Nishtha Wadaskar

B.Tech Computer Science
VIT Bhopal University