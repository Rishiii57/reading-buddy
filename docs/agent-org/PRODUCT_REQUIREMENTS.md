# Product requirements: cycle c01 / baseline

Written by the AI Product Manager for the Engineering team. Status *approved* means Engineering may start; *awaiting_human_approval* needs a team decision first; *deferred* is not in this cycle. An item is resolved only when QA validates its acceptance criteria (not when code changes).

## REQ-PREPRIMARY-CONTENT: No reading material for Nursery, LKG and UKG

**Priority:** P0 (score 24.92) · **Status:** awaiting_human_approval (Touches content, privacy or model/data collection: needs a human decision.) · **Owners:** Data Engineer, Speech AI Engineer, Frontend Engineer · **Complexity:** L

1. **Problem statement.** No reading material for Nursery, LKG and UKG. Seen in 26 of 50 simulated children (52%; pre-primary reach 100%), 26 occurrences; 85% of affected children abandoned or could not start.
2. **Affected personas.** L01, L02, L03, L04, L05, L06, L07, L08, N01, N02, N03, N04, N05, N06, N07, N08, N09, N10, U01, U02, U03, U04, U05, U06, U07, U08 · by grade: Nursery 10, LKG 8, UKG 8 · by language: Hindi 9, English 9, Gujarati 8
3. **Supporting evidence.** Symptoms: NO_TEXT_FOR_MY_LEVEL×26.  Children said: “The words were too hard. I can't read those yet.”
   - L01 (LKG, Hindi): LKG child landed on a 'Grade 1-2' text; nothing in the library is marked for Nursery/LKG/UKG. {"t": 5.72, "title": "बारिश आई", "grade_tag": "Grade 1-2"} · `agent_org/runs/c01/baseline/L01`
   - L02 (LKG, English): LKG child landed on a 'Grade 2-4' text; nothing in the library is marked for Nursery/LKG/UKG. {"t": 4.94, "title": "The Busy Ant", "grade_tag": "Grade 2-4"} · `agent_org/runs/c01/baseline/L02`
   - L03 (LKG, Gujarati): LKG child landed on a 'Grade 3-4' text; nothing in the library is marked for Nursery/LKG/UKG. {"t": 4.93, "title": "મારી શાળા", "grade_tag": "Grade 3-4"} · `agent_org/runs/c01/baseline/L03`
   - L04 (LKG, English): LKG child landed on a 'Grade 2-4' text; nothing in the library is marked for Nursery/LKG/UKG. {"t": 5.29, "title": "The Busy Ant", "grade_tag": "Grade 2-4"} · `agent_org/runs/c01/baseline/L04`
4. **Root-cause hypothesis.** The library holds 12 texts for Grades 1-4 (16-37 words of continuous text). The grade filter offers Grade 1-5 only. Pre-primary children are pre-readers or emergent readers; continuous text with no pre-reading formats cannot be read, so every pre-primary session degenerates into stall prompts.
5. **Expected behaviour.** Each language offers at least 3 items per pre-primary level (Nursery: listen-and-repeat rhymes of 2-4 short lines; LKG: picture-word / letter-sound items; UKG: 3-4 word sentences), selectable from a pre-primary filter, and Buddy models each line before the child repeats it.
6. **Technical implementation requirements.** Modules: `content/*.json`, `backend/content.py`, `frontend/app.js (grade filter)`, `cache/tts`
   - Add a `level` field (nursery|lkg|ukg|1..4) to content specs and `/api/library`; keep `grade` for backward compatibility.
   - Author pre-primary items per language; Hindi/Gujarati wording must be reviewed by a native-speaking teacher before release (human approval).
   - Pre-generate Timbre clips for every line and word (backend/pregen.py) so first use is instant and cached.
   - Library UI: add Nursery/LKG/UKG chips with picture icons (non-readers).
   - Tutor: an `echo` mode for pre-primary items (Buddy reads each line, child repeats) via TutorConfig, not a new engine.
7. **Acceptance criteria.**
   - `level_mismatch_rate` <= 0.0; scope: pre-primary personas. Baseline this cycle: 0.52.
   - `coverage` >= 0.6; scope: pre-primary personas. Baseline this cycle: 0.408.
   - `stuck_rate` <= 0.1; scope: pre-primary personas. Baseline this cycle: 0.0.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Re-run all Nursery/LKG/UKG personas with the same seeds; compare level_mismatch_rate, coverage and stuck_rate; native-speaker review sign-off recorded in the decision log. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P0

## REQ-CONSENT-GATE: Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass

**Priority:** P0 (score 19.45) · **Status:** awaiting_human_approval (Touches content, privacy or model/data collection: needs a human decision.) · **Owners:** Frontend Engineer · **Complexity:** M

1. **Problem statement.** Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass. Seen in 9 of 50 simulated children (18%; pre-primary reach 15%), 16 occurrences; 78% of affected children abandoned or could not start.
2. **Affected personas.** C1-05, C2-01, C2-06, C3-06, C4-01, L03, N01, N03, U04 · by grade: Nursery 2, LKG 1, UKG 1, Class 1 1, Class 2 2, Class 3 1, Class 4 1 · by language: Hindi 2, English 2, Gujarati 5
3. **Supporting evidence.** Symptoms: CONSENT_BLOCKS_CHILD×5, CONSENT_SELF_APPROVED×4, COULD_NOT_START_SESSION×2.  Children said: “There was a box for parents, so I just ticked it myself.” / “A box came and I didn't know what it said.” / “It didn't start.”
   - C1-05 (Class 1, Hindi): A written grown-ups-only box appeared; the child could not read it and could not start. {"t": 11.7, "grade": "Class 1", "tapped": ""} · `agent_org/runs/c01/baseline/C1-05`
   - C2-01 (Class 2, English): The parent-consent box was ticked by the child; nothing stops a child from confirming they are the parent. {"t": 12.92, "grade": "Class 2"} · `agent_org/runs/c01/baseline/C2-01`
   - C2-06 (Class 2, Gujarati): The parent-consent box was ticked by the child; nothing stops a child from confirming they are the parent. {"t": 16.81, "grade": "Class 2"} · `agent_org/runs/c01/baseline/C2-06`
   - C3-06 (Class 3, Gujarati): The parent-consent box was ticked by the child; nothing stops a child from confirming they are the parent. {"t": 14.98, "grade": "Class 3"} · `agent_org/runs/c01/baseline/C3-06`
4. **Root-cause hypothesis.** askConsent() shows a written English dialog with a checkbox 'I am the child's parent or guardian'. A pre-reader cannot read it and gets no spoken explanation; any child who can read English can tick it. The consent therefore neither informs the parent nor stops the child.
5. **Expected behaviour.** A child who meets the gate hears (in the session language) that a grown-up is needed, and the screen shows a clear 'ask a grown-up' picture. The gate requires an adult-only action a young child is unlikely to complete by chance (e.g. press-and-hold plus a simple question in the parent's language), and the Demo reader stays available without consent.
6. **Technical implementation requirements.** Modules: `frontend/index.html #consentDlg`, `frontend/app.js askConsent()`
   - Replace the checkbox with an adult verification step (press-and-hold 3 s + a two-digit arithmetic question or typed year of birth), shown only once per device.
   - Play a cached Timbre phrase 'Please ask a grown-up to help you start' in the selected language when the gate opens.
   - Log (locally, no personal data) gate shown / passed / cancelled for QA.
   - Privacy wording change requires human (team) approval.
7. **Acceptance criteria.**
   - `consent_blocked_rate` <= 0.0; scope: personas without grown-up setup who cannot read English. Baseline this cycle: 0.1.
   - `consent_self_approved_rate` <= 0.0; scope: personas without grown-up setup who read English. Baseline this cycle: 0.08.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Run personas with grown_up_setup=false; check no child completes the adult step and every pre-reader hears the spoken 'ask a grown-up' message. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P0

## REQ-SPOKEN-ONBOARDING: Before a session starts, all guidance is written English; non-readers get no spoken instructions

**Priority:** P1 (score 22.04) · **Status:** approved (P1 within capacity (1/8 units).) · **Owners:** Frontend Engineer, Speech AI Engineer · **Complexity:** S

1. **Problem statement.** Before a session starts, all guidance is written English; non-readers get no spoken instructions. Seen in 35 of 50 simulated children (70%; pre-primary reach 96%), 36 occurrences; 74% of affected children abandoned or could not start.
2. **Affected personas.** C1-03, C1-05, C1-06, C2-02, C2-05, C3-02, C3-03, C3-05, C4-03, C4-05, L01, L02, L03, L04, L05, L06, L07, L08, N01, N02, N03, N04, N05, N06, N07, N08, N09, N10, U01, U02, U03, U04, U05, U07, U08 · by grade: Nursery 10, LKG 8, UKG 7, Class 1 3, Class 2 2, Class 3 3, Class 4 2 · by language: Gujarati 12, Hindi 15, English 8
3. **Supporting evidence.** Symptoms: NO_SPOKEN_GUIDANCE_BEFORE_START×35, LISTEN_FIRST_NOT_FOUND×1.  Children said: “Nobody told me what to do.” / “It didn't say what to do, it was only writing.” / “I wanted it to read to me first.”
   - C1-03 (Class 1, Gujarati): On the reading page nothing was said out loud; the only instructions were written in English, which this child cannot read. {"t": 7.3, "bubble": "Hi! I'm Buddy. Press the big microphone and read the first line out loud."} · `agent_org/runs/c01/baseline/C1-03`
   - C1-05 (Class 1, Hindi): On the reading page nothing was said out loud; the only instructions were written in English, which this child cannot read. {"t": 8.36, "bubble": "Hi! I'm Buddy. Press the big microphone and read the first line out loud."} · `agent_org/runs/c01/baseline/C1-05`
   - C1-06 (Class 1, Gujarati): On the reading page nothing was said out loud; the only instructions were written in English, which this child cannot read. {"t": 6.37, "bubble": "Hi! I'm Buddy. Press the big microphone and read the first line out loud."} · `agent_org/runs/c01/baseline/C1-06`
   - C2-02 (Class 2, Hindi): On the reading page nothing was said out loud; the only instructions were written in English, which this child cannot read. {"t": 5.98, "bubble": "Hi! I'm Buddy. Press the big microphone and read the first line out loud."} · `agent_org/runs/c01/baseline/C2-02`
4. **Root-cause hypothesis.** resetReaderUI() writes 'Press the big microphone and read the first line out loud.' into the bubble but nothing is spoken until the session starts. Pre-readers, and children who read Hindi or Gujarati but not English, cannot tell which button starts reading or that 'Listen first' exists.
5. **Expected behaviour.** On opening a text, Buddy says (in the text's language, from the Timbre cache) one short line: what the big microphone does and that the speaker button reads the poem first. Bubble text also appears in the text's language.
6. **Technical implementation requirements.** Modules: `frontend/app.js openText()/resetReaderUI()`, `backend/phrases.py`
   - Add phrases `reader_hint` per language in backend/phrases.py; expose `/api/phrase/{lang}/{key}` returning the cached clip URL.
   - On openText(), play the hint once per visit after the first user gesture (autoplay policy); never while a session runs.
   - Localise the reader bubble strings (resetReaderUI, listeningBubble, yourTurnBubble) for hi/gu.
7. **Acceptance criteria.**
   - `spoken_guidance_gap_rate` <= 0.0; scope: personas with ui_english_reading < 0.3. Baseline this cycle: 0.7.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Pre-reader personas: the reader page must emit a spoken hint before the first mic tap (observed in the agent's 'heard' channel). QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P1

## REQ-STALL-TIMING: Stall prompt fires during normal thinking pauses of slow and hesitant readers

**Priority:** P1 (score 20.03) · **Status:** approved (P1 within capacity (2/8 units).) · **Owners:** Backend Engineer, AI/ML Engineer · **Complexity:** S

1. **Problem statement.** Stall prompt fires during normal thinking pauses of slow and hesitant readers. Seen in 20 of 50 simulated children (40%; pre-primary reach 31%), 32 occurrences; 70% of affected children abandoned or could not start.
2. **Affected personas.** C1-01, C1-02, C1-03, C1-06, C2-02, C2-03, C2-04, C2-06, C3-02, C3-03, C3-04, C3-06, L01, L05, N05, N07, N10, U01, U02, U08 · by grade: Nursery 3, LKG 2, UKG 3, Class 1 4, Class 2 4, Class 3 4 · by language: English 6, Hindi 7, Gujarati 7
3. **Supporting evidence.** Symptoms: INTERRUPTED_WHILE_THINKING×20.  Children said: “I was just thinking and Buddy jumped in.” / “Buddy talked when I was thinking!”
   - C1-01 (Class 1, English): Buddy started talking 2.4 s into a planned 1.92 s thinking pause. {"t": 46.3, "paused_s": 2.4, "planned_s": 1.92, "line": 0, "buddy_kind": "stall_phrase", "next_words": "rain,"} · `agent_org/runs/c01/baseline/C1-01`
   - C1-02 (Class 1, Hindi): Buddy started talking 2.1 s into a planned 2.09 s thinking pause. {"t": 30.94, "paused_s": 2.1, "planned_s": 2.09, "line": 0, "buddy_kind": "stall_phrase", "next_words": "आई,"} · `agent_org/runs/c01/baseline/C1-02`
   - C1-03 (Class 1, Gujarati): Buddy started talking 1.8 s into a planned 2.84 s thinking pause. {"t": 32.33, "paused_s": 1.8, "planned_s": 2.84, "line": 0, "buddy_kind": "stall_phrase", "next_words": "ટપ ટપ વરસાદ"} · `agent_org/runs/c01/baseline/C1-03`
   - C1-06 (Class 1, Gujarati): Buddy started talking 2.4 s into a planned 3.31 s thinking pause. {"t": 29.46, "paused_s": 2.4, "planned_s": 3.31, "line": 0, "buddy_kind": "stall_phrase", "next_words": "ને પીળો,"} · `agent_org/runs/c01/baseline/C1-06`
4. **Root-cause hypothesis.** TutorConfig.stall_mid_s = 2.0 s is one fixed threshold for every child. Word-by-word and hesitant readers in Nursery-UKG pause 2-5 s between words while decoding, so Buddy supplies the next words before the child tries them, which removes the decoding attempt.
5. **Expected behaviour.** Buddy waits longer mid-line for young/hesitant readers and for a child who has been reading word by word, while still prompting a genuinely stuck child within a few seconds.
6. **Technical implementation requirements.** Modules: `backend/tutor.py TutorConfig.stall_mid_s / tick()`, `backend/main.py Session`
   - Make stall thresholds adaptive: stall_mid_s = clamp(k x the reader's median inter-word gap observed in this session, 2.0, 5.0), with k configurable (default 2.0).
   - Add a `pace` profile (young|standard) to TutorConfig with stall_mid_s 3.5 s for young; select via the text level (pre-primary/Grade 1) until per-child profiles exist.
   - Never fire a stall prompt within 1.0 s of a transcript that advanced the pointer.
   - Keep eval/replay stall detection within 4.0 s on the stall test set (no regression in catching real stalls).
7. **Acceptance criteria.**
   - `stall_interruptions_per_agent` <= 0.5 × baseline; scope: affected personas. Baseline this cycle: 0.62.
   - `stuck_rate` <= baseline (no worse); scope: no new stuck children. Baseline this cycle: 0.0.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Re-run hesitant/word-by-word personas (same seeds) before/after; run eval.replay and check 'stalls prompted' stays >= 11/12. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P1

## REQ-MIC-TOGGLE: Tapping the big microphone during a session pauses it

**Priority:** P2 (score 18.82) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Frontend Engineer · **Complexity:** S

1. **Problem statement.** Tapping the big microphone during a session pauses it. Seen in 19 of 50 simulated children (38%; pre-primary reach 42%), 22 occurrences; 79% of affected children abandoned or could not start.
2. **Affected personas.** C1-01, C1-06, C2-02, C2-03, C2-04, C2-05, C2-06, C3-01, L03, L05, L06, N05, N06, N09, U01, U02, U05, U06, U08 · by grade: Nursery 3, LKG 3, UKG 5, Class 1 2, Class 2 5, Class 3 1 · by language: English 5, Gujarati 8, Hindi 6
3. **Supporting evidence.** Symptoms: MIC_TAP_PAUSED_SESSION×19, HARD_TO_RESUME×1.  Children said: “I pressed the mic to talk and it stopped!” / “I pressed the microphone and it paused.” / “It stopped and I didn't know how to make it go.”
   - C1-01 (Class 1, English): Tapped the big microphone to talk; the session paused instead. {"t": 29.62, "bubble": "Press play when you're ready to keep reading."} · `agent_org/runs/c01/baseline/C1-01`
   - C1-06 (Class 1, Gujarati): Tapped the big microphone to talk; the session paused instead. {"t": 53.4, "bubble": "Press play when you're ready to keep reading."} · `agent_org/runs/c01/baseline/C1-06`
   - C2-02 (Class 2, Hindi): Tapped the big microphone to talk; the session paused instead. {"t": 69.96, "bubble": "Press play when you're ready to keep reading."} · `agent_org/runs/c01/baseline/C2-02`
   - C2-03 (Class 2, Gujarati): Tapped the big microphone to talk; the session paused instead. {"t": 35.21, "bubble": "Press play when you're ready to keep reading."} · `agent_org/runs/c01/baseline/C2-03`
4. **Root-cause hypothesis.** micBtn.onclick toggles pause when a session is running. Young children tap the microphone to talk (the common mental model of a mic button), which silently pauses the session; the paused state is shown only as text and an icon change.
5. **Expected behaviour.** Tapping the mic while a session is listening does not pause; Buddy says a short 'I'm listening, go ahead!' (cached). Pausing stays available via the Pause button and Escape.
6. **Technical implementation requirements.** Modules: `frontend/app.js $('micBtn').onclick / togglePause()`
   - Change micBtn.onclick: while running and not paused, a tap plays a cached 'listening' cue and does not call togglePause(); while paused, a tap resumes.
   - Keep the separate Pause button and Escape key behaviour.
7. **Acceptance criteria.**
   - `mic_tap_pause_rate` <= 0.0; scope: all personas. Baseline this cycle: 0.38.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Personas with p_tap_mic_to_talk > 0, same seeds: no MIC_TAP_PAUSED_SESSION; Pause button still pauses (QA functional check). QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-MIDLINE-CORRECTION: A slip followed by a thinking pause triggers word practice mid-line

**Priority:** P2 (score 18.49) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Backend Engineer · **Complexity:** S

1. **Problem statement.** A slip followed by a thinking pause triggers word practice mid-line. Seen in 13 of 50 simulated children (26%; pre-primary reach 31%), 16 occurrences; 77% of affected children abandoned or could not start.
2. **Affected personas.** C1-01, C1-02, C1-03, C3-04, C3-06, L03, L05, L06, L07, N02, N06, N09, U06 · by grade: Nursery 3, LKG 4, UKG 1, Class 1 3, Class 3 2 · by language: English 4, Hindi 3, Gujarati 6
3. **Supporting evidence.** Symptoms: INTERRUPTED_WHILE_THINKING×13.  Children said: “Buddy talked when I was thinking!” / “I was just thinking and Buddy jumped in.”
   - C1-01 (Class 1, English): Buddy started talking 2.4 s into a planned 1.92 s thinking pause. {"t": 55.29, "paused_s": 2.1, "planned_s": 3.26, "line": 1, "buddy_kind": "fix_word", "next_words": "the roof and"} · `agent_org/runs/c01/baseline/C1-01`
   - C1-02 (Class 1, Hindi): Buddy started talking 2.1 s into a planned 2.09 s thinking pause. {"t": 66.41, "paused_s": 2.3, "planned_s": 2.51, "line": 1, "buddy_kind": "fix_word", "next_words": "ठंडी हवा भी"} · `agent_org/runs/c01/baseline/C1-02`
   - C1-03 (Class 1, Gujarati): Buddy started talking 1.8 s into a planned 2.84 s thinking pause. {"t": 40.49, "paused_s": 2.3, "planned_s": 2.14, "line": 0, "buddy_kind": "fix_word", "next_words": "ટપ વરસાદ પડે,"} · `agent_org/runs/c01/baseline/C1-03`
   - C3-04 (Class 3, English): Buddy started talking 2.5 s into a planned 2.25 s thinking pause. {"t": 136.42, "paused_s": 2.9, "planned_s": 2.07, "line": 3, "buddy_kind": "fix_word", "next_words": "the tree and"} · `agent_org/runs/c01/baseline/C3-04`
4. **Root-cause hypothesis.** tick() calls _check_line() as soon as idle >= stall_mid_s (2.0 s) when the line already has an error, so a child who misreads a word and pauses to think (or to self-correct) is pulled into word practice before finishing the line. Self-correction after 2 s is never possible.
5. **Expected behaviour.** After a slip, Buddy lets the child finish the line (or pause up to the stall threshold for that child), then practises the word.
6. **Technical implementation requirements.** Modules: `backend/tutor.py tick() -> _check_line()`
   - In tick(), when errors exist mid-line, wait max(stall threshold, self_correct_s + 1.5 s) before _check_line().
   - If a later transcript in the same line re-reads the slipped word correctly, clear it from line_errors (self-correction).
7. **Acceptance criteria.**
   - `correction_interruptions_per_agent` <= 0.5 × baseline; scope: affected personas. Baseline this cycle: 0.32.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Same personas and seeds before/after; unit test: slip + 2.5 s pause + continue does not trigger a correction mid-line. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-FALSE-CORRECTION-TUTOR: Correctly read words flagged for practice (tutor/aligner)

**Priority:** P2 (score 17.18) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** NLP Engineer, AI/ML Engineer · **Complexity:** M

1. **Problem statement.** Correctly read words flagged for practice (tutor/aligner). Seen in 4 of 50 simulated children (8%; pre-primary reach 8%), 4 occurrences; 75% of affected children abandoned or could not start.
2. **Affected personas.** C2-02, C2-03, N09, U07 · by grade: Nursery 1, UKG 1, Class 2 2 · by language: Hindi 1, Gujarati 3
3. **Supporting evidence.** Symptoms: FALSE_CORRECTION×4.  Children said: “Buddy said I got a word wrong but I read it right.” / “But I said it right!”
   - C2-02 (Class 2, Hindi): Read 'मेंढक' correctly but Buddy asked to practise it. {"t": 36.86, "word": "मेंढक", "child_said": "मेंढक", "speech_model_wrote": "मेंढक गाते मीठे गाने"} · `agent_org/runs/c01/baseline/C2-02`
   - C2-03 (Class 2, Gujarati): Read 'તે' correctly but Buddy asked to practise it. {"t": 92.06, "word": "તે", "child_said": "તે", "speech_model_wrote": "તે રોજ સવારે ધાણા શોધવા જથી"} · `agent_org/runs/c01/baseline/C2-03`
   - N09 (Nursery, Gujarati): Read 'patter' correctly but Buddy asked to practise it. {"t": 40.65, "word": "patter", "child_said": "patter", "speech_model_wrote": "put patter"} · `agent_org/runs/c01/baseline/N09`
   - U07 (UKG, Gujarati): Read 'મારો' correctly but Buddy asked to practise it. {"t": 37.6, "word": "મારો", "child_said": "મારો", "speech_model_wrote": "મારો પતંગ લાલ ને ને પીળૌ પીળૌ"} · `agent_org/runs/c01/baseline/U07`
4. **Root-cause hypothesis.** The strict aligner (match_thr 0.85) or the muted-fragment logic marks words as errors when the transcript is split or re-read; check each case against the child's ground truth.
5. **Expected behaviour.** < 1 false correction per 50 correctly read words in simulated sessions and in eval.replay.
6. **Technical implementation requirements.** Modules: `backend/aligner.py`, `backend/tutor.py _read()`
   - Inspect each logged case; add regression fixtures to tests/test_tutor.py; adjust alignment only with replay evidence.
7. **Acceptance criteria.**
   - `false_corrections_per_agent` <= 0.5 × baseline; scope: affected personas. Baseline this cycle: 0.16.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** eval.replay false corrections per 50 words must not rise; simulated sessions before/after. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-NAVIGATION: Children cannot find a text or leave the reading page by accident

**Priority:** P2 (score 16.8) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Frontend Engineer · **Complexity:** M

1. **Problem statement.** Children cannot find a text or leave the reading page by accident. Seen in 12 of 50 simulated children (24%; pre-primary reach 35%), 12 occurrences; 50% of affected children abandoned or could not start.
2. **Affected personas.** C1-02, C1-05, C4-05, L01, L02, L04, L08, N03, N08, U03, U05, U06 · by grade: Nursery 2, LKG 4, UKG 3, Class 1 2, Class 4 1 · by language: Hindi 8, English 3, Gujarati 1
3. **Supporting evidence.** Symptoms: LEFT_READING_BY_ACCIDENT×12.  Children said: “Where did my poem go?” / “I pressed something and the poem went away.”
   - C1-02 (Class 1, Hindi): A curious tap on 'Library' left the reading page. {"t": 80.82, "tapped": "Library", "view": "view-library"} · `agent_org/runs/c01/baseline/C1-02`
   - C1-05 (Class 1, Hindi): Tapped something that left the reading page before starting. {"t": 14.33, "view": "view-library"} · `agent_org/runs/c01/baseline/C1-05`
   - C4-05 (Class 4, Hindi): A curious tap on 'End' left the reading page. {"t": 81.63, "tapped": "End", "view": "view-summary"} · `agent_org/runs/c01/baseline/C4-05`
   - L01 (LKG, Hindi): A curious tap on 'Library' left the reading page. {"t": 30.1, "tapped": "Library", "view": "view-library"} · `agent_org/runs/c01/baseline/L01`
4. **Root-cause hypothesis.** Back and End are always-visible buttons next to the reading area; a stray tap leaves or ends the session with no confirmation.
5. **Expected behaviour.** Leaving a running session needs a confirmation that is spoken and pictorial; End during the first 10 s asks again.
6. **Technical implementation requirements.** Modules: `frontend/index.html reader-bar (Back/End)`, `frontend/app.js route()`
   - Confirm dialog (child-friendly, spoken) for Back/End while a session runs.
7. **Acceptance criteria.**
   - `abandon_rate` <= 0.8 × baseline; scope: all personas. Baseline this cycle: 0.68.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** All personas, same seeds. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-DRILL-LOOP: Word practice and line repetition loop on the same word or line

**Priority:** P2 (score 16.68) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Backend Engineer, AI/ML Engineer · **Complexity:** S

1. **Problem statement.** Word practice and line repetition loop on the same word or line. Seen in 3 of 50 simulated children (6%; pre-primary reach 0%), 3 occurrences; 100% of affected children abandoned or could not start.
2. **Affected personas.** C1-01, C1-04, C2-05 · by grade: Class 1 2, Class 2 1 · by language: English 2, Hindi 1
3. **Supporting evidence.** Symptoms: SAME_WORD_ASKED_AGAIN_AND_AGAIN×3.  Children said: “Buddy made me say the same word again and again.”
   - C1-01 (Class 1, English): Asked to say 'On' 3 times. {"t": 68.64, "word": "On", "times": 3} · `agent_org/runs/c01/baseline/C1-01`
   - C1-04 (Class 1, English): Asked to say 'his' 3 times. {"t": 50.14, "word": "his", "times": 3} · `agent_org/runs/c01/baseline/C1-04`
   - C2-05 (Class 2, Hindi): Asked to say 'घर' 3 times. {"t": 100.95, "word": "घर", "times": 3} · `agent_org/runs/c01/baseline/C2-05`
4. **Root-cause hypothesis.** A drill word is repeated until recognised and a line can be re-read until it is error-free, with up to max_line_mistakes = 10 mistakes per line before moving on. For young children ten failed tries on one line is far past frustration.
5. **Expected behaviour.** At most 2 attempts per practice word (then Buddy says it together with the child and moves on), and max_line_mistakes scaled by level (pre-primary/Grade 1: 4; others: 6).
6. **Technical implementation requirements.** Modules: `backend/tutor.py _drill_attempt(), _add_mistakes(), TutorConfig.max_line_mistakes`
   - Add TutorConfig.max_word_attempts (default 2): after that, mark the word 'helped', say `word_ok` and continue.
   - Make max_line_mistakes level-dependent through the pace profile.
7. **Acceptance criteria.**
   - `drill_repeat_rate` <= 0.0; scope: all personas. Baseline this cycle: 0.06.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Personas with low accuracy before/after; unit test for the attempt cap. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-FALSE-CORRECTION-STT: Correct reading misheard by the speech model (child voices)

**Priority:** P2 (score 15.93) · **Status:** awaiting_human_approval (Touches content, privacy or model/data collection: needs a human decision.) · **Owners:** Speech AI Engineer, AI/ML Engineer · **Complexity:** L

1. **Problem statement.** Correct reading misheard by the speech model (child voices). Seen in 4 of 50 simulated children (8%; pre-primary reach 4%), 4 occurrences; 50% of affected children abandoned or could not start.
2. **Affected personas.** C3-03, C4-04, C4-06, L07 · by grade: LKG 1, Class 3 1, Class 4 2 · by language: Gujarati 2, English 2
3. **Supporting evidence.** Symptoms: FALSE_CORRECTION_STT×4.  Children said: “I read it right but Buddy heard something else.” / “But I said it right!”
   - C3-03 (Class 3, Gujarati): Read 'મારી' correctly but Buddy asked to practise it (the speech model wrote it differently). {"t": 30.26, "word": "મારી", "child_said": "મારી", "speech_model_wrote": "માડી શાળા બહુ સુંદર છે"} · `agent_org/runs/c01/baseline/C3-03`
   - C4-04 (Class 4, English): Read 'It' correctly but Buddy asked to practise it (the speech model wrote it differently). {"t": 66.16, "word": "It", "child_said": "It", "speech_model_wrote": "id carried a grain"} · `agent_org/runs/c01/baseline/C4-04`
   - C4-06 (Class 4, Gujarati): Read 'વાર્તા' correctly but Buddy asked to practise it (the speech model wrote it differently). {"t": 70.42, "word": "વાર્તા", "child_said": "વાર્તા", "speech_model_wrote": "મારા શિક્ષક અમને બાર્તા"} · `agent_org/runs/c01/baseline/C4-06`
   - L07 (LKG, English): Read 'ટપ' correctly but Buddy asked to practise it (the speech model wrote it differently). {"t": 62.61, "word": "ટપ", "child_said": "ટપ", "speech_model_wrote": "ઠપ"} · `agent_org/runs/c01/baseline/L07`
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

## REQ-LONG-INTRO: Buddy's opening talk is long before the child gets a turn

**Priority:** P2 (score 15.03) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Backend Engineer · **Complexity:** S

1. **Problem statement.** Buddy's opening talk is long before the child gets a turn. Seen in 35 of 50 simulated children (70%; pre-primary reach 62%), 35 occurrences; 60% of affected children abandoned or could not start.
2. **Affected personas.** C1-02, C1-03, C1-04, C1-06, C2-01, C2-02, C2-03, C2-04, C2-05, C2-06, C3-01, C3-02, C3-03, C3-05, C3-06, C4-01, C4-02, C4-05, C4-06, L01, L03, L04, L06, L07, N02, N04, N05, N06, N07, N10, U01, U02, U05, U07, U08 · by grade: Nursery 6, LKG 5, UKG 5, Class 1 4, Class 2 6, Class 3 5, Class 4 4 · by language: Hindi 12, Gujarati 12, English 11
3. **Supporting evidence.** Symptoms: LONG_TUTOR_TALK×35.  Children said: “Buddy talks a lot before I get to read.” / “Buddy talked too long.”
   - C1-02 (Class 1, Hindi): Buddy talked for over 12 s in one go before the child could read. {"t": 24.93, "talk_s": 12.1} · `agent_org/runs/c01/baseline/C1-02`
   - C1-03 (Class 1, Gujarati): Buddy talked for over 12 s in one go before the child could read. {"t": 22.16, "talk_s": 12.1} · `agent_org/runs/c01/baseline/C1-03`
   - C1-04 (Class 1, English): Buddy talked for over 12 s in one go before the child could read. {"t": 22.84, "talk_s": 12.1} · `agent_org/runs/c01/baseline/C1-04`
   - C1-06 (Class 1, Gujarati): Buddy talked for over 12 s in one go before the child could read. {"t": 21.97, "talk_s": 12.5} · `agent_org/runs/c01/baseline/C1-06`
4. **Root-cause hypothesis.** start() chains welcome + 'today we're going to read' + title + 'listen carefully' + line 1 + 'your turn' into one ~13 s utterance; short attention spans are spent before reading starts.
5. **Expected behaviour.** First turn within ~8 s: one greeting phrase + line demonstration + 'your turn'; the title is shown, and the full welcome is used only on a child's first session.
6. **Technical implementation requirements.** Modules: `backend/tutor.py start()`
   - Drop `today` + title from start() after the first session on the device (client sends `first_visit`), or always for pre-primary items.
   - Merge `listen_first` and `read_with_me` into one short phrase per language.
7. **Acceptance criteria.**
   - `intro_s_median` <= 9.0; scope: all personas. Baseline this cycle: 14.0.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Median intro_s before/after on the same persona set. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-LANGUAGE-SELECTION: Children end up in, or hear, a language they did not choose

**Priority:** P2 (score 14.6) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Frontend Engineer · **Complexity:** S

1. **Problem statement.** Children end up in, or hear, a language they did not choose. Seen in 12 of 50 simulated children (24%; pre-primary reach 35%), 32 occurrences; 100% of affected children abandoned or could not start.
2. **Affected personas.** C1-04, C1-05, C2-04, L06, L07, N01, N02, N03, N04, N05, N09, N10 · by grade: Nursery 7, LKG 2, Class 1 2, Class 2 1 · by language: English 6, Hindi 3, Gujarati 3
3. **Supporting evidence.** Symptoms: BUDDY_LANGUAGE_NOT_UNDERSTOOD×8, WRONG_LANGUAGE_TEXT×11.  Children said: “This isn't my language!” / “I don't know what Buddy said.” / “Buddy talked in a language I don't really know.”
   - C1-04 (Class 1, English): Buddy spoke in en-IN, which this child understands poorly (0.5). {"t": 10.73, "kind": "intro", "said": "Hello! Welcome to Reading Buddy! Today we're going to read Ravi and the Mango Tr"} · `agent_org/runs/c01/baseline/C1-04`
   - C1-05 (Class 1, Hindi): Wanted hi-IN but ended up on a gu-IN text. {"t": 8.29, "wanted": "hi-IN", "got": "gu-IN", "title": "મારો પતંગ"} · `agent_org/runs/c01/baseline/C1-05`
   - C2-04 (Class 2, English): Wanted en-IN but ended up on a hi-IN text. {"t": 18.92, "wanted": "en-IN", "got": "hi-IN", "title": "चिड़िया का घोंसला"} · `agent_org/runs/c01/baseline/C2-04`
   - C2-04 (Class 2, English): Buddy spoke in hi-IN, which this child understands poorly (0.0). {"t": 22.56, "kind": "intro", "said": "नमस्ते! रीडिंग बडी में तुम्हारा स्वागत है! आज हम पढ़ेंगे चिड़िया का घोंसला ध्यान"} · `agent_org/runs/c01/baseline/C2-04`
4. **Root-cause hypothesis.** First-visit default language is Gujarati; language cards and tabs rely on reading script names; non-readers pick by picture and land in another language.
5. **Expected behaviour.** Default language follows the browser/device locale (hi -> Hindi, gu -> Gujarati, else English); each language card speaks its name when tapped once (tap again to open).
6. **Technical implementation requirements.** Modules: `frontend/app.js app.lang default 'gu-IN', library tabs`
   - Use navigator.languages to pick the first-visit default.
   - Language cards: first tap plays a cached clip of the language name.
7. **Acceptance criteria.**
   - `wrong_language_rate` <= 0.5 × baseline; scope: all personas. Baseline this cycle: 0.22.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** All personas, same seeds. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-TALK-OVER-BUDDY: What a child says while Buddy is talking is silently discarded

**Priority:** P2 (score 14.56) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Speech AI Engineer, Frontend Engineer · **Complexity:** M

1. **Problem statement.** What a child says while Buddy is talking is silently discarded. Seen in 26 of 50 simulated children (52%; pre-primary reach 38%), 46 occurrences; 65% of affected children abandoned or could not start.
2. **Affected personas.** C1-01, C1-03, C1-06, C2-01, C2-02, C2-03, C2-06, C3-01, C3-02, C3-04, C3-05, C3-06, C4-01, C4-02, C4-04, C4-05, L07, N04, N05, N07, N09, N10, U02, U06, U07, U08 · by grade: Nursery 5, LKG 1, UKG 4, Class 1 3, Class 2 4, Class 3 5, Class 4 4 · by language: English 12, Gujarati 7, Hindi 7
3. **Supporting evidence.** Symptoms: SPEECH_IGNORED_WHILE_BUDDY_TALKS×26.  Children said: “Buddy didn't hear me when I was talking.” / “I said it but Buddy didn't hear me!”
   - C1-01 (Class 1, English): 4 word(s) the child said were not heard because Buddy was talking or the session was paused. {"t": 27.68, "said": "Pitter patter falls the run", "heard": "run"} · `agent_org/runs/c01/baseline/C1-01`
   - C1-03 (Class 1, Gujarati): 2 word(s) the child said were not heard because Buddy was talking or the session was paused. {"t": 16.23, "said": "ટપ ઠપ", "heard": ""} · `agent_org/runs/c01/baseline/C1-03`
   - C1-06 (Class 1, Gujarati): 3 word(s) the child said were not heard because Buddy was talking or the session was paused. {"t": 65.86, "said": "આકાશે ઊડે રંગીલો", "heard": ""} · `agent_org/runs/c01/baseline/C1-06`
   - C2-01 (Class 2, English): 7 word(s) the child said were not heard because Buddy was talking or the session was paused. {"t": 23.06, "said": "A small ant walk across tree floor", "heard": ""} · `agent_org/runs/c01/baseline/C2-01`
4. **Root-cause hypothesis.** The mic is zeroed while Buddy speaks (to avoid echo). Eager readers start the next line during praise or the line demonstration; their words never reach the speech model and nothing tells them.
5. **Expected behaviour.** Short praise is interruptible: if the child starts speaking (local level detector), Buddy's praise clip stops and the mic opens. For non-interruptible speech (demonstrations), a visible/audible 'my turn first' cue.
6. **Technical implementation requirements.** Modules: `frontend/app.js startMic() mute while tutorSpeaking`, `frontend/app.js playSay()`
   - Client-side energy VAD on the raw mic stream while muted; if speech > 300 ms during a `praise` say, stop playback, send audio_done, unmute.
   - Mark say kinds as interruptible (praise, keep_going) vs not (intro demonstration, repeat_line, fix_*).
7. **Acceptance criteria.**
   - `unheard_words_per_agent` <= 0.5 × baseline; scope: affected personas. Baseline this cycle: 3.44.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Fast-reader personas (high p_talk_over_buddy) before/after; echo safety checked by a consenting adult on a laptop speaker (manual). QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-REPLAY: No way to hear a line again during reading

**Priority:** P3 (score 12.53) · **Status:** deferred (P3: below the approval line this cycle.) · **Owners:** Frontend Engineer, Backend Engineer · **Complexity:** S

1. **Problem statement.** No way to hear a line again during reading. Seen in 4 of 50 simulated children (8%; pre-primary reach 12%), 4 occurrences; 75% of affected children abandoned or could not start.
2. **Affected personas.** C3-05, L06, N06, U08 · by grade: Nursery 1, LKG 1, UKG 1, Class 3 1 · by language: Hindi 2, Gujarati 2
3. **Supporting evidence.** Symptoms: NO_REPLAY_CONTROL×4.  Children said: “I want to hear it again!” / “I wanted Buddy to read the line again but there was no button.”
   - C3-05 (Class 3, Hindi): Wanted Buddy to read the line again, but there is no button for that while reading ('Listen first' is switched off during a session). {"t": 24.06, "visible": ["Reading Buddy", "Home", "Library", "About", "Back", "Pause", "End", "Pause"]} · `agent_org/runs/c01/baseline/C3-05`
   - L06 (LKG, Gujarati): Wanted Buddy to read the line again, but there is no button for that while reading ('Listen first' is switched off during a session). {"t": 33.03, "visible": ["Reading Buddy", "Home", "Library", "About", "Back", "Pause", "End", "Pause"]} · `agent_org/runs/c01/baseline/L06`
   - N06 (Nursery, Gujarati): Wanted Buddy to read the line again, but there is no button for that while reading ('Listen first' is switched off during a session). {"t": 25.58, "visible": ["Reading Buddy", "Home", "Library", "About", "Back", "Pause", "End", "Pause"]} · `agent_org/runs/c01/baseline/N06`
   - U08 (UKG, Hindi): Wanted Buddy to read the line again, but there is no button for that while reading ('Listen first' is switched off during a session). {"t": 34.88, "visible": ["Reading Buddy", "Home", "Library", "About", "Back", "Pause", "End", "Pause"]} · `agent_org/runs/c01/baseline/U08`
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

**Priority:** P3 (score 10.91) · **Status:** awaiting_human_approval (Touches content, privacy or model/data collection: needs a human decision.) · **Owners:** NLP Engineer · **Complexity:** M

1. **Problem statement.** Some misreadings are accepted as correct (vowel length, matras, word endings, small words). Seen in 10 of 50 simulated children (20%; pre-primary reach 8%), 19 occurrences; 50% of affected children abandoned or could not start.
2. **Affected personas.** C1-03, C1-04, C2-01, C2-02, C3-02, C3-03, C4-02, C4-03, L06, U07 · by grade: LKG 1, UKG 1, Class 1 2, Class 2 2, Class 3 2, Class 4 2 · by language: Gujarati 5, English 3, Hindi 2
3. **Supporting evidence.** Symptoms: MISSED_ERROR×10. 
   - C1-03 (Class 1, Gujarati): Read 'ટપ' as 'None' and it was marked as read correctly. {"word": "ટપ", "child_said": null, "kind": "skip", "speech_model_wrote": ""} · `agent_org/runs/c01/baseline/C1-03`
   - C1-04 (Class 1, English): Read 'Ravi' as 'ran' and it was marked as read correctly. {"word": "Ravi", "child_said": "ran", "kind": "sub", "speech_model_wrote": "ran haa a"} · `agent_org/runs/c01/baseline/C1-04`
   - C2-01 (Class 2, English): Read 'small' as 'smal' and it was marked as read correctly. {"word": "small", "child_said": "smal", "kind": "sub", "speech_model_wrote": "A smal ant walked walked across the floor"} · `agent_org/runs/c01/baseline/C2-01`
   - C2-02 (Class 2, Hindi): Read 'भी' as 'भि' and it was marked as read correctly. {"word": "भी", "child_said": "भि", "kind": "sub", "speech_model_wrote": "टंडी ठंडी ठंडी हवा भि आई"} · `agent_org/runs/c01/baseline/C2-02`
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

