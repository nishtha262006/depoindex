# Response to Reviewer Feedback

Dear Reviewer,

Thank you for the detailed feedback on DepoIndex. I implemented the requested validation, provenance, auditability, and failure-handling improvements. The changes are summarized below.

## 1. Revalidation After Downstream Changes

### Weakness identified

A topic could become stale if information used during validation was modified after validation had already completed.

### Change implemented

DepoIndex now generates a validation fingerprint from validation-relevant topic fields.

The stored fingerprint is compared with the current topic state. If the topic changes after validation, the previous validation is no longer considered current.

The validation pipeline also supports downstream invalidation. When an upstream validation level changes, affected downstream levels return to `REVIEW` and must be validated again.

### Evidence

Automated tests cover validation fingerprints, validation state changes, and downstream invalidation.

## 2. Metadata Provenance and Speaker Context

### Weakness identified

Deposition-level metadata alone is not sufficient to establish who is speaking at every transcript position.

### Change implemented

Metadata fields now record:

- Value
- Source
- Extraction confidence

The system does not infer missing metadata.

Speaker context is represented separately from static deposition metadata.

When a speaker marker is unavailable at a transcript position, the system records the speaker context as unresolved instead of assigning a speaker based only on deposition-level information.

### Evidence

The metadata and speaker-context components are separately implemented and covered by automated tests.

## 3. Semantic Validation Independence

### Weakness identified

The semantic verifier should not be treated as independent ground truth when it uses the same model as topic generation.

### Change implemented

The validation pipeline separates two different checks:

1. Deterministic transcript-support validation.
2. Semantic validation.

The deterministic layer checks whether the proposed evidence is actually grounded in the transcript segment.

The semantic verifier separately evaluates transcript support, topic relevance, topic specificity, and semantic support.

A topic cannot become trusted solely because the language model agrees with its own generated topic.

### Important limitation

The current semantic verifier still uses Llama 3.2 3B, the same model family used for topic generation.

Therefore, this implementation does not claim full semantic independence.

A stronger independent model, external API, or human-annotated validation set would be needed to establish independent semantic ground truth.

This remains future work.

## 4. Boundary Proposal Acceptance

### Weakness identified

A proposed semantic boundary should not automatically be accepted simply because the model predicts a new topic.

### Change implemented

The experimental semantic-boundary module now requires multiple conditions before accepting a proposed boundary:

- The classifier must identify `NEW_TOPIC`.
- The confidence must meet the configured threshold.
- A reason must be provided.
- The resulting segmentation must demonstrate an improvement in the segmentation-quality metric.

### Production behavior

The production validated-index pipeline currently retains the fixed validated segments.

The semantic boundary system is therefore implemented as an experimental capability and is not presented as a fully calibrated production segmentation system.

### Remaining limitation

A large manually labeled boundary dataset has not yet been used to measure false splits and missed transitions.

This remains future work.

## 5. Fail-Closed Fallback and Audit Trail

### Weakness identified

Fallback behavior must not make validation more permissive or silently convert a failure into success.

### Change implemented

The fallback system records:

- Validation level
- Original validation status
- Recovery action
- Whether data changed
- Whether the fallback was more permissive
- Whether revalidation is required

Fallbacks that would make validation more permissive are rejected.

When a recovery changes validated information, downstream validation is invalidated and must be re-established.

The final validation state remains `REVIEW` when required validation has not been successfully completed.

## 6. Parser Audit

The transcript extraction pipeline now records an extraction audit including:

- Pages processed
- Raw lines
- Parsed lines
- Unparsed lines
- Ignored formatting lines
- Duplicate coordinates
- Ordering issues
- Line gaps
- Speaker-context resolution information

Extraction problems therefore become visible validation information instead of being silently ignored.

## 7. LLM Failure Handling

Language-model failures are now handled in a fail-closed manner.

If topic classification fails, the system does not fabricate a topic or evidence. Instead, the result is marked as unresolved and remains outside the trusted state.

If semantic validation fails, the topic remains in `REVIEW`.

Automated tests were added for both classification failure and semantic-verifier failure.

## 8. Four-Level Validation

The revised pipeline explicitly tracks four validation levels:

1. Extraction
2. Provenance
3. Semantic
4. Boundary

The final state is derived from these validation levels and the fallback audit.

A topic is not treated as `TRUSTED` when required validation has failed, remains unresolved, or has become stale.

## 9. Testing

The current automated test suite contains:

```text
72 passed in 6.56s

The tests cover:

Transcript parsing
Parser auditing
Metadata extraction
Metadata provenance
Speaker context
Deterministic transcript support
Semantic validation
Semantic disagreement
Boundary handling
Segmentation quality
Validation state
Validation fingerprinting
Downstream invalidation
Fallback behavior
Recovery behavior
LLM classification failure
LLM semantic-validation failure
10. End-to-End Evaluation Status

The previously generated end-to-end baseline contained:

26 generated topic segments
0 trusted topics
26 topics requiring review
1/26 provenance-valid topics

These values were produced before the final evidence-generation prompt was tightened to require verbatim contiguous transcript evidence.

They are therefore retained as a baseline diagnostic and are not presented as final measurements of the revised prompt behavior.

The final revised code was verified through the 72-test suite, but the full 26-segment Ollama generation was not rerun after that final prompt-only change.

This distinction is intentional: no revised end-to-end performance number is claimed without actually measuring it.

11. Before/After Summary
Area	Before	After	Evidence
Validation freshness	Validation could become stale after changes	Fingerprints detect stale validation and downstream levels can be invalidated	Validation tests
Metadata	Provenance was not explicit	Source and confidence are recorded	Metadata tests
Speaker context	Speaker information was not separately represented	Speaker context is tracked and unresolved when insufficient evidence exists	Speaker-context implementation/tests
Transcript grounding	Semantic judgment could be relied on too heavily	Deterministic transcript-support validation is required	Semantic/support tests
Semantic validation	Same-model validation could appear independent	Deterministic and semantic stages are separated; independence limitation is explicitly documented	Semantic validation implementation
Boundaries	Boundary acceptance criteria were limited	NEW_TOPIC, confidence, explanation, and quality checks are required	Boundary tests
Fallback	Recovery needed stronger fail-closed guarantees	Fallback actions and permissiveness are explicitly audited	Fallback/recovery tests
LLM failures	Failure behavior needed explicit handling	Classification and semantic failures remain fail-closed	LLM failure tests
Parser	Extraction issues were not fully audited	Structured parser audit added	Parser audit tests
12. Remaining Limitations

The following points are intentionally identified as limitations rather than presented as completed functionality:

The semantic verifier uses the same Llama 3.2 3B model family as topic generation.
A stronger independent semantic model or human-annotated ground-truth set has not yet been integrated.
Production segmentation still uses fixed-size chunking.
Semantic boundary detection remains experimental.
A large labeled dataset for boundary false-split and missed-transition calibration has not yet been created.
Speaker identity remains unresolved when the transcript does not provide sufficient local speaker information.
PDF extraction quality remains a dependency of the overall system.
13. Conclusion

The revised DepoIndex implementation addresses the requested validation and auditability concerns by introducing:

Parser auditing
Metadata provenance
Speaker-context handling
Four-level validation
Deterministic transcript grounding
Separate semantic verification
Validation fingerprints
Downstream invalidation
Fail-closed recovery
Fallback auditing
Explicit LLM failure handling
Experimental semantic boundary validation

The implementation distinguishes between functionality that is currently enforced in the production validation pipeline and functionality that remains experimental or requires additional independent evaluation.

Best regards,

Nishtha Wadaskar