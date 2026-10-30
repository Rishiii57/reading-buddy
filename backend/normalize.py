"""Text normalisation and fuzzy word similarity for English, Hindi and Gujarati.

Two keys per word:
  norm  - script-level cleanup (case, punctuation, nukta, chandrabindu, digits)
  loose - also collapses vowel length and nasal marks, so small spelling or
          script differences from the speech model still count as a match.
"""
import re
import unicodedata

from rapidfuzz.distance import Levenshtein

_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
         "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
         "seventeen", "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def _num_to_words(n: int) -> str:
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else _ONES[n % 10])
    if n < 1000:
        rest = n % 100
        return _ONES[n // 100] + "hundred" + ("" if rest == 0 else _num_to_words(rest))
    return str(n)


# Devanagari and Gujarati digits -> ASCII
_DIGITS = {ord(c): str(i) for i, c in enumerate("०१२३४५६७८९")}
_DIGITS.update({ord(c): str(i) for i, c in enumerate("૦૧૨૩૪૫૬૭૮૯")})

_NORM_MAP = {
    "़": "", "઼": "",          # nukta
    "ँ": "ं", "ઁ": "ં",  # chandrabindu -> anusvara
    "‌": "", "‍": "",          # ZWNJ / ZWJ
}
_LOOSE_MAP = {
    # Devanagari: long vowels -> short, drop nasal/visarga/virama
    "ी": "ि", "ू": "ु", "ई": "इ", "ऊ": "उ",
    "ै": "े", "ौ": "ो", "ऐ": "ए", "औ": "ओ",
    "ं": "", "ः": "", "्": "", "ॅ": "े", "ॉ": "ो",
    # Gujarati: same idea
    "ી": "િ", "ૂ": "ુ", "ઈ": "ઇ", "ઊ": "ઉ",
    "ૈ": "ે", "ૌ": "ો", "ઐ": "એ", "ઔ": "ઓ",
    "ં": "", "ઃ": "", "્": "", "ૅ": "ે", "ૉ": "ો",
}
_NORM_TABLE = str.maketrans(_NORM_MAP)
_LOOSE_TABLE = str.maketrans(_LOOSE_MAP)

# Fillers the child (or the speech model) may produce; never treated as reading.
FILLERS = {
    "um", "umm", "ummm", "uh", "uhh", "hmm", "hm", "mm", "ah", "aa", "aaa", "er", "erm",
    "अ", "आ", "अं", "हम्म", "हम", "उम्म", "अम्म", "ऊं",
    "અ", "આ", "હમ્મ", "ઉમ્મ", "અં",
}


def norm(word: str) -> str:
    w = unicodedata.normalize("NFD", word)
    w = w.translate(_NORM_TABLE)
    w = unicodedata.normalize("NFC", w).lower()
    w = w.translate(_DIGITS)
    w = w.replace("'", "").replace("’", "")
    # keep letters, marks and digits only
    w = "".join(ch for ch in w if unicodedata.category(ch)[0] in ("L", "M", "N"))
    if w.isdigit():
        w = _num_to_words(int(w))
    return w


def loose(word_norm: str) -> str:
    w = word_norm.translate(_LOOSE_TABLE)
    # English: collapse doubled letters ("pitter" ~ "piter")
    return re.sub(r"([a-z])\1+", r"\1", w)


def tokenize(text: str) -> list[str]:
    """Split a transcript into normalised tokens, dropping fillers and empties."""
    out = []
    for raw in text.split():
        n = norm(raw)
        if n and n not in FILLERS:
            out.append(n)
    return out


def similarity(a_norm: str, b_norm: str) -> float:
    """0..1 similarity between two normalised words (1.0 = same)."""
    if a_norm == b_norm:
        return 1.0
    la, lb = loose(a_norm), loose(b_norm)
    if la == lb:
        return 0.95
    if not la or not lb:
        return 0.0
    sim = Levenshtein.normalized_similarity(la, lb)
    # same stem, different ending ("walk"/"walked", "પડે"/"પડ્યો"): a small slip, let it go
    shorter = min(len(la), len(lb))
    common = 0
    while common < shorter and la[common] == lb[common]:
        common += 1
    if shorter >= 4 and common >= 2 and common >= 0.6 * shorter:  # not for tiny words: "tak" is not "tall"
        sim = max(sim, 0.72)
    return sim
