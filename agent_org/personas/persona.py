"""Child persona model: the 14 profile fields from the spec, plus the behaviour parameters
the simulation actually uses. Personas are synthetic testing profiles, never real children.

Every behavioural number is stated explicitly in library.json (no hidden defaults beyond the
ones below), so two personas that differ only in name are impossible to miss in review.
"""
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

LIBRARY = Path(__file__).with_name("library.json")

GRADES = ["Nursery", "LKG", "UKG", "Class 1", "Class 2", "Class 3", "Class 4"]
PRE_PRIMARY = {"Nursery", "LKG", "UKG"}
LANGS = ["en-IN", "hi-IN", "gu-IN"]
PROFICIENCY = ["pre_reader", "emergent", "early", "developing", "fluent"]
MISTAKES = {
    "skips_small_words", "letter_confusion", "guesses_from_first_letter", "drops_endings",
    "matra_errors", "nasal_errors", "conjunct_errors", "repeats_words", "self_corrects",
    "reads_too_fast", "monotone", "loses_place", "word_by_word", "adds_words",
}


@dataclass
class Behaviour:
    """Numbers the simulator uses. 0..1 unless stated."""
    words_per_s: float            # reading speed while reading aloud
    word_accuracy: float          # chance a word they can read comes out right (own language)
    echo_skill: float             # chance of repeating a word correctly right after hearing it
    can_decode: bool              # can read words they have not just heard
    p_skip_small: float           # skips a small function word
    p_hesitate: float             # per line: stops mid-line to think
    hesitation_s: list            # [min, max] seconds of a thinking pause
    p_self_correct: float         # after a slip, says the right word straight away
    p_repeat_word: float          # repeats a word
    volume: float                 # 1 = clear; low values make the speech model lose words
    p_talk_over_buddy: float      # starts talking while Buddy is still talking
    p_off_task_click: float       # per decision step: taps something random
    p_tap_mic_to_talk: float      # taps the big mic again "to talk" (it toggles pause)
    says_tired_after_s: float     # says "I'm tired" after this long (0 = never)
    max_nav_clicks: int           # gives up finding the reading page after this many taps


@dataclass
class Persona:
    id: str
    name: str                     # synthetic first name, for readable reports only
    grade: str
    age: float
    reading_proficiency: str
    language_preference: str      # language they want to read in
    languages: dict               # code -> {"speak": 0..1, "read": 0..1}
    ui_english_reading: float     # can they read the app's English buttons and bubbles
    vocabulary_level: str
    pronunciation: dict           # {"accuracy": 0..1, "notes": "..."}
    attention_span_s: float
    confidence: float
    patience: float               # frustration points tolerated before giving up
    learning_preferences: list
    common_mistakes: list
    technology_familiarity: float
    interaction_style: str
    testing_objectives: list
    journey: str                  # the task this child is given (see child_agent.journeys)
    grown_up_setup: bool          # a grown-up already allowed the mic on this device
    behaviour: Behaviour
    profile_note: str = ""
    seed: int = 0
    tags: list = field(default_factory=list)

    @property
    def pre_primary(self) -> bool:
        return self.grade in PRE_PRIMARY

    def speaks(self, lang: str) -> float:
        return self.languages.get(lang, {}).get("speak", 0.0)

    def reads(self, lang: str) -> float:
        return self.languages.get(lang, {}).get("read", 0.0)

    def to_dict(self) -> dict:
        return asdict(self)

    def public_brief(self) -> str:
        """What the agent 'knows' about itself (no product knowledge)."""
        return (f"{self.name}, {self.grade} (about {self.age:g} years). Prefers {self.language_preference}. "
                f"{self.profile_note}")


def validate(p: Persona) -> list[str]:
    errs = []
    if p.grade not in GRADES:
        errs.append(f"{p.id}: bad grade {p.grade}")
    if p.reading_proficiency not in PROFICIENCY:
        errs.append(f"{p.id}: bad proficiency {p.reading_proficiency}")
    if p.language_preference not in LANGS:
        errs.append(f"{p.id}: bad language {p.language_preference}")
    for m in p.common_mistakes:
        if m not in MISTAKES:
            errs.append(f"{p.id}: unknown mistake {m}")
    if not (2.5 <= p.age <= 10.5):
        errs.append(f"{p.id}: age {p.age} outside Nursery-Class 4")
    b = p.behaviour
    if not b.can_decode and p.reading_proficiency not in ("pre_reader", "emergent"):
        errs.append(f"{p.id}: a {p.reading_proficiency} reader should be able to decode")
    return errs


def load(path: Path = LIBRARY) -> list[Persona]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for d in raw["personas"]:
        d = dict(d)
        d["behaviour"] = Behaviour(**d["behaviour"])
        out.append(Persona(**d))
    errs = [e for p in out for e in validate(p)]
    ids = [p.id for p in out]
    if len(ids) != len(set(ids)):
        errs.append("duplicate persona ids")
    if errs:
        raise ValueError("invalid persona library:\n" + "\n".join(errs))
    return out


def select(personas: list[Persona], ids: list[str] | None = None, n: int | None = None,
           grades: list[str] | None = None, langs: list[str] | None = None) -> list[Persona]:
    out = [p for p in personas if (not ids or p.id in ids) and (not grades or p.grade in grades)
           and (not langs or p.language_preference in langs)]
    if n is not None:
        out = _spread(out, n)
    return out


def _spread(ps: list[Persona], n: int) -> list[Persona]:
    """Pick n personas spread across grades and languages (round-robin), not the first n."""
    if n >= len(ps):
        return ps
    buckets: dict[tuple, list] = {}
    for p in ps:
        buckets.setdefault((p.grade, p.language_preference), []).append(p)
    keys = sorted(buckets, key=lambda k: (GRADES.index(k[0]), k[1]))
    out, i = [], 0
    while len(out) < n:
        k = keys[i % len(keys)]
        if buckets[k]:
            out.append(buckets[k].pop(0))
        i += 1
        if i > 10 * len(ps):
            break
    return out
