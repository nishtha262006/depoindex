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

## Live Demo

Public demo:

https://nishtha262006.github.io/depoindex/

The demo provides an interactive view of the generated Topic Index, including topic labels, page/line provenance, evidence, and provenance validation results.

To run the application locally:

```powershell
uvicorn app.main:app --reload