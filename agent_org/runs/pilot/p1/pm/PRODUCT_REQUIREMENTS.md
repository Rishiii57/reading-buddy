# Product requirements: cycle pilot / p1

Written by the AI Product Manager for the Engineering team. Status *approved* means Engineering may start; *awaiting_human_approval* needs a team decision first; *deferred* is not in this cycle. An item is resolved only when QA validates its acceptance criteria (not when code changes).

## REQ-PREPRIMARY-CONTENT: No reading material for Nursery, LKG and UKG

**Priority:** P0 (score 25.64) · **Status:** awaiting_human_approval (Touches content, privacy or model/data collection: needs a human decision.) · **Owners:** Data Engineer, Speech AI Engineer, Frontend Engineer · **Complexity:** L

1. **Problem statement.** No reading material for Nursery, LKG and UKG. Seen in 3 of 5 simulated children (60%; pre-primary reach 100%), 3 occurrences; 100% of affected children abandoned or could not start.
2. **Affected personas.** L01, N01, U01 · by grade: Nursery 1, LKG 1, UKG 1 · by language: Hindi 1, English 1, Gujarati 1
3. **Supporting evidence.** Symptoms: NO_TEXT_FOR_MY_LEVEL×3.  Children said: “The words were too hard. I can't read those yet.”
   - L01 (LKG, Hindi): LKG child landed on a 'Grade 1-2' text; nothing in the library is marked for Nursery/LKG/UKG. {"t": 5.24, "title": "बारिश आई", "grade_tag": "Grade 1-2"} · `agent_org/runs/pilot/p1/L01`
   - N01 (Nursery, English): Nursery child landed on a 'Grade 1-2' text; nothing in the library is marked for Nursery/LKG/UKG. {"t": 5.3, "title": "बारिश आई", "grade_tag": "Grade 1-2"} · `agent_org/runs/pilot/p1/N01`
   - U01 (UKG, Gujarati): UKG child landed on a 'Grade 1' text; nothing in the library is marked for Nursery/LKG/UKG. {"t": 4.74, "title": "મારો પતંગ", "grade_tag": "Grade 1"} · `agent_org/runs/pilot/p1/U01`
4. **Root-cause hypothesis.** The library holds 12 texts for Grades 1-4 (16-37 words of continuous text). The grade filter offers Grade 1-5 only. Pre-primary children are pre-readers or emergent readers; continuous text with no pre-reading formats cannot be read, so every pre-primary session degenerates into stall prompts.
5. **Expected behaviour.** Each language offers at least 3 items per pre-primary level (Nursery: listen-and-repeat rhymes of 2-4 short lines; LKG: picture-word / letter-sound items; UKG: 3-4 word sentences), selectable from a pre-primary filter, and Buddy models each line before the child repeats it.
6. **Technical implementation requirements.** Modules: `content/*.json`, `backend/content.py`, `frontend/app.js (grade filter)`, `cache/tts`
   - Add a `level` field (nursery|lkg|ukg|1..4) to content specs and `/api/library`; keep `grade` for backward compatibility.
   - Author pre-primary items per language; Hindi/Gujarati wording must be reviewed by a native-speaking teacher before release (human approval).
   - Pre-generate Timbre clips for every line and word (backend/pregen.py) so first use is instant and cached.
   - Library UI: add Nursery/LKG/UKG chips with picture icons (non-readers).
   - Tutor: an `echo` mode for pre-primary items (Buddy reads each line, child repeats) via TutorConfig, not a new engine.
7. **Acceptance criteria.**
   - `level_mismatch_rate` <= 0.0; scope: pre-primary personas. Baseline this cycle: 0.6.
   - `coverage` >= 0.6; scope: pre-primary personas. Baseline this cycle: 0.373.
   - `stuck_rate` <= 0.1; scope: pre-primary personas. Baseline this cycle: 0.0.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Re-run all Nursery/LKG/UKG personas with the same seeds; compare level_mismatch_rate, coverage and stuck_rate; native-speaker review sign-off recorded in the decision log. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P0

## REQ-CONSENT-GATE: Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass

**Priority:** P0 (score 22.13) · **Status:** awaiting_human_approval (Touches content, privacy or model/data collection: needs a human decision.) · **Owners:** Frontend Engineer · **Complexity:** M

1. **Problem statement.** Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass. Seen in 3 of 5 simulated children (60%; pre-primary reach 33%), 6 occurrences; 67% of affected children abandoned or could not start.
2. **Affected personas.** C2-01, C4-01, N01 · by grade: Nursery 1, Class 2 1, Class 4 1 · by language: English 2, Hindi 1
3. **Supporting evidence.** Symptoms: CONSENT_SELF_APPROVED×2, CONSENT_BLOCKS_CHILD×1, COULD_NOT_START_SESSION×1.  Children said: “There was a box for parents, so I just ticked it myself.” / “A box came and I didn't know what it said.” / “It didn't start.”
   - C2-01 (Class 2, English): The parent-consent box was ticked by the child; nothing stops a child from confirming they are the parent. {"t": 11.89, "grade": "Class 2"} · `agent_org/runs/pilot/p1/C2-01`
   - C4-01 (Class 4, Hindi): The parent-consent box was ticked by the child; nothing stops a child from confirming they are the parent. {"t": 11.62, "grade": "Class 4"} · `agent_org/runs/pilot/p1/C4-01`
   - N01 (Nursery, English): A written grown-ups-only box appeared; the child could not read it and could not start. {"t": 17.68, "grade": "Nursery", "tapped": "Not now"} · `agent_org/runs/pilot/p1/N01`
   - N01 (Nursery, English): Never managed to start a reading session. {"t": 22.64, "tries": 3} (follows CONSENT_BLOCKS_CHILD) · `agent_org/runs/pilot/p1/N01`
4. **Root-cause hypothesis.** askConsent() shows a written English dialog with a checkbox 'I am the child's parent or guardian'. A pre-reader cannot read it and gets no spoken explanation; any child who can read English can tick it. The consent therefore neither informs the parent nor stops the child.
5. **Expected behaviour.** A child who meets the gate hears (in the session language) that a grown-up is needed, and the screen shows a clear 'ask a grown-up' picture. The gate requires an adult-only action a young child is unlikely to complete by chance (e.g. press-and-hold plus a simple question in the parent's language), and the Demo reader stays available without consent.
6. **Technical implementation requirements.** Modules: `frontend/index.html #consentDlg`, `frontend/app.js askConsent()`
   - Replace the checkbox with an adult verification step (press-and-hold 3 s + a two-digit arithmetic question or typed year of birth), shown only once per device.
   - Play a cached Timbre phrase 'Please ask a grown-up to help you start' in the selected language when the gate opens.
   - Log (locally, no personal data) gate shown / passed / cancelled for QA.
   - Privacy wording change requires human (team) approval.
7. **Acceptance criteria.**
   - `consent_blocked_rate` <= 0.0; scope: personas without grown-up setup who cannot read English. Baseline this cycle: 0.2.
   - `consent_self_approved_rate` <= 0.0; scope: personas without grown-up setup who read English. Baseline this cycle: 0.4.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Run personas with grown_up_setup=false; check no child completes the adult step and every pre-reader hears the spoken 'ask a grown-up' message. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P0

## REQ-SPOKEN-ONBOARDING: Before a session starts, all guidance is written English; non-readers get no spoken instructions

**Priority:** P1 (score 22.54) · **Status:** approved (P1 within capacity (1/8 units).) · **Owners:** Frontend Engineer, Speech AI Engineer · **Complexity:** S

1. **Problem statement.** Before a session starts, all guidance is written English; non-readers get no spoken instructions. Seen in 3 of 5 simulated children (60%; pre-primary reach 100%), 3 occurrences; 100% of affected children abandoned or could not start.
2. **Affected personas.** L01, N01, U01 · by grade: Nursery 1, LKG 1, UKG 1 · by language: Hindi 1, English 1, Gujarati 1
3. **Supporting evidence.** Symptoms: NO_SPOKEN_GUIDANCE_BEFORE_START×3.  Children said: “Nobody told me what to do.”
   - L01 (LKG, Hindi): On the reading page nothing was said out loud; the only instructions were written in English, which this child cannot read. {"t": 5.33, "bubble": "Hi! I'm Buddy. Press the big microphone and read the first line out loud."} · `agent_org/runs/pilot/p1/L01`
   - N01 (Nursery, English): On the reading page nothing was said out loud; the only instructions were written in English, which this child cannot read. {"t": 5.35, "bubble": "Hi! I'm Buddy. Press the big microphone and read the first line out loud."} · `agent_org/runs/pilot/p1/N01`
   - U01 (UKG, Gujarati): On the reading page nothing was said out loud; the only instructions were written in English, which this child cannot read. {"t": 4.74, "bubble": "Hi! I'm Buddy. Press the big microphone and read the first line out loud."} · `agent_org/runs/pilot/p1/U01`
4. **Root-cause hypothesis.** resetReaderUI() writes 'Press the big microphone and read the first line out loud.' into the bubble but nothing is spoken until the session starts. Pre-readers, and children who read Hindi or Gujarati but not English, cannot tell which button starts reading or that 'Listen first' exists.
5. **Expected behaviour.** On opening a text, Buddy says (in the text's language, from the Timbre cache) one short line: what the big microphone does and that the speaker button reads the poem first. Bubble text also appears in the text's language.
6. **Technical implementation requirements.** Modules: `frontend/app.js openText()/resetReaderUI()`, `backend/phrases.py`
   - Add phrases `reader_hint` per language in backend/phrases.py; expose `/api/phrase/{lang}/{key}` returning the cached clip URL.
   - On openText(), play the hint once per visit after the first user gesture (autoplay policy); never while a session runs.
   - Localise the reader bubble strings (resetReaderUI, listeningBubble, yourTurnBubble) for hi/gu.
7. **Acceptance criteria.**
   - `spoken_guidance_gap_rate` <= 0.0; scope: personas with ui_english_reading < 0.3. Baseline this cycle: 0.6.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Pre-reader personas: the reader page must emit a spoken hint before the first mic tap (observed in the agent's 'heard' channel). QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P1

## REQ-STALL-TIMING: Stall prompt fires during normal thinking pauses of slow and hesitant readers

**Priority:** P1 (score 21.77) · **Status:** approved (P1 within capacity (2/8 units).) · **Owners:** Backend Engineer, AI/ML Engineer · **Complexity:** S

1. **Problem statement.** Stall prompt fires during normal thinking pauses of slow and hesitant readers. Seen in 3 of 5 simulated children (60%; pre-primary reach 67%), 5 occurrences; 67% of affected children abandoned or could not start.
2. **Affected personas.** C4-01, L01, U01 · by grade: LKG 1, UKG 1, Class 4 1 · by language: Hindi 2, Gujarati 1
3. **Supporting evidence.** Symptoms: INTERRUPTED_WHILE_THINKING×3.  Children said: “Buddy talked when I was thinking!” / “I was just thinking and Buddy jumped in.”
   - C4-01 (Class 4, Hindi): Buddy started talking 0.2 s into a planned 2.23 s thinking pause. {"t": 22.58, "paused_s": 0.2, "planned_s": 2.23, "line": 0, "next_words": "एक बगीचा है।"} · `agent_org/runs/pilot/p1/C4-01`
   - L01 (LKG, Hindi): Buddy started talking 2.3 s into a planned 3.46 s thinking pause. {"t": 26.18, "paused_s": 2.3, "planned_s": 3.46, "line": 0, "next_words": "गरजे, बारिश आई,"} · `agent_org/runs/pilot/p1/L01`
   - U01 (UKG, Gujarati): Buddy started talking 2.1 s into a planned 2.32 s thinking pause. {"t": 25.7, "paused_s": 2.1, "planned_s": 2.32, "line": 0, "next_words": "પતંગ લાલ ને"} · `agent_org/runs/pilot/p1/U01`
4. **Root-cause hypothesis.** TutorConfig.stall_mid_s = 2.0 s is one fixed threshold for every child. Word-by-word and hesitant readers in Nursery-UKG pause 2-5 s between words while decoding, so Buddy supplies the next words before the child tries them, which removes the decoding attempt.
5. **Expected behaviour.** Buddy waits longer mid-line for young/hesitant readers and for a child who has been reading word by word, while still prompting a genuinely stuck child within a few seconds.
6. **Technical implementation requirements.** Modules: `backend/tutor.py TutorConfig.stall_mid_s / tick()`, `backend/main.py Session`
   - Make stall thresholds adaptive: stall_mid_s = clamp(k x the reader's median inter-word gap observed in this session, 2.0, 5.0), with k configurable (default 2.0).
   - Add a `pace` profile (young|standard) to TutorConfig with stall_mid_s 3.5 s for young; select via the text level (pre-primary/Grade 1) until per-child profiles exist.
   - Never fire a stall prompt within 1.0 s of a transcript that advanced the pointer.
   - Keep eval/replay stall detection within 4.0 s on the stall test set (no regression in catching real stalls).
7. **Acceptance criteria.**
   - `stall_interruptions_per_agent` ≤ 0.5 × baseline (0.0); scope: x baseline (halve). Baseline this cycle: 0.0.
   - `stuck_rate` ≤ 0.0 × baseline (0.0); scope: +0 vs baseline (no new stuck children). Baseline this cycle: 0.0.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Re-run hesitant/word-by-word personas (same seeds) before/after; run eval.replay and check 'stalls prompted' stays >= 11/12. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P1

## REQ-MIC-TOGGLE: Tapping the big microphone during a session pauses it

**Priority:** P1 (score 20.94) · **Status:** approved (P1 within capacity (3/8 units).) · **Owners:** Frontend Engineer · **Complexity:** S

1. **Problem statement.** Tapping the big microphone during a session pauses it. Seen in 3 of 5 simulated children (60%; pre-primary reach 67%), 4 occurrences; 100% of affected children abandoned or could not start.
2. **Affected personas.** C2-01, L01, U01 · by grade: LKG 1, UKG 1, Class 2 1 · by language: English 1, Hindi 1, Gujarati 1
3. **Supporting evidence.** Symptoms: MIC_TAP_PAUSED_SESSION×3, HARD_TO_RESUME×1.  Children said: “I pressed the mic to talk and it stopped!” / “I pressed the microphone and it paused.” / “It stopped and I didn't know how to make it go.”
   - C2-01 (Class 2, English): Tapped the big microphone to talk; the session paused instead. {"t": 35.06, "bubble": "Press play when you're ready to keep reading."} · `agent_org/runs/pilot/p1/C2-01`
   - L01 (LKG, Hindi): Tapped the big microphone to talk; the session paused instead. {"t": 30.74, "bubble": "Press play when you're ready to keep reading."} · `agent_org/runs/pilot/p1/L01`
   - L01 (LKG, Hindi): Took 8 s to work out how to carry on after a pause. {"t": 42.18, "waited_s": 8.5} (follows MIC_TAP_PAUSED_SESSION) · `agent_org/runs/pilot/p1/L01`
   - U01 (UKG, Gujarati): Tapped the big microphone to talk; the session paused instead. {"t": 37.68, "bubble": "Press play when you're ready to keep reading."} · `agent_org/runs/pilot/p1/U01`
4. **Root-cause hypothesis.** micBtn.onclick toggles pause when a session is running. Young children tap the microphone to talk (the common mental model of a mic button), which silently pauses the session; the paused state is shown only as text and an icon change.
5. **Expected behaviour.** Tapping the mic while a session is listening does not pause; Buddy says a short 'I'm listening, go ahead!' (cached). Pausing stays available via the Pause button and Escape.
6. **Technical implementation requirements.** Modules: `frontend/app.js $('micBtn').onclick / togglePause()`
   - Change micBtn.onclick: while running and not paused, a tap plays a cached 'listening' cue and does not call togglePause(); while paused, a tap resumes.
   - Keep the separate Pause button and Escape key behaviour.
7. **Acceptance criteria.**
   - `mic_tap_pause_rate` <= 0.0; scope: all personas. Baseline this cycle: 0.6.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Personas with p_tap_mic_to_talk > 0, same seeds: no MIC_TAP_PAUSED_SESSION; Pause button still pauses (QA functional check). QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P1

## REQ-DRILL-LOOP: Word practice and line repetition loop on the same word or line

**Priority:** P2 (score 17.5) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Backend Engineer, AI/ML Engineer · **Complexity:** S

1. **Problem statement.** Word practice and line repetition loop on the same word or line. Seen in 1 of 5 simulated children (20%; pre-primary reach 0%), 2 occurrences; 100% of affected children abandoned or could not start.
2. **Affected personas.** C2-01 · by grade: Class 2 1 · by language: English 1
3. **Supporting evidence.** Symptoms: SAME_WORD_ASKED_AGAIN_AND_AGAIN×1.  Children said: “Buddy made me say the same word again and again.”
   - C2-01 (Class 2, English): Asked to say 'grain' 3 times. {"t": 143.66, "word": "grain", "times": 3} · `agent_org/runs/pilot/p1/C2-01`
4. **Root-cause hypothesis.** A drill word is repeated until recognised and a line can be re-read until it is error-free, with up to max_line_mistakes = 10 mistakes per line before moving on. For young children ten failed tries on one line is far past frustration.
5. **Expected behaviour.** At most 2 attempts per practice word (then Buddy says it together with the child and moves on), and max_line_mistakes scaled by level (pre-primary/Grade 1: 4; others: 6).
6. **Technical implementation requirements.** Modules: `backend/tutor.py _drill_attempt(), _add_mistakes(), TutorConfig.max_line_mistakes`
   - Add TutorConfig.max_word_attempts (default 2): after that, mark the word 'helped', say `word_ok` and continue.
   - Make max_line_mistakes level-dependent through the pace profile.
7. **Acceptance criteria.**
   - `drill_repeat_rate` <= 0.0; scope: all personas. Baseline this cycle: 0.2.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Personas with low accuracy before/after; unit test for the attempt cap. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-LONG-INTRO: Buddy's opening talk is long before the child gets a turn

**Priority:** P2 (score 15.94) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Backend Engineer · **Complexity:** S

1. **Problem statement.** Buddy's opening talk is long before the child gets a turn. Seen in 4 of 5 simulated children (80%; pre-primary reach 67%), 4 occurrences; 75% of affected children abandoned or could not start.
2. **Affected personas.** C2-01, C4-01, L01, U01 · by grade: LKG 1, UKG 1, Class 2 1, Class 4 1 · by language: English 1, Hindi 2, Gujarati 1
3. **Supporting evidence.** Symptoms: LONG_TUTOR_TALK×4.  Children said: “Buddy talks a lot before I get to read.” / “Buddy talked too long.”
   - C2-01 (Class 2, English): Buddy talked for over 12 s in one go before the child could read. {"t": 26.2, "talk_s": 12.5} · `agent_org/runs/pilot/p1/C2-01`
   - C4-01 (Class 4, Hindi): Buddy talked for over 12 s in one go before the child could read. {"t": 25.4, "talk_s": 12.2} · `agent_org/runs/pilot/p1/C4-01`
   - L01 (LKG, Hindi): Buddy talked for over 12 s in one go before the child could read. {"t": 20.63, "talk_s": 12.2} · `agent_org/runs/pilot/p1/L01`
   - U01 (UKG, Gujarati): Buddy talked for over 12 s in one go before the child could read. {"t": 20.94, "talk_s": 12.6} · `agent_org/runs/pilot/p1/U01`
4. **Root-cause hypothesis.** start() chains welcome + 'today we're going to read' + title + 'listen carefully' + line 1 + 'your turn' into one ~13 s utterance; short attention spans are spent before reading starts.
5. **Expected behaviour.** First turn within ~8 s: one greeting phrase + line demonstration + 'your turn'; the title is shown, and the full welcome is used only on a child's first session.
6. **Technical implementation requirements.** Modules: `backend/tutor.py start()`
   - Drop `today` + title from start() after the first session on the device (client sends `first_visit`), or always for pre-primary items.
   - Merge `listen_first` and `read_with_me` into one short phrase per language.
7. **Acceptance criteria.**
   - `intro_s_median` <= 9.0; scope: all personas. Baseline this cycle: 13.4.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Median intro_s before/after on the same persona set. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-TALK-OVER-BUDDY: What a child says while Buddy is talking is silently discarded

**Priority:** P2 (score 14.89) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Speech AI Engineer, Frontend Engineer · **Complexity:** M

1. **Problem statement.** What a child says while Buddy is talking is silently discarded. Seen in 3 of 5 simulated children (60%; pre-primary reach 33%), 11 occurrences; 67% of affected children abandoned or could not start.
2. **Affected personas.** C2-01, C4-01, U01 · by grade: UKG 1, Class 2 1, Class 4 1 · by language: English 1, Hindi 1, Gujarati 1
3. **Supporting evidence.** Symptoms: SPEECH_IGNORED_WHILE_BUDDY_TALKS×3.  Children said: “Buddy didn't hear me when I was talking.” / “I said it but Buddy didn't hear me!”
   - C2-01 (Class 2, English): 7 word(s) the child said were not heard because Buddy was talking or the session was paused. {"t": 23.6, "said": "A small ant walk across tree floor", "heard": ""} · `agent_org/runs/pilot/p1/C2-01`
   - C4-01 (Class 4, Hindi): 8 word(s) the child said were not heard because Buddy was talking or the session was paused. {"t": 17.56, "said": "मीना के घड़ के पीछे एक बगीचा है", "heard": ""} · `agent_org/runs/pilot/p1/C4-01`
   - U01 (UKG, Gujarati): 1 word(s) the child said were not heard because Buddy was talking or the session was paused. {"t": 47.39, "said": "પીળો", "heard": ""} · `agent_org/runs/pilot/p1/U01`
4. **Root-cause hypothesis.** The mic is zeroed while Buddy speaks (to avoid echo). Eager readers start the next line during praise or the line demonstration; their words never reach the speech model and nothing tells them.
5. **Expected behaviour.** Short praise is interruptible: if the child starts speaking (local level detector), Buddy's praise clip stops and the mic opens. For non-interruptible speech (demonstrations), a visible/audible 'my turn first' cue.
6. **Technical implementation requirements.** Modules: `frontend/app.js startMic() mute while tutorSpeaking`, `frontend/app.js playSay()`
   - Client-side energy VAD on the raw mic stream while muted; if speech > 300 ms during a `praise` say, stop playback, send audio_done, unmute.
   - Mark say kinds as interruptible (praise, keep_going) vs not (intro demonstration, repeat_line, fix_*).
7. **Acceptance criteria.**
   - `unheard_words_per_agent` ≤ 0.5 × baseline (10.6); scope: x baseline. Baseline this cycle: 10.6.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** Fast-reader personas (high p_talk_over_buddy) before/after; echo safety checked by a consenting adult on a laptop speaker (manual). QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-LANGUAGE-SELECTION: Children end up in, or hear, a language they did not choose

**Priority:** P2 (score 14.5) · **Status:** deferred (P2: below the approval line this cycle.) · **Owners:** Frontend Engineer · **Complexity:** S

1. **Problem statement.** Children end up in, or hear, a language they did not choose. Seen in 1 of 5 simulated children (20%; pre-primary reach 33%), 1 occurrences; 100% of affected children abandoned or could not start.
2. **Affected personas.** N01 · by grade: Nursery 1 · by language: English 1
3. **Supporting evidence.** Symptoms: WRONG_LANGUAGE_TEXT×1.  Children said: “This isn't my language!”
   - N01 (Nursery, English): Wanted en-IN but ended up on a hi-IN text. {"t": 5.3, "wanted": "en-IN", "got": "hi-IN", "title": "बारिश आई"} · `agent_org/runs/pilot/p1/N01`
4. **Root-cause hypothesis.** First-visit default language is Gujarati; language cards and tabs rely on reading script names; non-readers pick by picture and land in another language.
5. **Expected behaviour.** Default language follows the browser/device locale (hi -> Hindi, gu -> Gujarati, else English); each language card speaks its name when tapped once (tap again to open).
6. **Technical implementation requirements.** Modules: `frontend/app.js app.lang default 'gu-IN', library tabs`
   - Use navigator.languages to pick the first-visit default.
   - Language cards: first tap plays a cached clip of the language name.
7. **Acceptance criteria.**
   - `wrong_language_rate` ≤ 0.5 × baseline (0.2); scope: x baseline. Baseline this cycle: 0.2.
   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.
8. **Validation methodology.** All personas, same seeds. QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.
9. **Priority.** P2

## REQ-LENIENT-MATCHING: Some misreadings are accepted as correct (vowel length, matras, word endings, small words)

**Priority:** P3 (score 12.0) · **Status:** awaiting_human_approval (Touches content, privacy or model/data collection: needs a human decision.) · **Owners:** NLP Engineer · **Complexity:** M

1. **Problem statement.** Some misreadings are accepted as correct (vowel length, matras, word endings, small words). Seen in 2 of 5 simulated children (40%; pre-primary reach 0%), 3 occurrences; 50% of affected children abandoned or could not start.
2. **Affected personas.** C2-01, C4-01 · by grade: Class 2 1, Class 4 1 · by language: English 1, Hindi 1
3. **Supporting evidence.** Symptoms: MISSED_ERROR×2. 
   - C2-01 (Class 2, English): Read 'carried' as 'carri' and it was marked as read correctly. {"word": "carried", "child_said": "carri", "kind": "sub", "speech_model_wrote": "is carri a grain rice its back"} · `agent_org/runs/pilot/p1/C2-01`
   - C4-01 (Class 4, Hindi): Read 'हैं' as 'हें' and it was marked as read correctly. {"word": "हैं", "child_said": "हें", "kind": "sub", "speech_model_wrote": "उसमें लाल और पीले फूल खिलते हें"} · `agent_org/runs/pilot/p1/C4-01`
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

