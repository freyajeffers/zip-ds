import os

import pdfplumber
from docx import Document
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    text: str
    offsets: list[tuple[int, int]] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_offsets(self) -> ExtractionResult:
        if len(self.offsets) != 1:
            raise ValueError("the extractor must return one complete-document offset span")
        start, end = self.offsets[0]
        if start != 0 or end != len(self.text):
            raise ValueError("extraction offsets must span the complete returned text")
        return self


def canonicalize_and_validate(path: str, root: str) -> str:
    if not isinstance(path, str) or not isinstance(root, str):
        raise TypeError("path and root must be strings")
    if not path or not root:
        raise ValueError("path and root must be non-empty")
    real = os.path.realpath(path)
    root_real = os.path.realpath(root)
    try:
        inside_root = os.path.commonpath([real, root_real]) == root_real
    except ValueError as exc:
        raise ValueError("Path escapes authorized root") from exc
    if not inside_root:
        raise ValueError("Path escapes authorized root")
    return real


def _validated_path(path: str, root: str) -> str:
    return canonicalize_and_validate(path, root)


def _result(text: str) -> ExtractionResult:
    return ExtractionResult(text=text, offsets=[(0, len(text))])


def read_txt(path: str, root: str) -> ExtractionResult:
    path = _validated_path(path, root)
    with open(path, "r", encoding="utf-8") as f:
        return _result(f.read())


def read_pdf(path: str, root: str) -> ExtractionResult:
    path = _validated_path(path, root)
    with pdfplumber.open(path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return _result(text)


def read_docx(path: str, root: str) -> ExtractionResult:
    path = _validated_path(path, root)
    doc = Document(path)
    return _result("\n".join(paragraph.text for paragraph in doc.paragraphs))
