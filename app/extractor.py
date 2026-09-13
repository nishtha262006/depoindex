from pathlib import Path
from pypdf import PdfReader


def extract_deposition(pdf_path: str) -> list[dict]:
    """
    Extract text from a deposition PDF page by page.

    Returns a list of dictionaries containing:
    - PDF page number
    - extracted text
    - individual lines
    """

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(path))

    pages = []

    for pdf_page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        lines = text.splitlines()

        pages.append(
            {
                "pdf_page": pdf_page_number,
                "text": text,
                "lines": lines,
            }
        )

    return pages