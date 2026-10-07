from pathlib import Path

from zip_ds.parsers.document_extractor import ExtractionResult, read_docx, read_pdf, read_txt


def extract_document(path: str, root: str) -> ExtractionResult:
    """Extract a supported document after authorized-root validation."""
    suffix = Path(path).suffix.casefold()
    readers = {".txt": read_txt, ".pdf": read_pdf, ".docx": read_docx}
    reader = readers.get(suffix)
    if reader is None:
        raise ValueError("unsupported document type; expected .txt, .pdf, or .docx")
    return reader(path, root)
