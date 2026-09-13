# LLM Usage

## Model

DepoIndex uses the locally hosted `llama3.2:3b` model through Ollama.

The model was selected because it can run locally without requiring an external API key or sending the deposition transcript to a third-party hosted LLM service.

## Where the LLM is used

The LLM is used in:

- `app/llm.py`
- `app/indexer.py`
- `app/baseline.py`
- `app/stability.py`
- `app/boundary.py`

The primary LLM task is to classify each transcript segment into a concise descriptive topic label and generate a short summary.

## Prompting approach

Each transcript chunk is provided to the model with page and line provenance:

`[Page X, Line Y] transcript text`

The model is instructed to:

1. Identify the main topic discussed.
2. Use only information present in the transcript.
3. Avoid inventing facts.
4. Return structured JSON.
5. Keep the topic label concise.
6. Avoid generating page or line numbers itself.

Page and line provenance is determined programmatically from the source transcript rather than being trusted from the LLM.

## Evidence and validation

The system performs provenance validation after LLM classification.

The validator checks that:

- The start position occurs before the end position.
- The specified page/line range contains transcript text.
- Evidence is present.
- The evidence can be matched against the transcript text within the specified range.

This separates LLM-based semantic classification from deterministic provenance verification.

## Boundary analysis

A separate LLM-based boundary analysis is used to classify transitions between adjacent transcript chunks as either:

- `SAME_TOPIC`
- `NEW_TOPIC`

The boundary analysis is treated as a semantic audit rather than as authoritative provenance generation.

## Stability testing

The same 26 transcript chunks were processed three times using:

- Model: `llama3.2:3b`
- Temperature: `0`

This produced 78 LLM calls.

Results are recorded in:

`data/stability_results.json`

and summarized in:

`data/stability_report.md`

The observed topic-label stability was 92.31% (24 of 26 chunks stable across all three runs).

The two unstable labels were minor wording variations referring to the same general subjects.

## Limitations

The current implementation uses deterministic fixed-size transcript chunks.

This makes page/line boundaries reproducible, but fixed-size chunks do not guarantee that every semantic topic begins and ends exactly at a natural conversational transition.

The project therefore includes a separate boundary-transition analysis and a manual review of 20 entries.
