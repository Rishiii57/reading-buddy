"""Unit tests for normalisation, alignment and the tutor rules (no API calls)."""
import pytest

from backend.aligner import AlignConfig, align
from backend.content import load_library
from backend.normalize import norm, similarity, tokenize
from tests.sim import simulate

LIB = load_library()
KITE = LIB["en-kite"]


def says(actions):
    return [(a["kind"], a["parts"]) for _, a in actions if a["type"] == "say"]


# ---------- normalisation ----------
def test_english_normalisation():
    assert norm("Blue,") == "blue"
    assert norm("don't") == "dont"
    assert norm("2") == "two"
    assert tokenize("umm I have uh a kite") == ["i", "have", "a", "kite"]


def test_indic_script_variants_match():
    assert norm("चिड़िया") == norm("चिडिया")          # nukta
    assert similarity(norm("हँसी"), norm("हंसी")) == 1.0  # chandrabindu vs anusvara
    assert similarity(norm("पीले"), norm("पिले")) >= 0.9  # vowel length
    assert similarity(norm("સુંદર"), norm("સુદર")) >= 0.9  # Gujarati anusvara dropped
    assert norm("थी।") == "थी"


def test_different_words_do_not_match():
    assert similarity(norm("kite"), norm("bike")) < 0.6
    assert similarity(norm("गुड़िया"), norm("चिड़िया")) < 0.75


# ---------- alignment ----------
def ops(text, p=0, free=frozenset()):
    return [o[0] for o in align(tokenize(text), KITE.words, p, AlignConfig(), free).ops]


def test_align_clean():
    assert ops("i have a kite of red and blue") == ["match"] * 8


def test_align_substitution_and_skip():
    assert ops("i have a bike of red") == ["match", "match", "match", "sub", "match", "match"]
    assert ops("i have kite of red") == ["match", "match", "del", "match", "match", "match"]


def test_align_insertion_and_restart():
    assert ops("i have a cat kite") == ["match", "match", "match", "ins", "match"]
    a = align(tokenize("kite of red"), KITE.words, 6, AlignConfig())
    assert a.start == 3  # child went back and re-read: follow, no correction


def test_free_words_do_not_hide_a_misread():
    # the tutor just said words 1-3; a misread of one of them is still a substitution
    assert "sub" in ops("i have a bike of red", free=frozenset({1, 2, 3}))


def test_words_written_together_still_match():
    t = LIB["gu-patang"]
    a = align(tokenize("મારું પતંગલાલને પીળો"), t.words, 0, AlignConfig())
    assert [o[0] for o in a.ops] == ["match", "match", "match"]
    assert a.ops[1][2] == [1, 2, 3]


def test_whole_line_skip():
    o = ops("it dances with the morning breeze", p=8)
    assert o.count("del") == 8 and o.count("match") == 6


# ---------- tutor rules: strict, line-by-line ----------
L0 = [(1, "ss", ""), (3, "tr", "i have a kite of red and blue")]
L1 = [(4, "ss", ""), (6.5, "tr", "it flies up high the whole day through")]


def kinds(actions):
    return [k for k, _ in says(actions)]


def test_clean_reading_is_silent_until_praise_and_finish():
    eng, acts = simulate(KITE, L0 + L1 + [
        (8, "ss", ""), (10, "tr", "it dances with the morning breeze"),
        (11, "ss", ""), (13, "tr", "above the roofs and tall green trees")])
    assert kinds(acts) == ["praise", "finish"]  # praise at the end of verse 1, then the finish
    s = eng.summary(14)
    assert s["words_read"] == len(KITE.words) and s["finished"] and not s["lines_skipped"]


def test_wrong_word_is_practised_then_whole_line_read_again():
    eng, acts = simulate(KITE, [(1, "ss", ""), (3, "tr", "i have a bike of red and blue"),
                                (6, "ss", ""), (7, "tr", "kite"),
                                (11, "ss", ""), (14, "tr", "i have a kite of red and blue")], until=15)
    s = says(acts)
    # "Let's practise this word together." then the word alone
    assert s[0] == ("fix_word", [("phrase", "lets_fix"), ("span", 3, 4)])
    # the word is right: "Yes! Very nice!", the complete original line, "Now you say the whole line."
    assert s[1] == ("repeat_line", [("phrase", "word_ok"), ("span", 0, 8), ("phrase", "say_line")])
    assert s[2] == ("praise", [("phrase", "line_done")]) and eng.line == 1
    assert eng.status[3] == "practise"


def test_every_wrong_word_is_practised_one_by_one():
    eng, acts = simulate(KITE, [(1, "ss", ""), (3, "tr", "i have a bike of bed and blue"),
                                (6, "ss", ""), (7, "tr", "kite"), (10, "ss", ""), (11, "tr", "red")], until=14)
    s = says(acts)
    assert [k for k, _ in s] == ["fix_word", "fix_next", "repeat_line"]
    assert s[1][1] == [("phrase", "word_ok"), ("span", 5, 6)]


def test_wrong_practice_word_is_said_again():
    eng, acts = simulate(KITE, [(1, "ss", ""), (3, "tr", "i have a bike of red and blue"),
                                (6, "ss", ""), (7, "tr", "bike")], until=9)
    assert kinds(acts) == ["fix_word", "fix_again"]
    assert says(acts)[1][1] == [("span", 3, 4)]  # a retry is the word alone
    assert eng.mode == "drill" and eng.mistakes[0] == 2


def test_strict_matching_counts_tiny_skips_and_near_misses():
    eng, acts = simulate(KITE, [(1, "ss", ""), (3, "tr", "i have kite of rad and blue")], until=4)
    assert eng.log[-1]["event"] == "correction" or any(e["event"] == "correction" for e in eng.log)
    corr = next(e for e in eng.log if e["event"] == "correction")
    assert corr["words"] == [2, 5]  # "a" skipped, "rad" for "red"


def test_more_than_ten_mistakes_leaves_the_line_and_says_so_at_the_end():
    script = [(1, "ss", ""), (3, "tr", "i have a bike of red and blue")] + [(6 + 3 * i, "tr", "bike") for i in range(10)]
    script += [(40, "ss", ""), (42, "tr", "it flies up high the whole day through"),
               (44, "ss", ""), (46, "tr", "it dances with the morning breeze"),
               (48, "ss", ""), (50, "tr", "above the roofs and tall green trees")]
    eng, acts = simulate(KITE, script, until=54)
    s = says(acts)
    assert ("skip_line", [("phrase", "skip_line")]) in s
    assert eng.mistakes[0] == 11  # left on the eleventh confirmed mistake
    finish = [p for k, p in s if k == "finish"][0]
    assert finish == [("phrase", "finish"), ("phrase", "missed_lines"), ("span", 0, 8)]
    summ = eng.summary(54)
    assert summ["lines_skipped"][0]["line"] == 1 and summ["lines_skipped"][0]["words"] == ["kite"]
    assert summ["lines_skipped"][0]["text"] == "I have a kite of red and blue," and summ["finished"]
    assert summ["lines_completed"] == 3


def test_stuck_child_gets_a_phrase_then_the_rest_of_the_line_then_time():
    eng, acts = simulate(KITE, L0 + [(4, "ss", ""), (5, "tr", "it flies up")], until=25)
    s = says(acts)
    assert s[0] == ("stall_phrase", [("phrase", "listen"), ("span", 11, 14)])  # "Listen... high the whole"
    assert s[1] == ("stall_rest", [("span", 11, 16), ("phrase", "now_you_try")])
    assert s[2] == ("take_time", [("phrase", "take_time")])
    assert len(s) == 3 and eng.mistakes.get(1, 0) == 0  # silence is never a mistake


def test_child_can_carry_on_after_the_prompted_phrase():
    eng, acts = simulate(KITE, L0 + [(4, "ss", ""), (5, "tr", "it flies up"),
                                     (12, "ss", ""), (13, "tr", "day through")], until=14)
    assert eng.line == 2 and not any(e["event"] == "correction" for e in eng.log)
    assert eng.status[11] == "helped"


def test_prompt_phrase_stops_at_a_comma():
    rain = LIB["hi-baarish"]  # "बादल गरजे, बारिश आई,"
    eng, acts = simulate(rain, [(1, "ss", ""), (3, "tr", "बादल")], until=7)
    assert says(acts)[0] == ("stall_phrase", [("phrase", "listen"), ("span", 1, 2)])


def test_session_opening_greets_names_the_poem_and_demonstrates():
    from backend.tutor import TutorEngine
    eng = TutorEngine(KITE, now=0.0)
    (a,) = eng.start(0.0)
    assert a["parts"] == [("phrase", "welcome"), ("phrase", "today"), ("title",),
                          ("phrase", "listen_first"), ("span", 0, 8), ("phrase", "read_with_me")]


def test_silence_during_word_practice_is_never_counted():
    eng, acts = simulate(KITE, [(1, "ss", ""), (3, "tr", "i have a bike of red and blue")], until=40)
    assert kinds(acts) == ["fix_word", "fix_again", "fix_again", "take_time"]
    assert eng.mistakes[0] == 1 and eng.mode == "drill"  # only the original slip


def test_asking_to_stop_takes_a_break():
    eng, acts = simulate(KITE, L0 + [(4, "ss", ""), (5, "tr", "i am tired")], until=12)
    assert says(acts)[-1] == ("break", [("phrase", "take_break")])
    assert eng.paused and any(a["type"] == "pause" for _, a in acts)


def test_stopping_after_a_slip_practises_the_slip():
    eng, acts = simulate(KITE, L0 + [(4, "ss", ""), (5, "tr", "it fries up")], until=9)
    assert says(acts)[0][0] == "fix_word" and says(acts)[0][1][1] == ("span", 9, 10)


def test_no_prompt_during_line_end_pause():
    eng, acts = simulate(KITE, L0 + [(6, "ss", ""), (8.5, "tr", "it flies up high the whole day through")], until=9)
    assert kinds(acts) == ["praise"]  # end of verse 1, no help needed


def test_self_correction_and_fillers_are_fine():
    eng, acts = simulate(KITE, [(1, "ss", ""), (3, "tr", "umm i have a bike kite of red and blue")], until=4)
    assert kinds(acts) == []
    assert eng.line == 1


def test_known_speech_model_mishearings_are_not_mistakes():
    rain = LIB["en-rain"]  # Prisma writes "peter" for "pitter" even when it is read correctly
    eng, acts = simulate(rain, [(1, "ss", ""), (3, "tr", "peter patter falls the rain")], until=4)
    assert kinds(acts) == [] and eng.line == 1


def test_same_close_form_three_times_is_accepted_but_a_wrong_word_never_is():
    script = [(1, "ss", ""), (3, "tr", "i have a kite of rat and blue")]
    eng, acts = simulate(KITE, script + [(6 + 3 * i, "tr", "rad") for i in range(3)], until=15)
    assert any(e["event"] == "accepted_as_heard" for e in eng.log)  # "rad" ~ "red", heard the same 3 times
    eng, acts = simulate(KITE, [(1, "ss", ""), (3, "tr", "i have a bike of red and blue")]
                         + [(6 + 3 * i, "tr", "bike") for i in range(4)], until=18)
    assert not any(e["event"] == "accepted_as_heard" for e in eng.log) and eng.mode == "drill"


def test_unclear_talk_during_word_practice_asks_again_and_is_not_a_mistake():
    eng, acts = simulate(KITE, [(1, "ss", ""), (3, "tr", "i have a bike of red and blue"),
                                (5, "ss", ""), (5.5, "tr", "wait what was that")], until=6)
    assert kinds(acts) == ["fix_word", "uncertain_word"] and eng.mistakes[0] == 1


def test_unclear_transcript_while_reading_asks_to_read_again():
    eng, acts = simulate(KITE, L0 + [(4, "ss", ""), (5, "tr", "hmm what is this one")], until=6)
    assert says(acts)[-1] == ("uncertain", [("phrase", "say_again")])
    assert not eng.mistakes


def test_pause_holds_prompts_until_resume():
    eng, acts = simulate(KITE, L0 + [(4, "ss", ""), (5, "tr", "it flies up"), (5.5, "pause", ""),
                                     (20, "resume", "")], until=25)  # Grade 1-2 text: young threshold
    prompts = [t for t, a in acts if a["type"] == "say" and a["kind"].startswith("stall")]
    assert prompts and prompts[0] >= 22  # nothing while paused; the stall timer restarts on resume


def replay_live(name):
    """Replay a recorded live microphone session (team member, consenting) through the engine."""
    import json
    from pathlib import Path
    from backend.tutor import TutorEngine
    fx = json.loads((Path(__file__).parent / "fixtures" / f"{name}.json").read_text())
    eng = TutorEngine(LIB[fx["text_id"]], now=0.0)
    eng.state = "CHILD_READING"
    ev, i, t, busy = fx["stt_events"], 0, 0.0, None
    while t < ev[-1]["t"] + 8:
        while i < len(ev) and ev[i]["t"] <= t:
            e = ev[i]
            i += 1
            acts = (eng.on_speech_start(t) if e["type"] == "speech_start" else
                    eng.on_transcript(e.get("text", ""), t, e.get("latency", 0), e.get("audio_duration_ms")))
            busy = t + 2.0 if any(a["type"] == "say" for a in acts) else busy
        if any(a["type"] == "say" for a in eng.tick(t)):
            busy = t + 2.0
        if busy and t >= busy:
            eng.on_tutor_audio_end(t)
            busy = None
        t = round(t + 0.05, 2)
    return eng


def test_live_sessions_asides_are_ignored():
    """Recorded live talk ("wait what", "मतलब पीछे से पढ़ते हैं") is logged as chatter, not mistakes."""
    for name, aside in [("live_en_kite", "wait what"), ("live_hi_chidiya", "मतलब पीछे से पढते हैं")]:
        eng = replay_live(name)
        assert any(e["event"] == "uncertain" and aside in e["text"] for e in eng.log)
        assert not any(e["event"] == "drill_miss" and e.get("heard") == aside for e in eng.log)


@pytest.mark.parametrize("text_id", sorted(LIB))
def test_every_text_reads_through_cleanly(text_id):
    text = LIB[text_id]
    script, t = [], 1.0
    for a, b in text.line_words:
        script += [(t, "ss", ""), (t + 2, "tr", " ".join(w.display for w in text.words[a:b]))]
        t += 3
    eng, acts = simulate(text, script, until=t + 1)
    assert eng.done
    allowed = ("praise", "finish", "echo_line") if text.pre_primary else ("praise", "finish")
    assert not [k for k in kinds(acts) if k not in allowed]


# ---------- REQ-PREPRIMARY-CONTENT: rhymes for Nursery/LKG/UKG with echo reading ----------
def test_library_has_pre_primary_rhymes_in_every_language():
    from collections import Counter
    c = Counter(t.language for t in LIB.values() if t.pre_primary)
    assert all(c[lang] >= 4 for lang in ("en-IN", "hi-IN", "gu-IN")), c


def test_pre_primary_rhyme_models_every_line():
    text = LIB["en-twinkle"]
    script, t = [], 1.0
    for a, b in text.line_words:
        script += [(t, "ss", ""), (t + 2, "tr", " ".join(w.display for w in text.words[a:b]))]
        t += 6
    eng, acts = simulate(text, script, until=t + 1)
    echoes = [a for _, a in acts if a["type"] == "say" and a["kind"] == "echo_line"]
    assert eng.done and len(echoes) == len(text.line_words) - 1
    assert echoes[0]["parts"][0] == ("span", *text.line_range(1))


def test_grade_texts_do_not_echo():
    text = KITE
    script = [(1, "ss", ""), (3, "tr", "i have a kite of red and blue")]
    eng, acts = simulate(text, script, until=6)
    assert not [a for _, a in acts if a["type"] == "say" and a["kind"] == "echo_line"]


# ---------- REQ-STALL-TIMING: adaptive mid-line stall threshold ----------
def _stall_prompts(acts):
    return [t for t, a in acts if a["type"] == "say" and a["kind"].startswith("stall")]


def test_young_text_waits_longer_mid_line():
    # "I have a kite" then silence: a Grade 1-2 text waits ~3 s (was 2 s) before helping
    eng, acts = simulate(KITE, L0 + [(4, "ss", ""), (5, "tr", "it flies up")], until=12)
    p = _stall_prompts(acts)
    assert p and 5 + 3.0 < p[0] < 5 + 4.6


def test_word_by_word_reader_is_not_interrupted():
    # a reader who pauses ~2.8 s between chunks and always carries on alone
    script = L0 + [(4.0, "ss", ""), (4.6, "tr", "it"), (7.4, "ss", ""), (8.0, "tr", "flies"),
                   (10.8, "ss", ""), (11.4, "tr", "up high"), (14.2, "ss", ""), (14.8, "tr", "the whole"),
                   (17.6, "ss", ""), (18.2, "tr", "day through")]
    eng, acts = simulate(KITE, script, until=20)
    assert _stall_prompts(acts) == []


def test_adaptive_limit_is_capped_and_still_helps_a_stuck_reader():
    from backend.tutor import TutorConfig
    eng, acts = simulate(KITE, L0 + [(4, "ss", ""), (5, "tr", "it flies up")], until=12,
                         cfg=TutorConfig(stall_mid_max_s=5.0))
    eng.pause_gaps = [9.0, 9.0, 9.0]
    assert eng.mid_limit() == 5.0


def test_rhyme_slips_are_helped_not_drilled():
    text = LIB["en-twinkle"]
    a, b = text.line_range(0)
    script = [(1, "ss", ""), (3, "tr", "twinkle twinkle little tar")]
    eng, acts = simulate(text, script, until=8)
    assert not [a for _, a in acts if a["type"] == "say" and a["kind"].startswith("fix")]
    assert eng.line == 1 and "helped" in eng.status[a:b]
