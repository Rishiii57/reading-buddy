"""The Product Manager's root-cause knowledge: how child-level symptoms map to underlying causes,
and what a precise engineering requirement for each cause looks like.

A symptom code can belong to more than one root cause. Each root cause owns only the evidence
its `match` predicate accepts (for example, an interruption by a stall prompt and an interruption
by a mid-line correction are different causes in different code paths). Anything no root cause
claims ends up in UNCLASSIFIED and is reported, never dropped.

Acceptance targets: a number is absolute; "x0.5" means at most 0.5 x the baseline value (a zero
baseline must stay zero); "baseline" means no worse than the baseline.

Severity (1-4): 4 = blocks reading or puts a child's privacy at risk; 3 = breaks the learning
loop or causes abandonment; 2 = noticeable friction; 1 = polish.
"""

ROOT_CAUSES = [
    {
        "id": "RC-PREPRIMARY-CONTENT",
        "title": "No reading material for Nursery, LKG and UKG",
        "codes": ["NO_TEXT_FOR_MY_LEVEL"],
        "severity": 4, "learning_impact": 3, "ux_impact": 3, "complexity": "L", "needs_human": True,
        "owners": ["Data Engineer", "Speech AI Engineer", "Frontend Engineer"],
        "modules": ["content/*.json", "backend/content.py", "frontend/app.js (grade filter)", "cache/tts"],
        "hypothesis": "The library holds 12 texts for Grades 1-4 (16-37 words of continuous text). The grade filter "
                      "offers Grade 1-5 only. Pre-primary children are pre-readers or emergent readers; continuous "
                      "text with no pre-reading formats cannot be read, so every pre-primary session degenerates "
                      "into stall prompts.",
        "expected": "Each language offers at least 3 items per pre-primary level (Nursery: listen-and-repeat rhymes of "
                    "2-4 short lines; LKG: picture-word / letter-sound items; UKG: 3-4 word sentences), selectable "
                    "from a pre-primary filter, and Buddy models each line before the child repeats it.",
        "tech": [
            "Add a `level` field (nursery|lkg|ukg|1..4) to content specs and `/api/library`; keep `grade` for backward compatibility.",
            "Author pre-primary items per language; Hindi/Gujarati wording must be reviewed by a native-speaking teacher before release (human approval).",
            "Pre-generate Timbre clips for every line and word (backend/pregen.py) so first use is instant and cached.",
            "Library UI: add Nursery/LKG/UKG chips with picture icons (non-readers).",
            "Tutor: an `echo` mode for pre-primary items (Buddy reads each line, child repeats) via TutorConfig, not a new engine.",
        ],
        "acceptance": [("level_mismatch_rate", "<=", 0.0, "pre-primary personas"),
                       ("coverage", ">=", 0.6, "pre-primary personas"),
                       ("stuck_rate", "<=", 0.1, "pre-primary personas")],
        "validation": "Re-run all Nursery/LKG/UKG personas with the same seeds; compare level_mismatch_rate, coverage and stuck_rate; native-speaker review sign-off recorded in the decision log.",
        "scope": {"grades": ["Nursery", "LKG", "UKG"]},
    },
    {
        "id": "RC-CONSENT-GATE",
        "title": "Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass",
        "codes": ["CONSENT_BLOCKS_CHILD", "CONSENT_SELF_APPROVED"],
        "severity": 4, "learning_impact": 2, "ux_impact": 3, "complexity": "M", "needs_human": True,
        "owners": ["Frontend Engineer"],
        "modules": ["frontend/index.html #consentDlg", "frontend/app.js askConsent()"],
        "hypothesis": "askConsent() shows a written English dialog with a checkbox 'I am the child's parent or guardian'. "
                      "A pre-reader cannot read it and gets no spoken explanation; any child who can read English can tick "
                      "it. The consent therefore neither informs the parent nor stops the child.",
        "expected": "A child who meets the gate hears (in the session language) that a grown-up is needed, and the screen "
                    "shows a clear 'ask a grown-up' picture. The gate requires an adult-only action a young child is "
                    "unlikely to complete by chance (e.g. press-and-hold plus a simple question in the parent's language), "
                    "and the Demo reader stays available without consent.",
        "tech": [
            "Replace the checkbox with an adult verification step (press-and-hold 3 s + a two-digit arithmetic question or typed year of birth), shown only once per device.",
            "Play a cached Timbre phrase 'Please ask a grown-up to help you start' in the selected language when the gate opens.",
            "Log (locally, no personal data) gate shown / passed / cancelled for QA.",
            "Privacy wording change requires human (team) approval.",
        ],
        "acceptance": [("consent_blocked_rate", "<=", 0.0, "personas without grown-up setup who cannot read English"),
                       ("consent_self_approved_rate", "<=", 0.0, "personas without grown-up setup who read English")],
        "validation": "Run personas with grown_up_setup=false; check no child completes the adult step and every pre-reader hears the spoken 'ask a grown-up' message.",
        "scope": {"grown_up_setup": False},
    },
    {
        "id": "RC-SPOKEN-ONBOARDING",
        "title": "Before a session starts, all guidance is written English; non-readers get no spoken instructions",
        "codes": ["NO_SPOKEN_GUIDANCE_BEFORE_START", "LISTEN_FIRST_NOT_FOUND"],
        "severity": 3, "learning_impact": 2, "ux_impact": 3, "complexity": "S", "needs_human": False,
        "owners": ["Frontend Engineer", "Speech AI Engineer"],
        "modules": ["frontend/app.js openText()/resetReaderUI()", "backend/phrases.py"],
        "hypothesis": "resetReaderUI() writes 'Press the big microphone and read the first line out loud.' into the bubble "
                      "but nothing is spoken until the session starts. Pre-readers, and children who read Hindi or Gujarati "
                      "but not English, cannot tell which button starts reading or that 'Listen first' exists.",
        "expected": "On opening a text, Buddy says (in the text's language, from the Timbre cache) one short line: what the "
                    "big microphone does and that the speaker button reads the poem first. Bubble text also appears in "
                    "the text's language.",
        "tech": [
            "Add phrases `reader_hint` per language in backend/phrases.py; expose `/api/phrase/{lang}/{key}` returning the cached clip URL.",
            "On openText(), play the hint once per visit after the first user gesture (autoplay policy); never while a session runs.",
            "Localise the reader bubble strings (resetReaderUI, listeningBubble, yourTurnBubble) for hi/gu.",
        ],
        "acceptance": [("spoken_guidance_gap_rate", "<=", 0.0, "personas with ui_english_reading < 0.3")],
        "validation": "Pre-reader personas: the reader page must emit a spoken hint before the first mic tap (observed in the agent's 'heard' channel).",
        "scope": {"ui_english_reading_lt": 0.3},
    },
    {
        "id": "RC-STALL-TIMING",
        "title": "Stall prompt fires during normal thinking pauses of slow and hesitant readers",
        "codes": ["INTERRUPTED_WHILE_THINKING"],
        "match": lambda e: str(e.get("buddy_kind", "")).startswith("stall") or e.get("buddy_kind") is None,
        "severity": 3, "learning_impact": 3, "ux_impact": 3, "complexity": "S", "needs_human": False,
        "owners": ["Backend Engineer", "AI/ML Engineer"],
        "modules": ["backend/tutor.py TutorConfig.stall_mid_s / tick()", "backend/main.py Session"],
        "hypothesis": "TutorConfig.stall_mid_s = 2.0 s is one fixed threshold for every child. Word-by-word and hesitant "
                      "readers in Nursery-UKG pause 2-5 s between words while decoding, so Buddy supplies the next words "
                      "before the child tries them, which removes the decoding attempt.",
        "expected": "Buddy waits longer mid-line for young/hesitant readers and for a child who has been reading word by "
                    "word, while still prompting a genuinely stuck child within a few seconds.",
        "tech": [
            "Make stall thresholds adaptive: stall_mid_s = clamp(k x the reader's median inter-word gap observed in this session, 2.0, 5.0), with k configurable (default 2.0).",
            "Add a `pace` profile (young|standard) to TutorConfig with stall_mid_s 3.5 s for young; select via the text level (pre-primary/Grade 1) until per-child profiles exist.",
            "Never fire a stall prompt within 1.0 s of a transcript that advanced the pointer.",
            "Keep eval/replay stall detection within 4.0 s on the stall test set (no regression in catching real stalls).",
        ],
        "acceptance": [("stall_interruptions_per_agent", "<=", "x0.5", "affected personas"),
                       ("stuck_rate", "<=", "baseline", "no new stuck children")],
        "validation": "Re-run hesitant/word-by-word personas (same seeds) before/after; run eval.replay and check 'stalls prompted' stays >= 11/12.",
    },
    {
        "id": "RC-MIDLINE-CORRECTION",
        "title": "A slip followed by a thinking pause triggers word practice mid-line",
        "codes": ["INTERRUPTED_WHILE_THINKING"],
        "match": lambda e: str(e.get("buddy_kind", "")).startswith(("fix", "repeat")),
        "severity": 3, "learning_impact": 3, "ux_impact": 2, "complexity": "S", "needs_human": False,
        "owners": ["Backend Engineer"],
        "modules": ["backend/tutor.py tick() -> _check_line()"],
        "hypothesis": "tick() calls _check_line() as soon as idle >= stall_mid_s (2.0 s) when the line already has an error, "
                      "so a child who misreads a word and pauses to think (or to self-correct) is pulled into word practice "
                      "before finishing the line. Self-correction after 2 s is never possible.",
        "expected": "After a slip, Buddy lets the child finish the line (or pause up to the stall threshold for that child), "
                    "then practises the word.",
        "tech": [
            "In tick(), when errors exist mid-line, wait max(stall threshold, self_correct_s + 1.5 s) before _check_line().",
            "If a later transcript in the same line re-reads the slipped word correctly, clear it from line_errors (self-correction).",
        ],
        "acceptance": [("correction_interruptions_per_agent", "<=", "x0.5", "affected personas")],
        "validation": "Same personas and seeds before/after; unit test: slip + 2.5 s pause + continue does not trigger a correction mid-line.",
    },
    {
        "id": "RC-MIC-TOGGLE",
        "title": "Tapping the big microphone during a session pauses it",
        "codes": ["MIC_TAP_PAUSED_SESSION", "HARD_TO_RESUME"],
        "severity": 3, "learning_impact": 2, "ux_impact": 3, "complexity": "S", "needs_human": False,
        "owners": ["Frontend Engineer"],
        "modules": ["frontend/app.js $('micBtn').onclick / togglePause()"],
        "hypothesis": "micBtn.onclick toggles pause when a session is running. Young children tap the microphone to talk "
                      "(the common mental model of a mic button), which silently pauses the session; the paused state is "
                      "shown only as text and an icon change.",
        "expected": "Tapping the mic while a session is listening does not pause; Buddy says a short 'I'm listening, go "
                    "ahead!' (cached). Pausing stays available via the Pause button and Escape.",
        "tech": [
            "Change micBtn.onclick: while running and not paused, a tap plays a cached 'listening' cue and does not call togglePause(); while paused, a tap resumes.",
            "Keep the separate Pause button and Escape key behaviour.",
        ],
        "acceptance": [("mic_tap_pause_rate", "<=", 0.0, "all personas")],
        "validation": "Personas with p_tap_mic_to_talk > 0, same seeds: no MIC_TAP_PAUSED_SESSION; Pause button still pauses (QA functional check).",
    },
    {
        "id": "RC-TALK-OVER-BUDDY",
        "title": "What a child says while Buddy is talking is silently discarded",
        "codes": ["SPEECH_IGNORED_WHILE_BUDDY_TALKS"],
        "severity": 2, "learning_impact": 2, "ux_impact": 2, "complexity": "M", "needs_human": False,
        "owners": ["Speech AI Engineer", "Frontend Engineer"],
        "modules": ["frontend/app.js startMic() mute while tutorSpeaking", "frontend/app.js playSay()"],
        "hypothesis": "The mic is zeroed while Buddy speaks (to avoid echo). Eager readers start the next line during praise "
                      "or the line demonstration; their words never reach the speech model and nothing tells them.",
        "expected": "Short praise is interruptible: if the child starts speaking (local level detector), Buddy's praise clip "
                    "stops and the mic opens. For non-interruptible speech (demonstrations), a visible/audible 'my turn first' cue.",
        "tech": [
            "Client-side energy VAD on the raw mic stream while muted; if speech > 300 ms during a `praise` say, stop playback, send audio_done, unmute.",
            "Mark say kinds as interruptible (praise, keep_going) vs not (intro demonstration, repeat_line, fix_*).",
        ],
        "acceptance": [("unheard_words_per_agent", "<=", "x0.5", "affected personas")],
        "validation": "Fast-reader personas (high p_talk_over_buddy) before/after; echo safety checked by a consenting adult on a laptop speaker (manual).",
    },
    {
        "id": "RC-LONG-INTRO",
        "title": "Buddy's opening talk is long before the child gets a turn",
        "codes": ["LONG_TUTOR_TALK"],
        "severity": 2, "learning_impact": 1, "ux_impact": 2, "complexity": "S", "needs_human": False,
        "owners": ["Backend Engineer"],
        "modules": ["backend/tutor.py start()"],
        "hypothesis": "start() chains welcome + 'today we're going to read' + title + 'listen carefully' + line 1 + 'your turn' "
                      "into one ~13 s utterance; short attention spans are spent before reading starts.",
        "expected": "First turn within ~8 s: one greeting phrase + line demonstration + 'your turn'; the title is shown, and "
                    "the full welcome is used only on a child's first session.",
        "tech": ["Drop `today` + title from start() after the first session on the device (client sends `first_visit`), or always for pre-primary items.",
                 "Merge `listen_first` and `read_with_me` into one short phrase per language."],
        "acceptance": [("intro_s_median", "<=", 9.0, "all personas")],
        "validation": "Median intro_s before/after on the same persona set.",
    },
    {
        "id": "RC-DRILL-LOOP",
        "title": "Word practice and line repetition loop on the same word or line",
        "codes": ["SAME_WORD_ASKED_AGAIN_AND_AGAIN"],
        "severity": 3, "learning_impact": 2, "ux_impact": 3, "complexity": "S", "needs_human": False,
        "owners": ["Backend Engineer", "AI/ML Engineer"],
        "modules": ["backend/tutor.py _drill_attempt(), _add_mistakes(), TutorConfig.max_line_mistakes"],
        "hypothesis": "A drill word is repeated until recognised and a line can be re-read until it is error-free, with up to "
                      "max_line_mistakes = 10 mistakes per line before moving on. For young children ten failed tries on one "
                      "line is far past frustration.",
        "expected": "At most 2 attempts per practice word (then Buddy says it together with the child and moves on), and "
                    "max_line_mistakes scaled by level (pre-primary/Grade 1: 4; others: 6).",
        "tech": ["Add TutorConfig.max_word_attempts (default 2): after that, mark the word 'helped', say `word_ok` and continue.",
                 "Make max_line_mistakes level-dependent through the pace profile."],
        "acceptance": [("drill_repeat_rate", "<=", 0.0, "all personas")],
        "validation": "Personas with low accuracy before/after; unit test for the attempt cap.",
    },
    {
        "id": "RC-FALSE-CORRECTION-TUTOR",
        "title": "Correctly read words flagged for practice (tutor/aligner)",
        "codes": ["FALSE_CORRECTION", "CORRECTED_A_WORD_NOT_YET_READ"],
        "severity": 3, "learning_impact": 3, "ux_impact": 3, "complexity": "M", "needs_human": False,
        "owners": ["NLP Engineer", "AI/ML Engineer"],
        "modules": ["backend/aligner.py", "backend/tutor.py _read()"],
        "hypothesis": "The strict aligner (match_thr 0.85) or the muted-fragment logic marks words as errors when the transcript "
                      "is split or re-read; check each case against the child's ground truth.",
        "expected": "< 1 false correction per 50 correctly read words in simulated sessions and in eval.replay.",
        "tech": ["Inspect each logged case; add regression fixtures to tests/test_tutor.py; adjust alignment only with replay evidence."],
        "acceptance": [("false_corrections_per_agent", "<=", "x0.5", "affected personas")],
        "validation": "eval.replay false corrections per 50 words must not rise; simulated sessions before/after.",
    },
    {
        "id": "RC-FALSE-CORRECTION-STT",
        "title": "Correct reading misheard by the speech model (child voices)",
        "codes": ["FALSE_CORRECTION_STT"],
        "severity": 3, "learning_impact": 3, "ux_impact": 3, "complexity": "L", "needs_human": True,
        "owners": ["Speech AI Engineer", "AI/ML Engineer"],
        "modules": ["backend/gnani.py STT settings", "content/stt_aliases.json", "eval/"],
        "hypothesis": "Prisma's error rate on young children's speech is unmeasured (all test audio is adult TTS). Gujarati already "
                      "shows 7.3 % WER on clean synthetic speech.",
        "expected": "Measured child-speech WER per language from consenting, safeguarded recordings; aliases learned from them.",
        "tech": ["Collect consented recordings (team members' children only with written parental consent, stored offline, deletable) - human approval.",
                 "Extend eval/run_stt.py to those recordings; learn aliases with eval/build_aliases.py."],
        "acceptance": [],
        "validation": "Audio evaluation report (separate from simulated satisfaction).",
    },
    {
        "id": "RC-LENIENT-MATCHING",
        "title": "Some misreadings are accepted as correct (vowel length, matras, word endings, small words)",
        "codes": ["MISSED_ERROR"],
        "severity": 2, "learning_impact": 2, "ux_impact": 1, "complexity": "M", "needs_human": True,
        "owners": ["NLP Engineer"],
        "modules": ["backend/normalize.py loose()/similarity()", "backend/content.py _SHORT_WORDS"],
        "hypothesis": "By design, loose() folds vowel length and nasalisation, similarity() gives a stem bonus, and skipped "
                      "short function words are forgiven; this tolerates speech-model spelling noise but also accepts "
                      "genuine matra/ending errors.",
        "expected": "Product decision (human): keep tolerance for pre-primary, but for Class 2-4 report frequent matra/ending "
                    "slips softly in the parent summary without interrupting the child.",
        "tech": ["Record 'near matches' (accepted with sim < 0.95) in the session log and summary as 'listen again' words for Class 2-4.",
                 "No change to live interruption behaviour."],
        "acceptance": [],
        "validation": "Summary lists near-match words in simulated Class 2-4 sessions; no change in false corrections.",
    },
    {
        "id": "RC-LANGUAGE-SELECTION",
        "title": "Children end up in, or hear, a language they did not choose",
        "codes": ["WRONG_LANGUAGE_TEXT", "BUDDY_LANGUAGE_NOT_UNDERSTOOD"],
        "severity": 2, "learning_impact": 2, "ux_impact": 2, "complexity": "S", "needs_human": False,
        "owners": ["Frontend Engineer"],
        "modules": ["frontend/app.js app.lang default 'gu-IN', library tabs"],
        "hypothesis": "First-visit default language is Gujarati; language cards and tabs rely on reading script names; "
                      "non-readers pick by picture and land in another language.",
        "expected": "Default language follows the browser/device locale (hi -> Hindi, gu -> Gujarati, else English); each "
                    "language card speaks its name when tapped once (tap again to open).",
        "tech": ["Use navigator.languages to pick the first-visit default.", "Language cards: first tap plays a cached clip of the language name."],
        "acceptance": [("wrong_language_rate", "<=", "x0.5", "all personas")],
        "validation": "All personas, same seeds.",
    },
    {
        "id": "RC-NAVIGATION",
        "title": "Children cannot find a text or leave the reading page by accident",
        "codes": ["NAV_TEXT_NOT_FOUND", "LEFT_READING_BY_ACCIDENT", "COULD_NOT_START_SESSION"],
        "severity": 3, "learning_impact": 2, "ux_impact": 3, "complexity": "M", "needs_human": False,
        "owners": ["Frontend Engineer"],
        "modules": ["frontend/index.html reader-bar (Back/End)", "frontend/app.js route()"],
        "hypothesis": "Back and End are always-visible buttons next to the reading area; a stray tap leaves or ends the session "
                      "with no confirmation.",
        "expected": "Leaving a running session needs a confirmation that is spoken and pictorial; End during the first 10 s asks again.",
        "tech": ["Confirm dialog (child-friendly, spoken) for Back/End while a session runs."],
        "acceptance": [("abandon_rate", "<=", "x0.8", "all personas")],
        "validation": "All personas, same seeds.",
    },
    {
        "id": "RC-BREAK",
        "title": "'I'm tired' is not recognised",
        "codes": ["BREAK_REQUEST_IGNORED"],
        "severity": 2, "learning_impact": 1, "ux_impact": 2, "complexity": "S", "needs_human": False,
        "owners": ["NLP Engineer"],
        "modules": ["backend/tutor.py _BREAK_WORDS/_asks_for_break()"],
        "hypothesis": "The break vocabulary misses common child phrasings or inflections.",
        "expected": "Common phrasings in all three languages trigger the break.",
        "tech": ["Extend _BREAK_WORDS with inflections; add unit tests per language."],
        "acceptance": [("break_ignored_rate", "<=", 0.0, "all personas")],
        "validation": "Personas that say they are tired.",
    },
    {
        "id": "RC-STUCK",
        "title": "Children who cannot read the next word wait without help",
        "codes": ["STUCK_WITHOUT_HELP"],
        "severity": 3, "learning_impact": 3, "ux_impact": 2, "complexity": "S", "needs_human": False,
        "owners": ["Backend Engineer"],
        "modules": ["backend/tutor.py stall thresholds / stall_level 3 wait"],
        "hypothesis": "After stall level 2 Buddy says 'take your time' and then waits indefinitely.",
        "expected": "A silent child gets the line modelled again after a longer wait instead of indefinite silence.",
        "tech": ["After `take_time`, re-demonstrate the current phrase after 8 s, at most twice per line, then offer to move on."],
        "acceptance": [("stuck_rate", "<=", "x0.5", "pre-reader personas")],
        "validation": "Pre-reader personas before/after.",
    },
    {
        "id": "RC-REPLAY",
        "title": "No way to hear a line again during reading",
        "codes": ["NO_REPLAY_CONTROL"],
        "severity": 2, "learning_impact": 2, "ux_impact": 2, "complexity": "S", "needs_human": False,
        "owners": ["Frontend Engineer", "Backend Engineer"],
        "modules": ["frontend/app.js setControls() (listenBtn disabled while running)", "backend/main.py control messages"],
        "hypothesis": "'Listen first' is disabled once a session runs; children who did not catch Buddy's model reading cannot ask for it again except by stalling.",
        "expected": "A 'hear this line' (speaker) button next to the active line during a session; Buddy reads the current line and the child continues.",
        "tech": ["Add a control message `replay_line`; engine returns a `say` of the current line span without counting a prompt.",
                 "Speaker icon button on the active line band; disabled while Buddy talks."],
        "acceptance": [("replay_missing_rate", "<=", 0.0, "personas who want replays")],
        "validation": "Replay-seeking personas before/after.",
    },
    {
        "id": "RC-RESTART",
        "title": "Reading the same text again does not work smoothly",
        "codes": ["RESTART_NOT_FOUND", "RESTART_FAILED"],
        "severity": 3, "learning_impact": 2, "ux_impact": 2, "complexity": "S", "needs_human": False,
        "owners": ["Frontend Engineer"],
        "modules": ["frontend/app.js againBtn / openText()"],
        "hypothesis": "'Read this again' routes to the same hash; the reader may not re-open or reset correctly.",
        "expected": "Read this again re-opens the text ready to start.",
        "tech": ["Force a re-render when the route hash is unchanged."],
        "acceptance": [("restart_failed_rate", "<=", 0.0, "restart personas")],
        "validation": "Restart personas.",
    },
    {
        "id": "RC-SESSION-STABILITY",
        "title": "Sessions stop unexpectedly",
        "codes": ["SESSION_STOPPED_UNEXPECTEDLY", "LISTEN_FIRST_STUCK"],
        "severity": 4, "learning_impact": 3, "ux_impact": 3, "complexity": "M", "needs_human": False,
        "owners": ["Integration Engineer", "Backend Engineer"],
        "modules": ["backend/main.py session_ws", "frontend/app.js ws.onclose"],
        "hypothesis": "A WebSocket close or STT reconnect failure ends the session with no resume.",
        "expected": "Reconnect transparently within 5 s and keep the reading position.",
        "tech": ["Client reconnect with session id; server keeps engine state for 60 s after disconnect."],
        "acceptance": [],
        "validation": "Network interruption tests (Playwright offline toggling).",
    },
]

COMPLEXITY_COST = {"S": 1, "M": 2, "L": 3}
