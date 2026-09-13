# DepoIndex — AI-Powered Deposition Topic Index

DepoIndex is an AI-assisted system that converts a deposition transcript into a verifiable Topic Index. Each topic is associated with an exact page/line range and evidence that can be checked against the source transcript.

## Challenge

AI/LLM Engineer Internship Program 2026–2027

Challenge: DepoIndex — AI-Powered Deposition Topic Index

## Features

- Extracts deposition text from PDF.
- Preserves transcript page and line provenance.
- Splits testimony into deterministic transcript segments.
- Uses a local LLM to classify the main topic of each segment.
- Generates a structured JSON Topic Index.
- Generates a human-readable Markdown Topic Index.
- Validates page/line ranges and evidence programmatically.
- Performs semantic boundary-transition analysis.
- Includes a 20-entry manual review.
- Performs a three-run LLM stability test.

## Architecture

Deposition PDF
  -> PDF Extraction
  -> Transcript + Page/Line Provenance
  -> Deterministic Chunking
  -> Local LLM Topic Classification
  -> Provenance Validation
  -> JSON + Markdown Topic Index

Boundary analysis runs as a separate semantic audit of transitions between adjacent chunks.

## Project Structure

```text
depoindex/
|-- app/
|   |-- extractor.py
|   |-- transcript.py
|   |-- provenance.py
|   |-- chunker.py
|   |-- llm.py
|   |-- indexer.py
|   |-- validator.py
|   |-- models.py
|   |-- output.py
|   |-- baseline.py
|   |-- boundary.py
|   |-- stability.py
|   `-- review and analysis scripts
|
|-- data/
|   |-- Persis_Yu_Deposition.pdf
|   |-- final_topic_index.json
|   |-- final_topic_index.md
|   |-- manual_review.json
|   |-- stability_results.json
|   |-- stability_report.md
|   |-- boundary_analysis.json
|   |-- boundary_report.md
|   `-- baseline_topics.json
|
|-- tests/
|   |-- test_transcript.py
|   `-- test_models.py
|
|-- llm_usage.md
|-- requirements.txt
|-- .gitignore
`-- README.md
```

## Setup

### 1. Create and activate the virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Install and start Ollama

Install Ollama and make sure it is running.

Pull the model:

```powershell
ollama pull llama3.2:3b
```

## Generate the Topic Index

From the project root:

```powershell
python -m app.generate_index
```

This generates:

- data/final_topic_index.json
- data/final_topic_index.md

## Validation

Run the automated test suite:

```powershell
python -m pytest -q
```

The tests verify transcript extraction, page/line boundaries, provenance lookup, model serialization, and provenance validation.

## Evaluation Results

### Final Topic Index

- 26 topic segments generated.
- All 26 topic segments passed deterministic provenance validation.
- Source testimony range: transcript pages 7–88.

### Manual Review

A manual review of 20 Topic Index entries was performed using five criteria:

1. Location accuracy
2. Topic relevance
3. Boundary quality
4. Coverage
5. Redundancy

Results:

- Location accuracy: 20/20 PASS (100%)
- Topic relevance: 19/20 PASS (95%)
- Boundary quality: 10/20 PASS (50%)
- Coverage: 19/20 PASS (95%)
- Redundancy: 20/20 PASS (100%)

The boundary-quality failures are documented rather than hidden. The main limitation is that the current segmentation uses deterministic fixed-size chunks, so some segment boundaries do not perfectly match natural semantic transitions.

### Three-Run Stability

The 26 chunks were processed three times using llama3.2:3b with temperature 0, resulting in 78 LLM calls.

- Stable chunks: 24/26
- Topic-label stability: 92.31%
- Boundary stability: 100%

The two unstable labels were minor wording variations referring to the same general subjects.

## Output Format

Each Topic Index entry contains:

- topic
- start_page
- start_line
- end_page
- end_line
- evidence
- provenance_valid
- validation_reason

Page and line provenance is generated programmatically and then validated against the transcript.

## Design Decisions

### Local LLM

The system uses Ollama with llama3.2:3b so the deposition can be processed locally without requiring an external LLM API.

### Deterministic provenance

Page and line locations are extracted from the PDF and assigned programmatically. The LLM is not trusted to invent or determine provenance.

### Separate validation

Semantic classification and provenance validation are intentionally separated. The LLM identifies the topic, while deterministic code verifies that the cited range and evidence exist in the transcript.

### Boundary audit

A separate LLM boundary analysis classifies transitions as SAME_TOPIC or NEW_TOPIC. It is used as a semantic audit rather than automatically changing the final provenance ranges.

## Limitations and Future Improvements

- Replace fixed-size chunking with semantic boundary detection.
- Improve evidence selection so evidence is more representative of the assigned topic.
- Add confidence scores and topic-quality checks.
- Add an interactive web interface for searching and inspecting Topic Index entries.
- Support additional deposition formats and OCR fallback for scanned PDFs.

## LLM Disclosure

See llm_usage.md for model selection, prompting, validation, boundary analysis, stability testing, and limitations.

## License

This project was created as an internship challenge submission.
