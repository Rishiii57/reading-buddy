"""Content library: poems and passages split into stanzas, lines and words."""
import json
from dataclasses import dataclass, field
from pathlib import Path

from .normalize import loose, norm

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
LANGUAGES = {"gu-IN": "ગુજરાતી", "en-IN": "English", "hi-IN": "हिन्दी"}

# Short function words: skipping one of these alone is forgiven.
_SHORT_WORDS = {
    "a", "an", "the", "of", "to", "and", "in", "on", "is", "it", "its", "at",
    "है", "हैं", "के", "की", "का", "को", "से", "में", "पर", "और", "भी",
    "છે", "ને", "માં", "તે", "એ", "પર", "ના", "ની", "નો",
}


@dataclass
class Word:
    idx: int
    display: str
    norm: str
    loose: str
    line: int
    stanza: int
    aliases: frozenset = frozenset()  # forms the speech model writes for this word when read correctly
    line_start: bool = False
    line_end: bool = False
    stanza_end: bool = False

    @property
    def short(self) -> bool:
        return self.norm in _SHORT_WORDS or len(self.loose) <= 1


@dataclass
class Text:
    id: str
    language: str
    title: str
    title_en: str
    type: str
    grade: str
    lines: list[str]
    words: list[Word] = field(default_factory=list)
    line_words: list[tuple[int, int]] = field(default_factory=list)  # [start, end) per line

    def line_range(self, line: int) -> tuple[int, int]:
        return self.line_words[line]

    def public(self) -> dict:
        return {
            "id": self.id, "language": self.language, "title": self.title,
            "title_en": self.title_en, "type": self.type, "grade": self.grade,
            "words": [{"i": w.idx, "t": w.display, "line": w.line, "stanza": w.stanza,
                       "line_end": w.line_end, "stanza_end": w.stanza_end} for w in self.words],
        }


def build_text(spec: dict) -> Text:
    text = Text(id=spec["id"], language=spec["language"], title=spec["title"],
                title_en=spec.get("title_en", spec["title"]), type=spec["type"],
                grade=spec["grade"], lines=[])
    line_no = 0
    for s_idx, stanza in enumerate(spec["stanzas"]):
        for line in stanza:
            text.lines.append(line)
            start = len(text.words)
            for raw in line.split():
                n = norm(raw)
                if not n:  # stray punctuation such as a separate danda
                    if text.words and text.words[-1].line == line_no:
                        text.words[-1].display += " " + raw
                    continue
                text.words.append(Word(len(text.words), raw, n, loose(n), line_no, s_idx))
            end = len(text.words)
            text.words[start].line_start = True
            text.words[end - 1].line_end = True
            text.line_words.append((start, end))
            line_no += 1
        text.words[-1].stanza_end = True
    return text


def load_library() -> dict[str, Text]:
    library = {}
    alias_file = CONTENT_DIR / "stt_aliases.json"
    aliases = json.loads(alias_file.read_text(encoding="utf-8")) if alias_file.exists() else {}
    for lang in LANGUAGES:
        for spec in json.loads((CONTENT_DIR / f"{lang}.json").read_text(encoding="utf-8")):
            text = build_text(spec)
            known = aliases.get(text.id, {})
            for w in text.words:
                if w.norm in known:
                    w.aliases = frozenset(known[w.norm])
            library[spec["id"]] = text
    return library
