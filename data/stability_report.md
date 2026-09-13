# DepoIndex — Three-Run Stability Report

## Test setup

- Runs: 3
- Chunks tested: 26
- Model: llama3.2:3b
- Temperature: 0

## Results

- Stable chunks: 24/26
- Topic-label stability: 92.31%
- Boundary stability: 100%

## Failure analysis

### Chunk 24

Observed labels across the three runs:

- Run 1: Servicer Regulation and Enforcement
- Run 2: Servicer Responsibilities and Loan Enforcement
- Run 3: Servicer Responsibilities and Loan Enforcement

Interpretation: the outputs describe the same general subject with minor wording variation. The instability is lexical rather than a major semantic topic change.

### Chunk 26

Observed labels across the three runs:

- Run 1: PEAKS loans program
- Run 2: PEAKS loans program servicing issues
- Run 3: PEAKS loans program servicing issues

Interpretation: the outputs describe the same general subject with minor wording variation. The instability is lexical rather than a major semantic topic change.

## Limitation

The current segmentation uses deterministic fixed-size transcript chunks. Therefore, page/line boundaries remain stable across runs, but semantic topic boundaries are not guaranteed to align with those fixed chunk boundaries.

This is reflected in the manual review, where several entries received boundary-quality failures.
