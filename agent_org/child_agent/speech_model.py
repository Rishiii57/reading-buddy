"""What a simulated child says when reading, and what the speech model writes down for it.

Two separate stages, so every report can tell a child's reading mistake apart from a speech-
recognition mistake:

  1. read_attempt(): the child's own reading of a stretch of text. Skips, substitutions
     (letter confusions, first-letter guesses, dropped endings, matra/nasal errors), repeats,
     self-corrections and thinking pauses, driven by the persona. Ground truth per word.
  2. stt_channel(): what Prisma would plausibly write for that speech. Words lost to low
     volume and a per-language error rate.

Stage 2 is a coarse model, not a measurement. The base error rates are Prisma's measured
clean-speech WER on synthetic adult voices (eval/RESULTS.md: en 1.4 %, gu 7.3 %, hi 0 %),
plus an ASSUMED extra for young children's voices. Real child-speech accuracy is unknown
until consenting recordings are tested (see the audio evaluation docs).
"""
import random
import re
from dataclasses import dataclass, field

BASE_STT_WER = {"en-IN": 0.014, "gu-IN": 0.073, "hi-IN": 0.01}
YOUNG_VOICE_EXTRA = 0.05  # assumption for ages under 6; unmeasured

_PUNCT = ".,!?;:।\"'“”‘’—-"

# confusable pairs (both directions)
_EN_LETTER = [("b", "d"), ("p", "q"), ("m", "n"), ("s", "z"), ("t", "d"), ("f", "v"), ("w", "v")]
_HI_LETTER = [("ब", "व"), ("श", "स"), ("ष", "स"), ("ड", "ढ"), ("ट", "ठ"), ("द", "ध"), ("ज", "झ"), ("त", "थ"), ("न", "ण"), ("र", "ड़")]
_GU_LETTER = [("બ", "વ"), ("શ", "સ"), ("ષ", "સ"), ("ડ", "ઢ"), ("ટ", "ઠ"), ("દ", "ધ"), ("જ", "ઝ"), ("ત", "થ"), ("ન", "ણ"), ("ર", "ડ")]
_HI_MATRA = [("ि", "ी"), ("ु", "ू"), ("े", "ै"), ("ो", "ौ"), ("ा", "")]
_GU_MATRA = [("િ", "ી"), ("ુ", "ૂ"), ("ે", "ૈ"), ("ો", "ૌ"), ("ા", "")]
_EN_GUESS = {  # common words a child substitutes when guessing from the first letter
    "a": ["and", "at", "all"], "b": ["big", "ball", "bed"], "c": ["cat", "can", "come"],
    "d": ["dog", "day", "down"], "f": ["fish", "fun", "for"], "g": ["go", "good", "get"],
    "h": ["have", "he", "here"], "i": ["in", "is", "it"], "k": ["kit", "king"],
    "l": ["look", "like", "little"], "m": ["me", "mum", "my"], "o": ["on", "of", "one"],
    "p": ["play", "put", "pig"], "r": ["run", "red", "ran"], "s": ["see", "sun", "said"],
    "t": ["the", "to", "tree"], "w": ["was", "we", "went"],
}


def clean(w: str) -> str:
    return w.strip(_PUNCT)


def is_small(w: str) -> bool:
    c = clean(w).lower()
    return c in {"a", "an", "the", "of", "to", "and", "in", "on", "is", "it", "its", "at", "by",
                 "है", "हैं", "के", "की", "का", "को", "से", "में", "पर", "और", "भी", "ने",
                 "છે", "ને", "માં", "તે", "એ", "પર", "ના", "ની", "નો", "ના"} or len(c) <= 2


@dataclass
class WordAttempt:
    idx: int
    target: str
    said: str | None       # None = skipped
    correct: bool
    kind: str              # ok | sub | skip | self_corrected | echo
    extra: list = field(default_factory=list)  # repeated / inserted words said after it


@dataclass
class Segment:
    """One stretch of continuous speech, then a pause."""
    text: str
    duration_s: float
    pause_after_s: float
    words: list            # WordAttempt idxs covered


def _swap(word: str, pairs, rng) -> str | None:
    opts = [(a, b) for a, b in pairs if a in word] + [(b, a) for a, b in pairs if b and b in word]
    if not opts:
        return None
    a, b = rng.choice(opts)
    return word.replace(a, b, 1)


def mispronounce(word: str, lang: str, mistakes: list, rng: random.Random) -> str:
    """A plausible wrong reading of `word` for this child."""
    w = clean(word)
    cands = []
    if lang == "en-IN":
        lw = w.lower()
        if "letter_confusion" in mistakes:
            s = _swap(lw, _EN_LETTER, rng)
            if s and s != lw:
                cands.append(s)
        if "guesses_from_first_letter" in mistakes and lw[:1] in _EN_GUESS:
            g = [x for x in _EN_GUESS[lw[:1]] if x != lw]
            if g:
                cands.append(rng.choice(g))
        if "drops_endings" in mistakes and len(lw) > 3:
            cands.append(re.sub(r"(s|es|ed|ing|e|y)$", "", lw) if re.search(r"(s|es|ed|ing|e|y)$", lw) else lw[:-1])
        if not cands:
            cands.append(rng.choice(_EN_GUESS.get(lw[:1], ["um"])) if len(lw) > 3 else lw[:-1] + "a")
    else:
        letters = _HI_LETTER if lang == "hi-IN" else _GU_LETTER
        matras = _HI_MATRA if lang == "hi-IN" else _GU_MATRA
        if "letter_confusion" in mistakes or "guesses_from_first_letter" in mistakes:
            s = _swap(w, letters, rng)
            if s and s != w:
                cands.append(s)
        if "matra_errors" in mistakes:
            s = _swap(w, matras, rng)
            if s and s != w:
                cands.append(s)
        if "nasal_errors" in mistakes:
            if "ं" in w or "ં" in w:
                cands.append(w.replace("ं", "").replace("ં", ""))
        if "conjunct_errors" in mistakes and ("्" in w or "્" in w):
            cands.append(w.replace("्", "", 1).replace("્", "", 1))
        if "drops_endings" in mistakes and len(w) > 3:
            cands.append(w[:-1])
        if not cands:
            s = _swap(w, letters, rng) or _swap(w, matras, rng)
            cands.append(s if s and s != w else w[: max(1, len(w) - 1)])
    out = rng.choice(cands)
    return out if out and out != w.lower() and out != w else (w[:-1] or w)


def read_attempt(words: list[tuple[int, str]], lang: str, persona, rng: random.Random,
                 heard_recently: set[str], max_words: int | None = None,
                 allow_hesitation: bool = True) -> tuple[list[WordAttempt], list[Segment], int]:
    """The child tries to read `words` [(idx, display)] aloud.

    Returns (attempts, segments, reached) where reached = how many of `words` the child got
    through before stopping (a pre-reader stops at the first word they have not just heard)."""
    b = persona.behaviour
    read_skill = persona.reads(lang)
    lang_comfort = 0.5 + 0.5 * persona.speaks(lang)
    attempts: list[WordAttempt] = []
    for k, (i, disp) in enumerate(words):
        if max_words is not None and k >= max_words:
            break
        w = clean(disp)
        heard = w.lower() in heard_recently
        if heard:
            p_ok = max(b.echo_skill, b.word_accuracy * read_skill)
        elif b.can_decode and read_skill > 0.05:
            difficulty = 1.0 - min(0.35, 0.03 * max(0, len(w) - 4))  # longer words are harder
            p_ok = b.word_accuracy * (0.55 + 0.45 * read_skill) * difficulty * lang_comfort
        else:
            break  # cannot read this word at all: the child stops here
        if is_small(disp) and rng.random() < b.p_skip_small:
            attempts.append(WordAttempt(i, w, None, False, "skip"))
            continue
        if rng.random() < p_ok * persona.pronunciation.get("accuracy", 1.0) ** 0.3:
            a = WordAttempt(i, w, w, True, "echo" if heard and not b.can_decode else "ok")
        else:
            wrong = mispronounce(w, lang, persona.common_mistakes, rng)
            if rng.random() < b.p_self_correct:
                a = WordAttempt(i, w, f"{wrong} {w}", True, "self_corrected")
            else:
                a = WordAttempt(i, w, wrong, False, "sub")
        if rng.random() < b.p_repeat_word:
            a.extra.append(a.said or w)
        attempts.append(a)
    reached = len(attempts)

    # segment into speech with thinking pauses
    segments: list[Segment] = []
    cur: list[WordAttempt] = []
    hesitate_at = None
    if allow_hesitation and len(attempts) >= 2 and rng.random() < b.p_hesitate:
        hesitate_at = rng.randint(1, len(attempts) - 1)
    if "word_by_word" in persona.common_mistakes and allow_hesitation:
        gaps = {k for k in range(1, len(attempts)) if rng.random() < 0.6}
    else:
        gaps = set()
    for k, a in enumerate(attempts):
        if (k == hesitate_at or k in gaps) and cur:
            lo, hi = b.hesitation_s
            segments.append(_segment(cur, b, rng.uniform(lo, hi)))
            cur = []
        cur.append(a)
    if cur:
        segments.append(_segment(cur, b, 0.0))
    return attempts, segments, reached


def _segment(attempts: list[WordAttempt], b, pause: float) -> Segment:
    toks = []
    for a in attempts:
        if a.said:
            toks.append(a.said)
        toks += a.extra
    n = max(1, len(" ".join(toks).split()))
    return Segment(" ".join(toks), round(n / b.words_per_s + 0.2, 2), round(pause, 2), [a.idx for a in attempts])


def stt_channel(text: str, lang: str, persona, rng: random.Random) -> tuple[str, list[str]]:
    """What the speech model would write for `text`. Returns (heard, notes)."""
    notes = []
    wer = BASE_STT_WER.get(lang, 0.03) + (YOUNG_VOICE_EXTRA if persona.age < 6 else 0.0)
    wer += 0.3 * max(0.0, 0.8 - persona.behaviour.volume)  # quiet or whispered speech
    out = []
    for w in text.split():
        r = rng.random()
        if r < wer * 0.4:
            notes.append(f"lost '{w}'")
            continue
        if r < wer:
            pairs = {"en-IN": _EN_LETTER, "hi-IN": _HI_LETTER, "gu-IN": _GU_LETTER}[lang]
            s = _swap(w.lower() if lang == "en-IN" else w, pairs, rng)
            if s:
                notes.append(f"'{w}' heard as '{s}'")
                out.append(s)
                continue
        out.append(w)
    return " ".join(out), notes
