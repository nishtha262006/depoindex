from app.transcript import build_transcript


def chunk_transcript(
    pdf_path: str,
    chunk_size: int = 80,
) -> list[list[dict]]:
    """
    Split the structured transcript into ordered chunks.

    Each chunk contains complete transcript records, so every
    piece of text keeps its original page and line provenance.

    chunk_size is the maximum number of transcript records
    in each chunk.
    """

    transcript = build_transcript(pdf_path)

    chunks = []

    for start in range(0, len(transcript), chunk_size):
        chunk = transcript[start:start + chunk_size]
        chunks.append(chunk)

    return chunks