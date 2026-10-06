import os

import pdfplumber
from docx import Document


def _validated_path(path: str) -> str:
    if not isinstance(path, str) or not path:
        raise TypeError("path must be a non-empty string")
    return path


def read_txt(path: str) -> tuple[str, list[tuple[int, int]]]:
    path = _validated_path(path)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    # naive single chunk covering the whole file
    return text, [(0, len(text))]


def read_pdf(path: str) -> tuple[str, list[tuple[int, int]]]:
    path = _validated_path(path)
    with pdfplumber.open(path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    text = "\n".join(pages)
    return text, [(0, len(text))]


def read_docx(path: str) -> tuple[str, list[tuple[int, int]]]:
    path = _validated_path(path)
    doc = Document(path)
    paras = [p.text for p in doc.paragraphs]
    text = "\n".join(paras)
    return text, [(0, len(text))]


def canonicalize_and_validate(path: str, root: str) -> str:
    real = os.path.realpath(path)
    root_real = os.path.realpath(root)
    try:
        inside_root = os.path.commonpath([real, root_real]) == root_real
    except ValueError as exc:
        raise ValueError("Path escapes authorized root") from exc
    if not inside_root:
        raise ValueError("Path escapes authorized root")
    return real
