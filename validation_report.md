# DepoIndex — Validation Report

## 1. Evaluation Methodology

The DepoIndex pipeline was evaluated using deterministic provenance checks, a manual review of 20 Topic Index entries, semantic boundary analysis, and a three-run stability test on the same deposition transcript.

### Manual review

Twenty Topic Index entries were reviewed against the original deposition transcript using five criteria:

1. **Location accuracy** — whether the cited page/line range points to the correct transcript content.
2. **Topic relevance** — whether the topic label accurately describes the testimony in the segment.
3. **Boundary quality** — whether the start and end locations align with reasonable semantic topic boundaries.
4. **Coverage** — whether the segment captures the substantive discussion represented by its topic.
5. **Redundancy** — whether the entry unnecessarily duplicates another topic.

### Automated provenance validation

For every generated entry, the system programmatically checks that:

- the start location does not occur after the end location;
- the specified page/line range maps to transcript text; and
- the selected evidence appears in the cited transcript range after text normalization.

The LLM is not trusted to determine provenance.

### Stability test

The complete pipeline was run three times on the same deposition using the local `llama3.2:3b` model through Ollama with temperature 0. The runs were compared for topic-label stability and page/line boundary stability.

### Boundary analysis

A separate semantic boundary audit classified each transition between adjacent deterministic chunks as `SAME_TOPIC` or `NEW_TOPIC`. The audit was used for analysis and did not automatically modify the final provenance ranges.

---

## 2. Final Topic Index Results

- **Topic segments generated:** 26
- **Source testimony range:** transcript pages 7–88
- **Deterministic provenance validation:** 26/26 PASS (100%)

The final Topic Index is available in both JSON and human-readable Markdown formats.

---

## 3. Manual Review Results

| Criterion | Result |
|---|---:|
| Location accuracy | 20/20 PASS (100%) |
| Topic relevance | 19/20 PASS (95%) |
| Boundary quality | 10/20 PASS (50%) |
| Coverage | 19/20 PASS (95%) |
| Redundancy | 20/20 PASS (100%) |

The main weakness identified by manual review was semantic boundary quality. Several fixed-size chunks began or ended in the middle of a discussion or near a reporter interruption.

---

## 4. Three-Run Stability Results

The stability test processed 26 deterministic chunks three times, producing 78 local LLM calls.

- **Stable chunks:** 24/26
- **Topic-label stability:** 92.31%
- **Boundary stability:** 100%

The two unstable labels were minor lexical variations that referred to the same general subject.

### Unstable Case 1 — Chunk 24

Observed labels:

- Run 1: `Servicer Regulation and Enforcement`
- Run 2: `Servicer Responsibilities and Loan Enforcement`
- Run 3: `Servicer Responsibilities and Loan Enforcement`

The variation changes wording but not the general subject.

### Unstable Case 2 — Chunk 26

Observed labels:

- Run 1: `PEAKS loans program`
- Run 2: `PEAKS loans program servicing issues`
- Run 3: `PEAKS loans program servicing issues`

Again, the variation is primarily lexical and remains within the same general topic.

---

## 5. Failure / Difficult-Case Analysis

### Failure Case 1 — Topic 7 Boundary

**What the system produced:** The segment begins during discussion of report paragraph numbering before the substantive discussion of for-profit colleges begins.

**What it should have produced:** The segment should begin at the natural transition into the discussion of for-profit colleges.

**Why it failed:** The current pipeline uses deterministic fixed-size chunks rather than semantic topic boundaries. A chunk can therefore start or end inside a related but different discussion.

**How to improve it:** Add semantic boundary detection that evaluates topic continuity around candidate boundaries before finalizing segment start and end locations.

### Failure Case 2 — Topic 10 Boundary

**What the system produced:** The segment continues material from the preceding topic and ends near a reporter interruption instead of a clean semantic endpoint.

**What it should have produced:** The segment should begin when the discussion shifts specifically to evidence of misrepresentation in education financing and end when that discussion naturally concludes.

**Why it failed:** Fixed-size chunking does not account for question/answer structure, interruptions, or semantic transitions.

**How to improve it:** Use a boundary classifier together with transcript structure to move boundaries to nearby semantic transition points while preserving exact page/line provenance.

### Failure Case 3 — Topic 20 Relevance and Boundary

**What the system produced:** The segment is labeled around the CFPB and SEC investigations into the Vervent defendants, but the segment begins with CFPB findings and only later reaches the SEC-related material. The manual review marked relevance, boundary quality, and coverage as failures for this entry.

**What it should have produced:** The topic label and segment should represent the complete substantive discussion covered by the range, or the range should be split at the semantic transition into the SEC-related discussion.

**Why it failed:** A single deterministic chunk can contain multiple closely related investigation subjects, making a concise topic label insufficiently representative of the entire segment.

**How to improve it:** Detect meaningful topic transitions within chunks and split or relabel segments based on semantic coherence, while retaining programmatically verified provenance.

---

## 6. Boundary Analysis

The separate boundary audit evaluated 25 transitions between adjacent chunks:

- **SAME_TOPIC:** 23
- **NEW_TOPIC:** 2

The two substantive transitions identified were:

1. `ITT Educational Services Settlement and Government Loans` → `ITT Student Loan Practices`
2. `Investigations into ITT and PEAKS program` → `Servicer Regulation and Enforcement`

The boundary audit is currently diagnostic. It does not automatically change the final index, because automatic boundary changes could introduce unsupported provenance changes without further validation.

---

## 7. Limitations

- Fixed-size chunking does not always align with natural semantic topic boundaries.
- Evidence selection currently uses a simple fallback strategy and may not always be the most representative evidence for the assigned topic.
- The local `llama3.2:3b` model can produce minor lexical variation between runs.
- The current system does not assign confidence scores to topic quality or boundary decisions.

---

## 8. Future Improvements

1. Replace fixed-size chunking with semantic boundary detection.
2. Improve evidence selection using topic-representative transcript spans.
3. Add confidence and topic-quality scoring.
4. Use transcript question/answer structure and reporter interruptions as additional boundary signals.
5. Add richer transcript inspection and filtering to the web interface.
6. Add OCR fallback for scanned deposition PDFs.

---

## 9. Conclusion

The system successfully produces a reproducible, provenance-validated Topic Index and demonstrates strong location accuracy, topic relevance, coverage, and redundancy results. The primary limitation is semantic boundary quality, which is explicitly measured and documented rather than hidden. The evaluation therefore identifies a clear next engineering step: replacing fixed-size segmentation with semantically informed boundary detection while preserving deterministic provenance validation.
