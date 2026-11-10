# Product requirements: cycle c02 / retest

Written by the AI Product Manager for the Engineering team. Status *approved* means Engineering may start; *awaiting_human_approval* needs a team decision first; *deferred* is not in this cycle. An item is resolved only when QA validates its acceptance criteria (not when code changes).

## REQ-PREPRIMARY-CONTENT: No reading material for Nursery, LKG and UKG

**Priority:** P1 (score 19.73) · **Status:** awaiting_human_approval (Touches content, privacy or model/data collection: needs a human decision.) · **Owners:** Data Engineer, Speech AI Engineer, Frontend Engineer · **Complexity:** L

1. **Problem statement.** No reading material for Nursery, LKG and UKG. Seen in 5 of 50 simulated children (10%; pre-primary reach 19%), 5 occurrences; 60% of affected children abandoned or could not start.
2. **Affected personas.** L03, L04, N03, N06, U01 · by grade: Nursery 2, LKG 2, UKG 1 · by language: Gujarati 4, English 1
3. **Supporting evidence.** Symptoms: NO_TEXT_FOR_MY_LEVEL×5.  Children said: “The words were too hard. I can't read those yet.”
   - L03 (LKG, Gujarati): LKG child landed on a 'Grade 2-3' text, made for children who already read. {"t": 8.22, "title": "ચકલી અને દાણા", "grade_tag": "Grade 2-3"} · `agent_org/runs/c02/retest/L03`
   - L04 (LKG, English): LKG child landed on a 'Grade 2-4' text, made for children who already read. {"t": 11.37, "title": "The Busy Ant", "grade_tag": "Grade 2-4"} · `agent_org/runs/c02/retest/L04`
   - N03 (Nursery, Gujarati): Nursery child landed on a 'Grade 3' text, made for children who already read. {"t": 9.86, "title": "Ravi and the Mango Tree", "grade_tag": "Grade 3"} · `agent_org/runs/c02/retest/N03`
   - N06 (Nursery, Gujarati): Nursery child landed on a 'Grade 3-4' text, made for children who already read. {"t": 7.33, "title": "મારી શાળા", "grade_tag": "Grade 3-4"} · `agent_org/runs/c02/retest/N06`
4. **Root-cause hypothesis.** The library holds 12 texts for Grades 1-4 (16-37 words of continuous text). The grade filter offers Grade 1-5 only. Pre-primary children are pre-readers or emergent readers; continuous text with no pre-reading formats cannot be read, so every pre-primary session degenerates into stall prompts.
5. **Expected behaviour.** Each language offers at least 3 items per pre-primary level (Nursery: listen-and-repeat rhymes of 2-4 short lines; LKG: picture-word / letter-sound items; UKG: 3-4 word sentences), selectable from a pre-primary filter, and Buddy models each line before the child repeats it.
6. **Technical implementation requirements.** Modules: `content/*.json`, `backend/content.py`, `frontend/app.js (grade filter)`, `cache/tts`
   - Add a `level` field (nursery|lkg|ukg|1..4) to content specs and `/api/library`; keep `grade` for backward compatibility.
   - Author pre-primary items per language; Hindi/Gujarati wording must be reviewed by a native-speaking teacher before release (human approval).
   - Pre-generate Timbre clips for every line and word (backend/pregen.py) so first use is instant and cached.
   - Library UI: add Nursery/LKG/UKG chips with picture icons (non-readers).
   - Tutor: an `echo` mode for pre-primary items (Buddy reads each line, child repeats) via TutorConfig, not a new engine.
7. **Acceptance criteria.**
   - `level_mismatch_rate` <= 0.0; scope: pre-primary personas. Baseline this cycle: 0.1.
   - `coverage` >= 0.6; scope: pre-primary personas. Baseline this cycle: 0.626.
   - `stuck_rate` <= 0.1; scope: pre-primary personas. Baseline this cycle: 0.0.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Re-run all Nursery/LKG/UKG personas with the same seeds; compare level_mismatch_rate, coverage and stuck_rate; native-speaker review sign-off recorded in the decision log. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P1

## REQ-STALL-TIMING: Stall prompt fires during normal thinking pauses of slow and hesitant readers

**Priority:** P1 (score 19.21) · **Status:** validated_fixed (Validated fix holds: residual cases only (11 children, was 20). Kept under watch.) · **Owners:** Backend Engineer, AI/ML Engineer · **Complexity:** S

1. **Problem statement.** Stall prompt fires during normal thinking pauses of slow and hesitant readers. Seen in 11 of 50 simulated children (22%; pre-primary reach 38%), 18 occurrences; 55% of affected children abandoned or could not start.
2. **Affected personas.** C2-03, L01, L04, L05, L07, N01, N04, N06, N10, U01, U02 · by grade: Nursery 4, LKG 4, UKG 2, Class 2 1 · by language: Gujarati 3, Hindi 2, English 6
3. **Supporting evidence.** Symptoms: INTERRUPTED_WHILE_THINKING×11.  Children said: “Buddy talked when I was thinking!” / “I was just thinking and Buddy jumped in.”
   - C2-03 (Class 2, Gujarati): Buddy started talking 3.1 s into a planned 2.98 s thinking pause. {"t": 41.13, "paused_s": 3.1, "planned_s": 2.98, "line": 1, "buddy_kind": "stall_phrase", "next_words": "દાણા શોધવા જતી."} · `agent_org/runs/c02/retest/C2-03`
   - L01 (LKG, Hindi): Buddy started talking 4.5 s into a planned 4.27 s thinking pause. {"t": 36.5, "paused_s": 4.5, "planned_s": 4.27, "line": 0, "buddy_kind": "stall_phrase", "next_words": "गोपी चंदर,"} · `agent_org/runs/c02/retest/L01`
   - L04 (LKG, English): Buddy started talking 2.4 s into a planned 2.83 s thinking pause. {"t": 37.59, "paused_s": 2.4, "planned_s": 2.83, "line": 0, "buddy_kind": "stall_phrase", "next_words": "small ant walked"} · `agent_org/runs/c02/retest/L04`
   - L05 (LKG, Hindi): Buddy started talking 5.3 s into a planned 5.99 s thinking pause. {"t": 49.7, "paused_s": 5.3, "planned_s": 5.99, "line": 0, "buddy_kind": "stall_phrase", "next_words": "रानी है,"} · `agent_org/runs/c02/retest/L05`
4. **Root-cause hypothesis.** TutorConfig.stall_mid_s = 2.0 s is one fixed threshold for every child. Word-by-word and hesitant readers in Nursery-UKG pause 2-5 s between words while decoding, so Buddy supplies the next words before the child tries them, which removes the decoding attempt.
5. **Expected behaviour.** Buddy waits longer mid-line for young/hesitant readers and for a child who has been reading word by word, while still prompting a genuinely stuck child within a few seconds.
6. **Technical implementation requirements.** Modules: `backend/tutor.py TutorConfig.stall_mid_s / tick()`, `backend/main.py Session`
   - Make stall thresholds adaptive: stall_mid_s = clamp(k x the reader's median inter-word gap observed in this session, 2.0, 5.0), with k configurable (default 2.0).
   - Add a `pace` profile (young|standard) to TutorConfig with stall_mid_s 3.5 s for young; select via the text level (pre-primary/Grade 1) until per-child profiles exist.
   - Never fire a stall prompt within 1.0 s of a transcript that advanced the pointer.
   - Keep eval/replay stall detection within 4.0 s on the stall test set (no regression in catching real stalls).
7. **Acceptance criteria.**
   - `stall_interruptions_per_agent` <= 0.5 × baseline; scope: affected personas. Baseline this cycle: 0.36.
   - `stuck_rate` <= baseline (no worse); scope: no new stuck children. Baseline this cycle: 0.0.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Re-run hesitant/word-by-word personas (same seeds) before/after; run eval.replay and check 'stalls prompted' stays >= 11/12. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P1

## REQ-NAVIGATION: Children cannot find a text or leave the reading page by accident

**Priority:** P2 (score 18.0) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Frontend Engineer · **Complexity:** M

1. **Problem statement.** Children cannot find a text or leave the reading page by accident. Seen in 18 of 50 simulated children (36%; pre-primary reach 62%), 18 occurrences; 33% of affected children abandoned or could not start.
2. **Affected personas.** C1-06, C2-02, L01, L02, L03, L06, L07, L08, N01, N03, N05, N06, N08, N09, U03, U05, U06, U08 · by grade: Nursery 6, LKG 6, UKG 4, Class 1 1, Class 2 1 · by language: Gujarati 6, Hindi 8, English 4
3. **Supporting evidence.** Symptoms: LEFT_READING_BY_ACCIDENT×18.  Children said: “Where did my poem go?” / “I pressed something and the poem went away.”
   - C1-06 (Class 1, Gujarati): A curious tap on 'Home' left the reading page. {"t": 62.64, "tapped": "Home", "view": "view-home"} · `agent_org/runs/c02/retest/C1-06`
   - C2-02 (Class 2, Hindi): A curious tap on 'Library' left the reading page. {"t": 47.05, "tapped": "Library", "view": "view-library"} · `agent_org/runs/c02/retest/C2-02`
   - L01 (LKG, Hindi): A curious tap on 'Library' left the reading page. {"t": 93.46, "tapped": "Library", "view": "view-library"} · `agent_org/runs/c02/retest/L01`
   - L02 (LKG, English): Tapped something that left the reading page before starting. {"t": 15.0, "view": "view-about"} · `agent_org/runs/c02/retest/L02`
4. **Root-cause hypothesis.** Back and End are always-visible buttons next to the reading area; a stray tap leaves or ends the session with no confirmation.
5. **Expected behaviour.** Leaving a running session needs a confirmation that is spoken and pictorial; End during the first 10 s asks again.
6. **Technical implementation requirements.** Modules: `frontend/index.html reader-bar (Back/End)`, `frontend/app.js route()`
   - Confirm dialog (child-friendly, spoken) for Back/End while a session runs.
7. **Acceptance criteria.**
   - `abandon_rate` <= 0.8 × baseline; scope: all personas. Baseline this cycle: 0.4.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** All personas, same seeds. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-FALSE-CORRECTION-TUTOR: Correctly read words flagged for practice (tutor/aligner)

**Priority:** P2 (score 17.34) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** NLP Engineer, AI/ML Engineer · **Complexity:** M

1. **Problem statement.** Correctly read words flagged for practice (tutor/aligner). Seen in 5 of 50 simulated children (10%; pre-primary reach 4%), 5 occurrences; 80% of affected children abandoned or could not start.
2. **Affected personas.** C2-01, C2-05, C3-04, C4-04, U01 · by grade: UKG 1, Class 2 2, Class 3 1, Class 4 1 · by language: English 3, Hindi 1, Gujarati 1
3. **Supporting evidence.** Symptoms: FALSE_CORRECTION×5.  Children said: “Buddy said I got a word wrong but I read it right.” / “But I said it right!”
   - C2-01 (Class 2, English): Read 'But' correctly but Buddy asked to practise it. {"t": 203.1, "word": "But", "child_said": "But", "speech_model_wrote": "But the ant did not give"} · `agent_org/runs/c02/retest/C2-01`
   - C2-05 (Class 2, Hindi): Read 'पर' correctly but Buddy asked to practise it. {"t": 40.22, "word": "पर", "child_said": "पड़ पर", "speech_model_wrote": "एक पेड़ पड़ पर छोटी चिड़िया रहती थी"} · `agent_org/runs/c02/retest/C2-05`
   - C3-04 (Class 3, English): Read 'Every' correctly but Buddy asked to practise it. {"t": 173.37, "word": "Every", "child_said": "Every", "speech_model_wrote": "Every sunmer summer"} · `agent_org/runs/c02/retest/C3-04`
   - C4-04 (Class 4, English): Read 'the' correctly but Buddy asked to practise it. {"t": 73.14, "word": "the", "child_said": "the", "speech_model_wrote": "The rice was bigger than dhe ant"} · `agent_org/runs/c02/retest/C4-04`
4. **Root-cause hypothesis.** The strict aligner (match_thr 0.85) or the muted-fragment logic marks words as errors when the transcript is split or re-read; check each case against the child's ground truth.
5. **Expected behaviour.** < 1 false correction per 50 correctly read words in simulated sessions and in eval.replay.
6. **Technical implementation requirements.** Modules: `backend/aligner.py`, `backend/tutor.py _read()`
   - Inspect each logged case; add regression fixtures to tests/test_tutor.py; adjust alignment only with replay evidence.
7. **Acceptance criteria.**
   - `false_corrections_per_agent` <= 0.5 × baseline; scope: affected personas. Baseline this cycle: 0.16.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** eval.replay false corrections per 50 words must not rise; simulated sessions before/after. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-MIDLINE-CORRECTION: A slip followed by a thinking pause triggers word practice mid-line

**Priority:** P2 (score 17.2) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Backend Engineer · **Complexity:** S

1. **Problem statement.** A slip followed by a thinking pause triggers word practice mid-line. Seen in 3 of 50 simulated children (6%; pre-primary reach 4%), 4 occurrences; 100% of affected children abandoned or could not start.
2. **Affected personas.** C2-04, C3-04, U01 · by grade: UKG 1, Class 2 1, Class 3 1 · by language: English 2, Gujarati 1
3. **Supporting evidence.** Symptoms: INTERRUPTED_WHILE_THINKING×3.  Children said: “I was just thinking and Buddy jumped in.” / “Buddy talked when I was thinking!”
   - C2-04 (Class 2, English): Buddy started talking 3.3 s into a planned 2.09 s thinking pause. {"t": 59.13, "paused_s": 3.3, "planned_s": 2.09, "line": 0, "buddy_kind": "fix_word", "next_words": "रहती थी।"} · `agent_org/runs/c02/retest/C2-04`
   - C3-04 (Class 3, English): Buddy started talking 0.3 s into a planned 1.99 s thinking pause. {"t": 77.79, "paused_s": 0.3, "planned_s": 1.99, "line": 1, "buddy_kind": "fix_word", "next_words": "summer the tree"} · `agent_org/runs/c02/retest/C3-04`
   - U01 (UKG, Gujarati): Buddy started talking 3.9 s into a planned 3.56 s thinking pause. {"t": 162.04, "paused_s": 1.7, "planned_s": 2.44, "line": 3, "buddy_kind": "fix_word", "next_words": "ઊડતો જાય."} · `agent_org/runs/c02/retest/U01`
4. **Root-cause hypothesis.** tick() calls _check_line() as soon as idle >= stall_mid_s (2.0 s) when the line already has an error, so a child who misreads a word and pauses to think (or to self-correct) is pulled into word practice before finishing the line. Self-correction after 2 s is never possible.
5. **Expected behaviour.** After a slip, Buddy lets the child finish the line (or pause up to the stall threshold for that child), then practises the word.
6. **Technical implementation requirements.** Modules: `backend/tutor.py tick() -> _check_line()`
   - In tick(), when errors exist mid-line, wait max(stall threshold, self_correct_s + 1.5 s) before _check_line().
   - If a later transcript in the same line re-reads the slipped word correctly, clear it from line_errors (self-correction).
7. **Acceptance criteria.**
   - `correction_interruptions_per_agent` <= 0.5 × baseline; scope: affected personas. Baseline this cycle: 0.08.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Same personas and seeds before/after; unit test: slip + 2.5 s pause + continue does not trigger a correction mid-line. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-DRILL-LOOP: Word practice and line repetition loop on the same word or line

**Priority:** P2 (score 16.55) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Backend Engineer, AI/ML Engineer · **Complexity:** S

1. **Problem statement.** Word practice and line repetition loop on the same word or line. Seen in 5 of 50 simulated children (10%; pre-primary reach 4%), 9 occurrences; 80% of affected children abandoned or could not start.
2. **Affected personas.** C2-01, C2-04, C2-05, C3-01, L03 · by grade: LKG 1, Class 2 3, Class 3 1 · by language: English 3, Hindi 1, Gujarati 1
3. **Supporting evidence.** Symptoms: SAME_WORD_ASKED_AGAIN_AND_AGAIN×5.  Children said: “Buddy made me say the same word again and again.” / “Again? I said it already!”
   - C2-01 (Class 2, English): Asked to say 'It' 3 times. {"t": 92.44, "word": "It", "times": 3} · `agent_org/runs/c02/retest/C2-01`
   - C2-04 (Class 2, English): Asked to say 'पर' 3 times. {"t": 73.82, "word": "पर", "times": 3} · `agent_org/runs/c02/retest/C2-04`
   - C2-05 (Class 2, Hindi): Asked to say 'एक' 3 times. {"t": 160.78, "word": "एक", "times": 3} · `agent_org/runs/c02/retest/C2-05`
   - C3-01 (Class 3, English): Asked to say 'the' 3 times. {"t": 163.5, "word": "the", "times": 3} · `agent_org/runs/c02/retest/C3-01`
4. **Root-cause hypothesis.** A drill word is repeated until recognised and a line can be re-read until it is error-free, with up to max_line_mistakes = 10 mistakes per line before moving on. For young children ten failed tries on one line is far past frustration.
5. **Expected behaviour.** At most 2 attempts per practice word (then Buddy says it together with the child and moves on), and max_line_mistakes scaled by level (pre-primary/Grade 1: 4; others: 6).
6. **Technical implementation requirements.** Modules: `backend/tutor.py _drill_attempt(), _add_mistakes(), TutorConfig.max_line_mistakes`
   - Add TutorConfig.max_word_attempts (default 2): after that, mark the word 'helped', say `word_ok` and continue.
   - Make max_line_mistakes level-dependent through the pace profile.
7. **Acceptance criteria.**
   - `drill_repeat_rate` <= 0.0; scope: all personas. Baseline this cycle: 0.1.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Personas with low accuracy before/after; unit test for the attempt cap. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-FALSE-CORRECTION-STT: Correct reading misheard by the speech model (child voices)

**Priority:** P2 (score 14.64) · **Status:** awaiting_human_approval (Touches content, privacy or model/data collection: needs a human decision.) · **Owners:** Speech AI Engineer, AI/ML Engineer · **Complexity:** L

1. **Problem statement.** Correct reading misheard by the speech model (child voices). Seen in 2 of 50 simulated children (4%; pre-primary reach 0%), 3 occurrences; 0% of affected children abandoned or could not start.
2. **Affected personas.** C4-02, C4-06 · by grade: Class 4 2 · by language: English 1, Gujarati 1
3. **Supporting evidence.** Symptoms: FALSE_CORRECTION_STT×2.  Children said: “I read it right but Buddy heard something else.”
   - C4-02 (Class 4, English): Read 'ant' correctly but Buddy asked to practise it (the speech model wrote it differently). {"t": 120.18, "word": "ant", "child_said": "ant", "speech_model_wrote": "bua But the amt did not give"} · `agent_org/runs/c02/retest/C4-02`
   - C4-06 (Class 4, Gujarati): Read 'મોટું' correctly but Buddy asked to practise it (the speech model wrote it differently). {"t": 61.0, "word": "મોટું", "child_said": "મોટું", "speech_model_wrote": "શાળામાં એક મોઠું મેદાન છે"} · `agent_org/runs/c02/retest/C4-06`
4. **Root-cause hypothesis.** Prisma's error rate on young children's speech is unmeasured (all test audio is adult TTS). Gujarati already shows 7.3 % WER on clean synthetic speech.
5. **Expected behaviour.** Measured child-speech WER per language from consenting, safeguarded recordings; aliases learned from them.
6. **Technical implementation requirements.** Modules: `backend/gnani.py STT settings`, `content/stt_aliases.json`, `eval/`
   - Collect consented recordings (team members' children only with written parental consent, stored offline, deletable) - human approval.
   - Extend eval/run_stt.py to those recordings; learn aliases with eval/build_aliases.py.
7. **Acceptance criteria.**
   - None measurable by the simulation yet; needs the method in 8.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Audio evaluation report (separate from simulated satisfaction). QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-SPOKEN-ONBOARDING: Before a session starts, all guidance is written English; non-readers get no spoken instructions

**Priority:** P2 (score 14.54) · **Status:** validated_fixed (Validated fix holds: residual cases only (1 children, was 35). Kept under watch.) · **Owners:** Frontend Engineer, Speech AI Engineer · **Complexity:** S

1. **Problem statement.** Before a session starts, all guidance is written English; non-readers get no spoken instructions. Seen in 1 of 50 simulated children (2%; pre-primary reach 4%), 1 occurrences; 0% of affected children abandoned or could not start.
2. **Affected personas.** N06 · by grade: Nursery 1 · by language: Gujarati 1
3. **Supporting evidence.** Symptoms: LISTEN_FIRST_NOT_FOUND×1.  Children said: “I wanted it to read to me first.”
   - N06 (Nursery, Gujarati): Wanted to hear the poem first but could not tell which button does that. {"t": 11.88, "label": "Listen first"} · `agent_org/runs/c02/retest/N06`
4. **Root-cause hypothesis.** resetReaderUI() writes 'Press the big microphone and read the first line out loud.' into the bubble but nothing is spoken until the session starts. Pre-readers, and children who read Hindi or Gujarati but not English, cannot tell which button starts reading or that 'Listen first' exists.
5. **Expected behaviour.** On opening a text, Buddy says (in the text's language, from the Timbre cache) one short line: what the big microphone does and that the speaker button reads the poem first. Bubble text also appears in the text's language.
6. **Technical implementation requirements.** Modules: `frontend/app.js openText()/resetReaderUI()`, `backend/phrases.py`
   - Add phrases `reader_hint` per language in backend/phrases.py; expose `/api/phrase/{lang}/{key}` returning the cached clip URL.
   - On openText(), play the hint once per visit after the first user gesture (autoplay policy); never while a session runs.
   - Localise the reader bubble strings (resetReaderUI, listeningBubble, yourTurnBubble) for hi/gu.
7. **Acceptance criteria.**
   - `spoken_guidance_gap_rate` <= 0.0; scope: personas with ui_english_reading < 0.3. Baseline this cycle: 0.0.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Pre-reader personas: the reader page must emit a spoken hint before the first mic tap (observed in the agent's 'heard' channel). QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-LONG-INTRO: Buddy's opening talk is long before the child gets a turn

**Priority:** P2 (score 14.18) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Backend Engineer · **Complexity:** S

1. **Problem statement.** Buddy's opening talk is long before the child gets a turn. Seen in 33 of 50 simulated children (66%; pre-primary reach 62%), 33 occurrences; 30% of affected children abandoned or could not start.
2. **Affected personas.** C1-02, C1-05, C1-06, C2-03, C2-04, C2-05, C2-06, C3-01, C3-02, C3-03, C3-04, C3-05, C3-06, C4-01, C4-03, C4-05, C4-06, L01, L03, L05, L06, L07, N01, N02, N06, N07, N09, N10, U02, U04, U05, U06, U08 · by grade: Nursery 6, LKG 5, UKG 5, Class 1 3, Class 2 4, Class 3 6, Class 4 4 · by language: Hindi 12, Gujarati 12, English 9
3. **Supporting evidence.** Symptoms: LONG_TUTOR_TALK×33.  Children said: “Buddy talks a lot before I get to read.” / “Buddy talked too long.”
   - C1-02 (Class 1, Hindi): Buddy talked for over 12 s in one go before the child could read. {"t": 28.23, "talk_s": 12.3} · `agent_org/runs/c02/retest/C1-02`
   - C1-05 (Class 1, Hindi): Buddy talked for over 12 s in one go before the child could read. {"t": 27.7, "talk_s": 12.1} · `agent_org/runs/c02/retest/C1-05`
   - C1-06 (Class 1, Gujarati): Buddy talked for over 12 s in one go before the child could read. {"t": 30.72, "talk_s": 13.0} · `agent_org/runs/c02/retest/C1-06`
   - C2-03 (Class 2, Gujarati): Buddy talked for over 12 s in one go before the child could read. {"t": 27.85, "talk_s": 12.2} · `agent_org/runs/c02/retest/C2-03`
4. **Root-cause hypothesis.** start() chains welcome + 'today we're going to read' + title + 'listen carefully' + line 1 + 'your turn' into one ~13 s utterance; short attention spans are spent before reading starts.
5. **Expected behaviour.** First turn within ~8 s: one greeting phrase + line demonstration + 'your turn'; the title is shown, and the full welcome is used only on a child's first session.
6. **Technical implementation requirements.** Modules: `backend/tutor.py start()`
   - Drop `today` + title from start() after the first session on the device (client sends `first_visit`), or always for pre-primary items.
   - Merge `listen_first` and `read_with_me` into one short phrase per language.
7. **Acceptance criteria.**
   - `intro_s_median` <= 9.0; scope: all personas. Baseline this cycle: 13.8.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Median intro_s before/after on the same persona set. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-TALK-OVER-BUDDY: What a child says while Buddy is talking is silently discarded

**Priority:** P2 (score 14.16) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Speech AI Engineer, Frontend Engineer · **Complexity:** M

1. **Problem statement.** What a child says while Buddy is talking is silently discarded. Seen in 26 of 50 simulated children (52%; pre-primary reach 50%), 49 occurrences; 38% of affected children abandoned or could not start.
2. **Affected personas.** C1-01, C1-02, C1-03, C1-05, C2-01, C2-03, C2-06, C3-01, C3-04, C4-01, C4-02, C4-04, C4-05, L01, L04, L05, L06, L07, N01, N04, N09, N10, U01, U02, U04, U08 · by grade: Nursery 4, LKG 5, UKG 4, Class 1 4, Class 2 3, Class 3 2, Class 4 4 · by language: English 12, Hindi 7, Gujarati 7
3. **Supporting evidence.** Symptoms: SPEECH_IGNORED_WHILE_BUDDY_TALKS×26.  Children said: “Buddy didn't hear me when I was talking.” / “I said it but Buddy didn't hear me!”
   - C1-01 (Class 1, English): 4 word(s) the child said were not heard because Buddy was talking or the session was paused. {"t": 27.58, "said": "Rain rain ga all", "heard": ""} · `agent_org/runs/c02/retest/C1-01`
   - C1-02 (Class 1, Hindi): 3 word(s) the child said were not heard because Buddy was talking or the session was paused. {"t": 38.97, "said": "मछली की रानी रानी", "heard": "रानी"} · `agent_org/runs/c02/retest/C1-02`
   - C1-03 (Class 1, Gujarati): 1 word(s) the child said were not heard because Buddy was talking or the session was paused. {"t": 17.76, "said": "આવ", "heard": ""} · `agent_org/runs/c02/retest/C1-03`
   - C1-05 (Class 1, Hindi): 3 word(s) the child said were not heard because Buddy was talking or the session was paused. {"t": 24.89, "said": "મામાણું ઘર કેટલે", "heard": ""} · `agent_org/runs/c02/retest/C1-05`
4. **Root-cause hypothesis.** The mic is zeroed while Buddy speaks (to avoid echo). Eager readers start the next line during praise or the line demonstration; their words never reach the speech model and nothing tells them.
5. **Expected behaviour.** Short praise is interruptible: if the child starts speaking (local level detector), Buddy's praise clip stops and the mic opens. For non-interruptible speech (demonstrations), a visible/audible 'my turn first' cue.
6. **Technical implementation requirements.** Modules: `frontend/app.js startMic() mute while tutorSpeaking`, `frontend/app.js playSay()`
   - Client-side energy VAD on the raw mic stream while muted; if speech > 300 ms during a `praise` say, stop playback, send audio_done, unmute.
   - Mark say kinds as interruptible (praise, keep_going) vs not (intro demonstration, repeat_line, fix_*).
7. **Acceptance criteria.**
   - `unheard_words_per_agent` <= 0.5 × baseline; scope: affected personas. Baseline this cycle: 2.6.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Fast-reader personas (high p_talk_over_buddy) before/after; echo safety checked by a consenting adult on a laptop speaker (manual). QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-LANGUAGE-SELECTION: Children end up in, or hear, a language they did not choose

**Priority:** P3 (score 13.6) · **Status:** deferred (P3: below the approval line this cycle.) · **Owners:** Frontend Engineer · **Complexity:** S

1. **Problem statement.** Children end up in, or hear, a language they did not choose. Seen in 12 of 50 simulated children (24%; pre-primary reach 35%), 35 occurrences; 50% of affected children abandoned or could not start.
2. **Affected personas.** C1-04, C1-05, C2-04, L06, L07, N01, N02, N03, N04, N05, N09, N10 · by grade: Nursery 7, LKG 2, Class 1 2, Class 2 1 · by language: English 6, Hindi 3, Gujarati 3
3. **Supporting evidence.** Symptoms: BUDDY_LANGUAGE_NOT_UNDERSTOOD×8, WRONG_LANGUAGE_TEXT×11.  Children said: “This isn't my language!” / “I don't know what Buddy said.” / “Buddy talked in a language I don't really know.”
   - C1-04 (Class 1, English): Buddy spoke in en-IN, which this child understands poorly (0.5). {"t": 13.35, "kind": "intro", "said": "Hello! Welcome to Reading Buddy! Today we're going to read Baa, Baa, Black Sheep"} · `agent_org/runs/c02/retest/C1-04`
   - C1-05 (Class 1, Hindi): Wanted hi-IN but ended up on a gu-IN text. {"t": 8.08, "wanted": "hi-IN", "got": "gu-IN", "title": "મામાનું ઘર કેટલે"} · `agent_org/runs/c02/retest/C1-05`
   - C1-05 (Class 1, Hindi): Buddy spoke in gu-IN, which this child understands poorly (0.0). {"t": 15.62, "kind": "intro", "said": "નમસ્તે! રીડિંગ બડીમાં તારું સ્વાગત છે! આજે આપણે વાંચીશું મામાનું ઘર કેટલે ધ્યાનથ"} · `agent_org/runs/c02/retest/C1-05`
   - C2-04 (Class 2, English): Wanted en-IN but ended up on a hi-IN text. {"t": 8.98, "wanted": "en-IN", "got": "hi-IN", "title": "चिड़िया का घोंसला"} · `agent_org/runs/c02/retest/C2-04`
4. **Root-cause hypothesis.** First-visit default language is Gujarati; language cards and tabs rely on reading script names; non-readers pick by picture and land in another language.
5. **Expected behaviour.** Default language follows the browser/device locale (hi -> Hindi, gu -> Gujarati, else English); each language card speaks its name when tapped once (tap again to open).
6. **Technical implementation requirements.** Modules: `frontend/app.js app.lang default 'gu-IN', library tabs`
   - Use navigator.languages to pick the first-visit default.
   - Language cards: first tap plays a cached clip of the language name.
7. **Acceptance criteria.**
   - `wrong_language_rate` <= 0.5 × baseline; scope: all personas. Baseline this cycle: 0.22.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** All personas, same seeds. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P3

## REQ-RESTART: Reading the same text again does not work smoothly

**Priority:** P3 (score 13.52) · **Status:** deferred (P3: below the approval line this cycle.) · **Owners:** Frontend Engineer · **Complexity:** S

1. **Problem statement.** Reading the same text again does not work smoothly. Seen in 1 of 50 simulated children (2%; pre-primary reach 4%), 1 occurrences; 0% of affected children abandoned or could not start.
2. **Affected personas.** L07 · by grade: LKG 1 · by language: English 1
3. **Supporting evidence.** Symptoms: RESTART_NOT_FOUND×1.  Children said: “Again!”
   - L07 (LKG, English): Wanted to read it again but found no way from the end screen.  · `agent_org/runs/c02/retest/L07`
4. **Root-cause hypothesis.** 'Read this again' routes to the same hash; the reader may not re-open or reset correctly.
5. **Expected behaviour.** Read this again re-opens the text ready to start.
6. **Technical implementation requirements.** Modules: `frontend/app.js againBtn / openText()`
   - Force a re-render when the route hash is unchanged.
7. **Acceptance criteria.**
   - `restart_failed_rate` <= 0.0; scope: restart personas. Baseline this cycle: 0.02.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Restart personas. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P3

## REQ-REPLAY: No way to hear a line again during reading

**Priority:** P3 (score 11.03) · **Status:** deferred (P3: below the approval line this cycle.) · **Owners:** Frontend Engineer, Backend Engineer · **Complexity:** S

1. **Problem statement.** No way to hear a line again during reading. Seen in 4 of 50 simulated children (8%; pre-primary reach 12%), 4 occurrences; 0% of affected children abandoned or could not start.
2. **Affected personas.** C3-05, L06, N06, U08 · by grade: Nursery 1, LKG 1, UKG 1, Class 3 1 · by language: Hindi 2, Gujarati 2
3. **Supporting evidence.** Symptoms: NO_REPLAY_CONTROL×4.  Children said: “I want to hear it again!” / “I wanted Buddy to read the line again but there was no button.”
   - C3-05 (Class 3, Hindi): Wanted Buddy to read the line again, but there is no button for that while reading ('Listen first' is switched off during a session). {"t": 35.8, "visible": ["Reading Buddy", "Home", "Library", "About", "Back", "Pause", "End", "Listening"]} · `agent_org/runs/c02/retest/C3-05`
   - L06 (LKG, Gujarati): Wanted Buddy to read the line again, but there is no button for that while reading ('Listen first' is switched off during a session). {"t": 42.7, "visible": ["Reading Buddy", "Home", "Library", "About", "Back", "Pause", "End", "Listening"]} · `agent_org/runs/c02/retest/L06`
   - N06 (Nursery, Gujarati): Wanted Buddy to read the line again, but there is no button for that while reading ('Listen first' is switched off during a session). {"t": 29.26, "visible": ["Reading Buddy", "Home", "Library", "About", "Back", "Pause", "End", "Listening"]} · `agent_org/runs/c02/retest/N06`
   - U08 (UKG, Hindi): Wanted Buddy to read the line again, but there is no button for that while reading ('Listen first' is switched off during a session). {"t": 36.63, "visible": ["Reading Buddy", "Home", "Library", "About", "Back", "Pause", "End", "Listening"]} · `agent_org/runs/c02/retest/U08`
4. **Root-cause hypothesis.** 'Listen first' is disabled once a session runs; children who did not catch Buddy's model reading cannot ask for it again except by stalling.
5. **Expected behaviour.** A 'hear this line' (speaker) button next to the active line during a session; Buddy reads the current line and the child continues.
6. **Technical implementation requirements.** Modules: `frontend/app.js setControls() (listenBtn disabled while running)`, `backend/main.py control messages`
   - Add a control message `replay_line`; engine returns a `say` of the current line span without counting a prompt.
   - Speaker icon button on the active line band; disabled while Buddy talks.
7. **Acceptance criteria.**
   - `replay_missing_rate` <= 0.0; scope: personas who want replays. Baseline this cycle: 0.08.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Replay-seeking personas before/after. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P3

## REQ-LENIENT-MATCHING: Some misreadings are accepted as correct (vowel length, matras, word endings, small words)

**Priority:** P3 (score 10.95) · **Status:** awaiting_human_approval (Touches content, privacy or model/data collection: needs a human decision.) · **Owners:** NLP Engineer · **Complexity:** M

1. **Problem statement.** Some misreadings are accepted as correct (vowel length, matras, word endings, small words). Seen in 14 of 50 simulated children (28%; pre-primary reach 19%), 17 occurrences; 21% of affected children abandoned or could not start.
2. **Affected personas.** C1-02, C1-04, C1-05, C2-01, C2-03, C3-01, C3-03, C3-06, C4-06, L01, L03, U01, U07, U08 · by grade: LKG 2, UKG 3, Class 1 3, Class 2 2, Class 3 3, Class 4 1 · by language: Hindi 4, English 3, Gujarati 7
3. **Supporting evidence.** Symptoms: MISSED_ERROR×14. 
   - C1-02 (Class 1, Hindi): Read 'है' as 'हे' and it was marked as read correctly. {"word": "है", "child_said": "हे", "kind": "sub", "speech_model_wrote": "हे"} · `agent_org/runs/c02/retest/C1-02`
   - C1-04 (Class 1, English): Read 'Baa' as 'Ba' and it was marked as read correctly. {"word": "Baa", "child_said": "Ba", "kind": "sub", "speech_model_wrote": "Ba baa"} · `agent_org/runs/c02/retest/C1-04`
   - C1-05 (Class 1, Hindi): Read 'મામો' as 'મામૌ' and it was marked as read correctly. {"word": "મામો", "child_said": "મામૌ", "kind": "sub", "speech_model_wrote": "મામૌ લાગે મીઠો"} · `agent_org/runs/c02/retest/C1-05`
   - C2-01 (Class 2, English): Read 'up' as 'None' and it was marked as read correctly. {"word": "up", "child_said": null, "kind": "skip", "speech_model_wrote": "big the the ant did not give"} · `agent_org/runs/c02/retest/C2-01`
4. **Root-cause hypothesis.** By design, loose() folds vowel length and nasalisation, similarity() gives a stem bonus, and skipped short function words are forgiven; this tolerates speech-model spelling noise but also accepts genuine matra/ending errors.
5. **Expected behaviour.** Product decision (human): keep tolerance for pre-primary, but for Class 2-4 report frequent matra/ending slips softly in the parent summary without interrupting the child.
6. **Technical implementation requirements.** Modules: `backend/normalize.py loose()/similarity()`, `backend/content.py _SHORT_WORDS`
   - Record 'near matches' (accepted with sim < 0.95) in the session log and summary as 'listen again' words for Class 2-4.
   - No change to live interruption behaviour.
7. **Acceptance criteria.**
   - None measurable by the simulation yet; needs the method in 8.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Summary lists near-match words in simulated Class 2-4 sessions; no change in false corrections. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P3

