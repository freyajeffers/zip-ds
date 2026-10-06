import re
import unicodedata

from pydantic import BaseModel, ConfigDict, Field, model_validator


class NormalizedText(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    text: str
    offsets: list[tuple[int, int]] = Field(min_length=0)

    @model_validator(mode="after")
    def validate_offsets(self) -> NormalizedText:
        if len(self.offsets) != len(self.text):
            raise ValueError("one source offset pair is required per normalized character")
        for start, end in self.offsets:
            if start < 0 or end <= start:
                raise ValueError("offsets must be non-negative and ordered")
        return self


def normalize_text(text: str) -> NormalizedText:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    chars = []
    offsets = []
    for idx, ch in enumerate(text):
        if unicodedata.category(ch).startswith("C") and ch not in "\n\t":
            continue
        normalized = unicodedata.normalize("NFKC", ch)
        chars.append(normalized)
        offsets.append((idx, idx + 1))
    return NormalizedText(text="".join(chars), offsets=offsets)


def isolate_bibliography(text: str) -> tuple[str, str]:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    match = re.search(r"(?im)^\s*(references|bibliography|works cited)\s*$", text)
    if not match:
        return text, ""
    return text[: match.start()].rstrip(), text[match.start() :].lstrip()
