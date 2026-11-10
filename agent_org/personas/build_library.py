"""Builds library.json: 50 synthetic child personas (Nursery to Class 4).

Each grade has a behaviour template drawn from typical development at that age (pre-readers who
echo, emergent decoders, word-by-word early readers, developing and fluent readers). Every persona
then states what makes this child different: languages, reading level, mistakes, temperament,
technology habits and the task they are given. The table below is the single source of truth;
run `python -m agent_org.personas.build_library` to regenerate the JSON.

Distribution: Nursery 10, LKG 8, UKG 8, Class 1-4 6 each. Languages: English 17, Hindi 17, Gujarati 16.
"""
import json
from pathlib import Path

OUT = Path(__file__).with_name("library.json")

GRADE = {  # template: proficiency, age, ui_english_reading, attention, patience, technology, behaviour
    "Nursery": dict(prof="pre_reader", age=3.5, ui=0.0, attn=110, pat=3.0, tech=0.4,
                    b=dict(words_per_s=0.8, word_accuracy=0.0, echo_skill=0.5, can_decode=False, p_skip_small=0.4,
                           p_hesitate=0.6, hesitation_s=[2.0, 5.0], p_self_correct=0.0, p_repeat_word=0.15, volume=0.7,
                           p_talk_over_buddy=0.2, p_off_task_click=0.12, p_tap_mic_to_talk=0.3, says_tired_after_s=0,
                           max_nav_clicks=8)),
    "LKG": dict(prof="emergent", age=4.5, ui=0.05, attn=140, pat=3.3, tech=0.5,
                b=dict(words_per_s=0.7, word_accuracy=0.4, echo_skill=0.65, can_decode=True, p_skip_small=0.3,
                       p_hesitate=0.65, hesitation_s=[2.0, 4.5], p_self_correct=0.05, p_repeat_word=0.1, volume=0.7,
                       p_talk_over_buddy=0.15, p_off_task_click=0.08, p_tap_mic_to_talk=0.2, says_tired_after_s=0,
                       max_nav_clicks=9)),
    "UKG": dict(prof="early", age=5.5, ui=0.15, attn=170, pat=3.8, tech=0.55,
                b=dict(words_per_s=0.9, word_accuracy=0.6, echo_skill=0.75, can_decode=True, p_skip_small=0.2,
                       p_hesitate=0.6, hesitation_s=[1.8, 4.0], p_self_correct=0.1, p_repeat_word=0.1, volume=0.8,
                       p_talk_over_buddy=0.1, p_off_task_click=0.06, p_tap_mic_to_talk=0.12, says_tired_after_s=0,
                       max_nav_clicks=10)),
    "Class 1": dict(prof="early", age=6.5, ui=0.35, attn=190, pat=4.0, tech=0.65,
                    b=dict(words_per_s=1.3, word_accuracy=0.72, echo_skill=0.85, can_decode=True, p_skip_small=0.25,
                           p_hesitate=0.45, hesitation_s=[1.5, 3.5], p_self_correct=0.15, p_repeat_word=0.06, volume=0.85,
                           p_talk_over_buddy=0.12, p_off_task_click=0.04, p_tap_mic_to_talk=0.08, says_tired_after_s=0,
                           max_nav_clicks=11)),
    "Class 2": dict(prof="developing", age=7.5, ui=0.6, attn=210, pat=4.2, tech=0.75,
                    b=dict(words_per_s=1.8, word_accuracy=0.8, echo_skill=0.9, can_decode=True, p_skip_small=0.15,
                           p_hesitate=0.3, hesitation_s=[1.2, 3.0], p_self_correct=0.25, p_repeat_word=0.05, volume=0.9,
                           p_talk_over_buddy=0.12, p_off_task_click=0.03, p_tap_mic_to_talk=0.05, says_tired_after_s=0,
                           max_nav_clicks=12)),
    "Class 3": dict(prof="developing", age=8.5, ui=0.75, attn=240, pat=4.5, tech=0.8,
                    b=dict(words_per_s=2.1, word_accuracy=0.87, echo_skill=0.93, can_decode=True, p_skip_small=0.1,
                           p_hesitate=0.25, hesitation_s=[1.0, 2.5], p_self_correct=0.35, p_repeat_word=0.04, volume=0.95,
                           p_talk_over_buddy=0.1, p_off_task_click=0.02, p_tap_mic_to_talk=0.02, says_tired_after_s=0,
                           max_nav_clicks=13)),
    "Class 4": dict(prof="fluent", age=9.5, ui=0.85, attn=280, pat=4.8, tech=0.85,
                    b=dict(words_per_s=2.4, word_accuracy=0.92, echo_skill=0.96, can_decode=True, p_skip_small=0.05,
                           p_hesitate=0.2, hesitation_s=[1.0, 2.2], p_self_correct=0.45, p_repeat_word=0.02, volume=1.0,
                           p_talk_over_buddy=0.08, p_off_task_click=0.01, p_tap_mic_to_talk=0.0, says_tired_after_s=0,
                           max_nav_clicks=14)),
}

NAMES = iter(["Anaya", "Vihaan", "Saanvi", "Reyansh", "Diya", "Arjun", "Myra", "Advik", "Kiara", "Ayaan", "Aadhya",
              "Vivaan", "Prisha", "Krish", "Anvi", "Shaurya", "Navya", "Atharv", "Riya", "Hridaan", "Tara", "Yash",
              "Pari", "Rudra", "Ira", "Dev", "Jiya", "Om", "Siya", "Neel", "Avni", "Kian", "Mahi", "Parth", "Zoya",
              "Rohan", "Nisha", "Aarush", "Esha", "Veer", "Trisha", "Manav", "Khushi", "Laksh", "Ritika"])


def L(**kw):
    """languages: en=(speak, read), hi=..., gu=..."""
    m = {"en": "en-IN", "hi": "hi-IN", "gu": "gu-IN"}
    return {m[k]: {"speak": v[0], "read": v[1]} for k, v in kw.items()}


# id, grade, preferred language, languages, distinctive traits (overrides), journey, grown-up setup, profile note
ROWS = [
    # ---------------- Nursery (pre-readers) ----------------
    ("N02", "Nursery", "hi-IN", L(hi=(0.8, 0), en=(0.3, 0)), dict(conf=0.25, vol=0.4, prefs=["listen_first", "likes_songs"],
     style="loves listening, rarely speaks up; whispers when she does", b=dict(p_hesitate=0.8, echo_skill=0.45)),
     "listen_then_read", True, "Enjoys rhymes read to her but is shy about speaking."),
    ("N03", "Nursery", "gu-IN", L(gu=(0.8, 0), hi=(0.3, 0)), dict(attn=60, pat=2.5, tech=0.55,
     style="taps everything on the screen, fast and often", b=dict(p_off_task_click=0.25, p_tap_mic_to_talk=0.5)),
     "discover_and_start", False, "Very curious with tablets; short attention."),
    ("N04", "Nursery", "en-IN", L(en=(0.75, 0), hi=(0.6, 0)), dict(conf=0.9, tech=0.5,
     style="loud and eager, says words as soon as he hears them", b=dict(echo_skill=0.8, volume=1.0, p_talk_over_buddy=0.4)),
     "read_whole_poem", True, "Knows many nursery rhymes by heart; repeats eagerly."),
    ("N05", "Nursery", "hi-IN", L(hi=(0.75, 0)), dict(conf=0.2, pat=3.5,
     style="very quiet, long silences before answering", b=dict(volume=0.35, hesitation_s=[3.0, 7.0], p_hesitate=0.9)),
     "discover_and_start", True, "Shy; speaks in a whisper."),
    ("N06", "Nursery", "gu-IN", L(gu=(0.85, 0), en=(0.1, 0)), dict(prefs=["wants_replay", "needs_audio_for_everything"],
     style="asks for things to be said again", b=dict(echo_skill=0.55)), "replay_line", True,
     "Speaks only Gujarati at home; wants to hear things twice."),
    ("N07", "Nursery", "en-IN", L(en=(0.55, 0), hi=(0.8, 0)), dict(attn=80,
     style="gets tired quickly and says so", b=dict(says_tired_after_s=45)), "read_whole_poem", True,
     "English-medium school, Hindi at home; tires fast."),
    ("N08", "Nursery", "hi-IN", L(hi=(0.7, 0), en=(0.5, 0)), dict(mist=["adds_words", "repeats_words"],
     style="mixes Hindi and English words, repeats words", b=dict(p_repeat_word=0.3)), "read_whole_poem", False,
     "Code-mixes Hindi and English."),
    ("N09", "Nursery", "gu-IN", L(gu=(0.6, 0)), dict(pron=0.45, pat=5.0, prefs=["listen_first"],
     style="patient; speech sounds still developing", b=dict(echo_skill=0.4)), "listen_then_read", True,
     "Speech sounds still developing (r/l, s/sh)."),
    ("N10", "Nursery", "en-IN", L(en=(0.8, 0.1), hi=(0.4, 0)), dict(prof="emergent", age=4.2, tech=0.6,
     style="knows some letters, likes doing things again", b=dict(can_decode=True, word_accuracy=0.2, echo_skill=0.7)),
     "restart_session", True, "Recognises a few letters; loves repeating favourites."),
    # ---------------- LKG ----------------
    ("L02", "LKG", "en-IN", L(en=(0.7, 0.25), hi=(0.6, 0)), dict(mist=["letter_confusion", "word_by_word"],
     style="mixes up b/d and p/q"), "make_mistakes", True, "Confuses letters that look alike."),
    ("L03", "LKG", "gu-IN", L(gu=(0.85, 0.2), en=(0.3, 0)), dict(mist=["guesses_from_first_letter"],
     style="chatty, guesses words from pictures", b=dict(p_tap_mic_to_talk=0.4, p_talk_over_buddy=0.25)),
     "discover_and_start", False, "Guesses words from the picture or first letter."),
    ("L04", "LKG", "en-IN", L(en=(0.8, 0.3)), dict(pat=2.5, attn=90, conf=0.85,
     style="fast and impatient, wants to finish quickly", b=dict(words_per_s=1.2, p_hesitate=0.3)),
     "read_whole_poem", True, "Impatient; dislikes waiting."),
    ("L05", "LKG", "hi-IN", L(hi=(0.85, 0.3)), dict(mist=["word_by_word"], pat=4.5,
     style="careful and slow, long pauses between words", b=dict(words_per_s=0.5, p_hesitate=0.85, hesitation_s=[3.0, 6.0])),
     "read_whole_poem", True, "Careful, sounds out each letter."),
    ("L06", "LKG", "gu-IN", L(gu=(0.8, 0.15), hi=(0.6, 0.05)), dict(prefs=["listen_first", "wants_replay"],
     style="likes to hear things first"), "listen_then_read", True, "Bilingual Gujarati-Hindi; reads very little yet."),
    ("L07", "LKG", "en-IN", L(en=(0.7, 0.2), gu=(0.5, 0)), dict(conf=0.9, prefs=["likes_praise"],
     style="loves praise, tries hard, many mistakes", b=dict(word_accuracy=0.35)), "restart_session", True,
     "Very motivated by stars and praise."),
    ("L08", "LKG", "hi-IN", L(hi=(0.8, 0.25)), dict(attn=100, style="says when tired", b=dict(says_tired_after_s=55)),
     "read_whole_poem", True, "Gets tired after a minute of reading."),
    # ---------------- UKG ----------------
    ("U02", "UKG", "en-IN", L(en=(0.75, 0.5), hi=(0.5, 0.1)), dict(mist=["word_by_word", "skips_small_words"],
     style="reads single words but struggles to join them", b=dict(p_skip_small=0.35, p_hesitate=0.8)),
     "read_whole_poem", True, "Can read words, not yet sentences."),
    ("U03", "UKG", "hi-IN", L(hi=(0.85, 0.5)), dict(mist=["matra_errors", "nasal_errors"],
     style="drops and swaps matras"), "make_mistakes", True, "Mixes up short and long vowel signs."),
    ("U04", "UKG", "gu-IN", L(gu=(0.85, 0.45)), dict(mist=["conjunct_errors", "loses_place"], pat=2.8,
     style="gets upset quickly; taps mic to talk", b=dict(p_tap_mic_to_talk=0.25)), "discover_and_start", False,
     "Struggles with joined letters; low frustration tolerance."),
    ("U05", "UKG", "hi-IN", L(hi=(0.9, 0.5), en=(0.4, 0.2)), dict(style="wants to choose a story herself"),
     "explore_and_read", True, "Wants to pick her own story."),
    ("U06", "UKG", "en-IN", L(en=(0.85, 0.5)), dict(tech=0.9, ui=0.35, style="tech-savvy; explores every button",
     b=dict(p_off_task_click=0.15)), "explore_and_read", True, "Uses a tablet daily; explores."),
    ("U07", "UKG", "gu-IN", L(gu=(0.8, 0.5)), dict(conf=0.3, style="reads in a whisper", b=dict(volume=0.4)),
     "read_whole_poem", True, "Low confidence, reads very softly."),
    ("U08", "UKG", "hi-IN", L(hi=(0.85, 0.5)), dict(mist=["repeats_words", "self_corrects"], prefs=["wants_replay"],
     style="repeats words, corrects himself", b=dict(p_repeat_word=0.2, p_self_correct=0.3)), "replay_line", True,
     "Repeats words while thinking."),
    # ---------------- Class 1 ----------------
    ("C1-01", "Class 1", "en-IN", L(en=(0.85, 0.65)), dict(mist=["skips_small_words"],
     style="skips small words like 'a' and 'the'", b=dict(p_skip_small=0.45)), "read_whole_poem", True,
     "Frequently skips small words."),
    ("C1-02", "Class 1", "hi-IN", L(hi=(0.9, 0.65), en=(0.5, 0.3)), dict(mist=["letter_confusion"],
     style="confuses ब/व, श/स"), "make_mistakes", True, "Confuses similar Hindi letters."),
    ("C1-03", "Class 1", "gu-IN", L(gu=(0.9, 0.6)), dict(mist=["word_by_word"], style="slow, word by word",
     b=dict(words_per_s=0.9, p_hesitate=0.7)), "read_whole_poem", True, "Slow, careful Gujarati reader."),
    ("C1-04", "Class 1", "en-IN", L(en=(0.45, 0.55), gu=(0.9, 0.4)), dict(prefs=["listen_first"],
     style="reads English letters but follows spoken English with difficulty"), "listen_then_read", True,
     "Gujarati at home; English-medium school."),
    ("C1-05", "Class 1", "hi-IN", L(hi=(0.9, 0.7)), dict(conf=0.95, style="confident, races ahead, talks over Buddy",
     b=dict(words_per_s=1.9, p_talk_over_buddy=0.3)), "read_whole_poem", False, "Confident Hindi reader for his age."),
    ("C1-06", "Class 1", "gu-IN", L(gu=(0.9, 0.6)), dict(attn=120, style="tires after a couple of minutes",
     b=dict(says_tired_after_s=70)), "read_whole_poem", True, "Tires quickly in the evening."),
    # ---------------- Class 2 ----------------
    ("C2-02", "Class 2", "hi-IN", L(hi=(0.9, 0.8)), dict(mist=["monotone"], style="accurate but flat"),
     "read_whole_poem", True, "Reads accurately without expression."),
    ("C2-03", "Class 2", "gu-IN", L(gu=(0.9, 0.4), en=(0.8, 0.75)), dict(mist=["matra_errors", "guesses_from_first_letter"],
     style="speaks Gujarati well, reads it poorly"), "make_mistakes", True, "Reads English better than Gujarati."),
    ("C2-04", "Class 2", "en-IN", L(en=(0.85, 0.7)), dict(mist=["loses_place", "repeats_words"],
     style="loses place and restarts lines"), "restart_session", True, "Loses his place."),
    ("C2-05", "Class 2", "hi-IN", L(hi=(0.9, 0.75)), dict(mist=["adds_words", "self_corrects"],
     b=dict(p_self_correct=0.5), style="adds words, corrects herself"), "make_mistakes", True, "Self-corrects a lot."),
    ("C2-06", "Class 2", "gu-IN", L(gu=(0.9, 0.7), en=(0.8, 0.7)), dict(tech=0.85,
     style="independent; reads the screen"), "explore_and_read", False, "Uses the app alone."),
    # ---------------- Class 3 ----------------
    ("C3-01", "Class 3", "en-IN", L(en=(0.9, 0.85)), dict(mist=["monotone"], prefs=["wants_rhythm_feedback"],
     style="fluent but no expression"), "read_whole_poem", True, "Struggles with reading expression."),
    ("C3-02", "Class 3", "hi-IN", L(hi=(0.95, 0.8)), dict(mist=["conjunct_errors"], style="trips on joined letters"),
     "make_mistakes", True, "Trips on conjunct consonants."),
    ("C3-03", "Class 3", "gu-IN", L(gu=(0.95, 0.85)), dict(mist=["reads_too_fast", "drops_endings"],
     style="rushes, drops endings, talks over Buddy", b=dict(words_per_s=3.0, p_talk_over_buddy=0.3)),
     "read_whole_poem", True, "Rushes through text."),
    ("C3-04", "Class 3", "en-IN", L(en=(0.9, 0.6)), dict(mist=["letter_confusion", "word_by_word"], pat=5.5,
     prefs=["listen_first"], style="reverses letters; very persistent", b=dict(words_per_s=1.1, word_accuracy=0.7)),
     "listen_then_read", True, "Reverses letters (dyslexia-like pattern)."),
    ("C3-05", "Class 3", "hi-IN", L(hi=(0.95, 0.85), gu=(0.2, 0.05)), dict(prefs=["wants_replay"],
     style="likes to hear model reading"), "replay_line", True, "Strong Hindi reader."),
    ("C3-06", "Class 3", "gu-IN", L(gu=(0.9, 0.8), en=(0.8, 0.75)), dict(style="independent; tires after a while",
     b=dict(says_tired_after_s=110)), "explore_and_read", False, "Explores the app without a grown-up."),
    # ---------------- Class 4 ----------------
    ("C4-02", "Class 4", "en-IN", L(en=(0.95, 0.95)), dict(mist=["monotone"], prefs=["wants_rhythm_feedback"],
     style="fluent; needs help with rhythm and intonation"), "read_whole_poem", True, "Fluent; rhythm needs work."),
    ("C4-03", "Class 4", "gu-IN", L(gu=(0.95, 0.9)), dict(mist=["self_corrects"], b=dict(p_self_correct=0.7),
     style="careful, self-corrects"), "make_mistakes", True, "Careful Gujarati reader."),
    ("C4-04", "Class 4", "en-IN", L(en=(0.95, 0.95), hi=(0.8, 0.7)), dict(attn=120, pat=2.5, prefs=["wants_challenge"],
     style="gets bored with easy texts"), "explore_and_read", True, "Finds most texts too easy."),
    ("C4-05", "Class 4", "hi-IN", L(hi=(0.95, 0.9)), dict(mist=["reads_too_fast", "skips_small_words"],
     b=dict(words_per_s=3.0, p_skip_small=0.15)), "restart_session", True, "Very fast reader."),
    ("C4-06", "Class 4", "gu-IN", L(gu=(0.85, 0.5), en=(0.95, 0.9)), dict(mist=["matra_errors", "conjunct_errors"],
     style="English-medium; Gujarati reading weaker"), "read_whole_poem", True, "Reads English better than Gujarati."),
]


def build() -> dict:
    lib = json.loads(OUT.read_text(encoding="utf-8"))
    pilot = {p["id"]: p for p in lib["personas"] if p["id"] in ("N01", "L01", "U01", "C2-01", "C4-01")}
    out = list(pilot.values())
    for k, (pid, grade, pref, langs, o, journey, grown, note) in enumerate(ROWS):
        g = GRADE[grade]
        b = {**g["b"], **o.get("b", {})}
        if "vol" in o:
            b["volume"] = o["vol"]
        prof = o.get("prof", g["prof"])
        out.append({
            "id": pid, "name": next(NAMES), "grade": grade, "age": o.get("age", g["age"]),
            "reading_proficiency": prof, "language_preference": pref, "languages": langs,
            "ui_english_reading": o.get("ui", min(g["ui"], langs.get("en-IN", {}).get("read", 0) + 0.1)),
            "vocabulary_level": {"pre_reader": "small, spoken", "emergent": "small", "early": "growing",
                                 "developing": "age-typical", "fluent": "rich"}[prof],
            "pronunciation": {"accuracy": o.get("pron", {"pre_reader": 0.6, "emergent": 0.65, "early": 0.75,
                                                        "developing": 0.82, "fluent": 0.92}[prof]),
                              "notes": o.get("style", "")},
            "attention_span_s": o.get("attn", g["attn"]), "confidence": o.get("conf", 0.6),
            "patience": o.get("pat", g["pat"]), "learning_preferences": o.get("prefs", []),
            "common_mistakes": o.get("mist", ["word_by_word"] if prof in ("pre_reader", "emergent") else []),
            "technology_familiarity": o.get("tech", g["tech"]), "interaction_style": o.get("style", ""),
            "testing_objectives": [OBJECTIVES[journey]], "journey": journey, "grown_up_setup": grown,
            "profile_note": note, "behaviour": b, "seed": 1000 + 17 * k,
        })
    order = ["Nursery", "LKG", "UKG", "Class 1", "Class 2", "Class 3", "Class 4"]
    out.sort(key=lambda p: (order.index(p["grade"]), p["id"]))
    return {"version": 2, "note": lib["note"], "personas": out}


OBJECTIVES = {
    "discover_and_start": "Discover how to start reading without help",
    "listen_then_read": "Listen to the poem first, then read it",
    "read_whole_poem": "Read an entire poem",
    "make_mistakes": "Make reading mistakes and understand the corrections",
    "explore_and_read": "Explore the library and pick something suitable, then read",
    "replay_line": "Hear a line again when unsure",
    "restart_session": "Finish, then read the same text again",
}

if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    from collections import Counter
    ps = data["personas"]
    print(len(ps), Counter(p["grade"] for p in ps), Counter(p["language_preference"] for p in ps))
