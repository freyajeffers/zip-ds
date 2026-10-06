import re
import unicodedata
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class NormalizedText:
    text: str
    offsets: List[Tuple[int, int]]


def normalize_text(text: str) -> NormalizedText:
    chars = []
    offsets = []
    for idx, ch in enumerate(text):
        if unicodedata.category(ch).startswith("C") and ch not in "\n\t":
            continue
        normalized = unicodedata.normalize("NFKC", ch)
        chars.append(normalized)
        offsets.append((idx, idx + 1))
    return NormalizedText("".join(chars), offsets)


def isolate_bibliography(text: str) -> Tuple[str, str]:
    match = re.search(r"(?im)^\s*(references|bibliography|works cited)\s*$", text)
    if not match:
        return text, ""
    return text[:match.start()].rstrip(), text[match.start():].lstrip()
