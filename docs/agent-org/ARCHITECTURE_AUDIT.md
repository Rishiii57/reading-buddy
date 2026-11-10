# Reading Buddy: Architecture Audit (Task 2, Phase 1)

Audited at commit `1a2d767` (the single commit on `main`). Everything below was read from the code, not the README. Where the README and the code disagree, the code wins.

## 1. System at a glance

```
Browser (frontend/app.js, vanilla JS, hash router)
  │  mic → AudioWorklet → linear resampler → 16 kHz PCM16, 512-sample (1024-byte) frames
  │  muted (zeros) while Buddy speaks or the session is paused
  ▼
FastAPI  backend/main.py   WebSocket /ws/session
  │  1st text msg: {"type":"start","text_id":..,"mode":"mic"|"demo"}
  │  then binary audio frames + control msgs: live, pause, resume, audio_start, audio_done, stop
  ├──► Gnani Prisma v2.5 streaming STT (wss://api.vachana.ai/stt/v3/stream), opened per session
  │      events: speech_start, transcript{text, latency, audio_duration_ms}, error
  ├──► TutorEngine (backend/tutor.py) + aligner (backend/aligner.py) + normalize.py
  │      returns actions: say{kind, parts}, progress, summary, pause
  └──► Gnani Timbre v3.0 TTS (REST, voice Lakshmi) via backend/gnani.py TTS, disk cache cache/tts/
         server → browser: ready, state, speech, heard, say{clips[url]}, summary, auto_pause, error
```

Three loops run per session in `main.py`: `stt_reader` (Prisma events → engine), `ticker` (every 100 ms, `engine.tick(now)` for stalls/timeouts), and the receive loop (audio + control). `warm_up` and `prefetch` pre-synthesise likely clips.

## 2. Backend modules

| File | Lines | Role |
|---|---|---|
| `backend/main.py` | 366 | FastAPI app, REST endpoints, `Session` class, WebSocket handler, static frontend mount |
| `backend/gnani.py` | 144 | `TTS` (Timbre REST, sha1-keyed permanent cache, 429 back-off, concurrency 2), `open_stt` (Prisma WS headers), `Usage` ledger (`cache/usage.json`, git-ignored) |
| `backend/tutor.py` | 581 | `TutorEngine`: explicit state machine, pure and clock-injected (`now` passed into every method) |
| `backend/aligner.py` | 179 | Semi-global DP alignment, affine gaps, back-window for re-reading, 1↔2/3 token joins |
| `backend/normalize.py` | 106 | `norm` (nukta, chandrabindu→anusvara, ZWJ, digits→words), `loose` (vowel length, nasal marks, doubled English letters), `similarity` (Levenshtein + stem bonus), filler list |
| `backend/content.py` | 98 | Loads `content/*.json` into `Text`/`Word`; short function-word list; STT aliases |
| `backend/phrases.py` | 71 | Buddy's fixed phrases in en/hi/gu (hi/gu translations not yet checked by a native teacher, per the file's own note) |
| `backend/pregen.py` | 40 | Pre-generates TTS clips |

### REST endpoints
`GET /api/library`, `GET /api/text/{id}`, `GET /api/listen/{id}` (per-line clips for "Listen first"), `GET /api/demo/{id}/plan`, `GET /api/demo/{id}/say?a&b&swap&said` (16 kHz WAV of the synthetic demo child, voice Riyaa), `GET /api/usage`, `GET /tts/{name}`, `GET /healthz`.

## 3. STT and TTS integration

- **Prisma STT**: one WebSocket per session, opened **as soon as the session WebSocket receives `start`** (before the mic is live). Headers: `language_code`, `model=prisma-v2.5`, `x-sample-rate=16000`, `x-vad-threshold=0.5` (env `STT_VAD_THRESHOLD`), `x-min-silence-ms=300`, `x-max-speech-s=8`, `x-idle-timeout-sec=300`, `format=verbatim`. On close it reconnects after 0.2 s; a failed reconnect ends the session with "Speech service disconnected." Billing is by streamed audio: `StreamClock` counts frames, and **silence frames are streamed too** (the browser sends zeros while muted), so a session costs STT time for its full duration, including Buddy's talking time.
- **Timbre TTS**: `TTS.get(text, lang, speed, voice, container, sample_rate)` → cache key → `cache/tts/<key>.mp3|wav`. 453 clips are already committed, so most phrases and lines cost nothing. Speeds: phrases 1.0, spans 0.9, single practice word 0.85. A TTS failure inside `handle_actions` skips that `say` and marks the tutor audio as ended, so the session continues silently.
- **Demo reader**: the browser fetches WAVs from `/api/demo/.../say` and streams them as if they were mic audio, so the demo goes through real Prisma STT and real Timbre. It costs credits like a mic session (plus Timbre for any uncached demo utterance).

## 4. Content library

12 texts, 4 per language, each 2 stanzas of 4–5 lines in total:

| Language | Texts (grade) |
|---|---|
| en-IN | en-kite poem (1-2), en-rain poem (1), en-mango passage (3), en-ant passage (2-4) |
| hi-IN | hi-gudiya poem (1), hi-baarish poem (1-2), hi-chidiya passage (2-3), hi-bagicha passage (3-4) |
| gu-IN | gu-patang poem (1), gu-varsad poem (1-2), gu-chakli passage (2-3), gu-shala passage (3-4) |

`content/stt_aliases.json` maps each word to the forms Prisma writes when that word is read correctly (learned from clean readings by `eval/build_aliases.py`).

## 5. Tutor state machine (`TutorEngine`)

States: `SESSION_START → TEACHER_DEMONSTRATION → CHILD_READING ⇄ STALL_PROMPT / UNCERTAIN_AUDIO → INDIVIDUAL_WORD_CORRECTION → COMPLETE_LINE_DEMONSTRATION → COMPLETE_LINE_REPETITION → LINE_COMPLETED / STANZA_COMPLETED / LINE_SKIPPED → SESSION_COMPLETED`.

Key behaviour (from code):
- `start()`: one long `say` = welcome + "today we're going to read" + title + "listen carefully" + **line 1** + "your turn". Only line 1 is demonstrated; later lines are not.
- **Stalls** (`tick`): idle thresholds are fixed, not per child: 6 s before the first word, 4 s at a line start, 2 s mid-line, at least 3.5 s after Buddy speaks. Level 1 = "Listen…" + next ≤3 words (stops at a comma); level 2 = rest of line + "Now you try!"; level 3 = "Take your time", then silence.
- **Corrections**: line-level. Errors are collected while the line is read; at line end (or on a stall after an error) Buddy drills each wrong/skipped word alone, then demonstrates the whole line, then the child repeats it. In a drill, the same close form heard 3× in a row is accepted ("aunt" for "ant").
- **Line skip**: more than `max_line_mistakes = 10` mistakes on one line → "That's okay! Leave this line." Ten is a lot of failed attempts for a 4-year-old.
- **Uncertain audio**: segments of ≥2 tokens with <50 % reliable matches → "Can you read it again?", at most once per 10 s. Never counted as a mistake.
- **Break**: tokens like "stop", "tired", "बस", "થાકી" auto-pause the session.
- **Self-correction**: a trailing unmatched token is held for 2 s (`self_correct_s`) before being judged.
- **Fragments**: speech overlapping Buddy's own speech span is never counted as a mistake.
- Summary: words read alone / helped / to practise, lines completed/skipped, prompts, WPM.

`TutorConfig` holds every threshold, and `eval/replay.py --set key=value` can override any of them, so per-proficiency tuning has a ready hook.

## 6. Frontend and user navigation

Views (hash routes): `#/` home → `#/languages` → `#/library/<lang>` (grade chips **All, Grade 1–5**) → `#/read/<id>` → `#/done` summary; plus `#/about`.

Reader controls: big mic button (`#micBtn`: start / pause / resume), `#pauseBtn`, `#endBtn`, `#listenBtn` ("Listen first"), `#demoBtn` (shown only if `eval/testset/<id>/demo.json` exists), Escape toggles pause. Mic use is gated by a parent consent `<dialog>` (`#consentDlg`, remembered in `localStorage rb.consent`). Live feedback: word highlight classes (`is-read`, `is-helped`, `is-practise`, `is-current`, `is-target`), Buddy speech bubble (`#bubbleLabel`/`#bubbleText`), step tag (`#stepTag`, parent wording), help chip, "what the speech model heard" list. Default language on first visit is **Gujarati** (`gu-IN`), whatever the browser language.

Stable selectors for automation: ids above, `.lang-card[data-lang]`, `.story[data-id]`, `.chip[data-grade]`, `#w<i>` per word, `#micDock[data-state]` (idle/connecting/listening/hearing/talking/paused/error), `#buddy[data-state]`.

## 7. Existing testing infrastructure

- `tests/test_tutor.py`: 31 test functions (42 cases with parametrisation), all offline. `tests/sim.py` drives `TutorEngine` on a simulated clock from a script of `(t, 'ss'|'tr'|'pause'|'resume', text)`.
- `eval/make_testset.py`: synthetic readings (Timbre voices Riyaa, Devansh) per text with variants `clean_a, clean_b, sub, skip, stall, demo`; `eval/make_hardset.py` adds noise (~10 dB SNR) and mid-line pauses (`hard`, `hard2`). WAVs are git-ignored and rebuilt from the TTS cache.
- `eval/run_stt.py`: streams test WAVs through Prisma at real time, records events to `eval/runs/stt/*.json` (**96 recordings committed**: 12 texts × 8 variants). Costs credits only when re-run.
- `eval/replay.py`: replays those recordings through `TutorEngine` offline and scores tracking, stall prompts, error catch, false corrections, per-language results → `eval/RESULTS.md`. **Zero credits.**
- Current results: clean tracking 23/24, errors caught 23/24, stalls prompted 11/12 (median 2.39 s), false corrections 0.104 per 50 words (clean) but 1.02 and 2.22 per 50 words on the noisy/hesitant `hard`/`hard2` sets, and tracking only 3/12 and 2/12 there.

## 8. Limitations found (inputs for the Product Manager, not yet prioritised)

1. **No content for Nursery, LKG or UKG.** All texts are Grade 1–4, and the grade filter offers Grades 1–5, not pre-primary. 26 of the 50 planned personas have no suitable text. Texts are 16–37 words of continuous reading; pre-readers need picture-word, rhyme-repeat or listen-and-repeat formats.
2. **The interface assumes the child can read English instructions.** All bubbles, buttons and the consent dialog are English-only, even in a Hindi or Gujarati session. A non-reading Nursery child gets no audio guidance until the session starts.
3. **Fixed timing for every child.** Stall thresholds (2 s mid-line) and `max_line_mistakes = 10` do not adapt to age or proficiency. Hesitant readers get interrupted; struggling readers face up to 10 failed tries before Buddy moves on.
4. **Robustness drops in noise and with hesitation.** On hard/hard2, tracking falls to 17–25 % and false corrections rise to 1–2.2 per 50 words. Real child speech (higher pitch, slower, mispronounced) is untested: every test reading is a synthetic Timbre voice reading fluently.
5. **Every session spends Prisma credits for its whole duration**, including silence and Buddy's speech. STT connects before the mic is live. Agents running real sessions must be budgeted.
6. **Only line 1 is demonstrated.** Later lines start without a model reading unless the child stalls. "Listen first" exists but is optional and not offered to younger children by default.
7. **No replay or "say it again" control** for a child who didn't catch what Buddy said. No way to replay a single line.
8. **Default language is Gujarati** for first-time visitors, whatever the browser locale.
9. **Demo reader appears only for texts with a `demo.json`.** Today that is all 12 texts, but new content won't get it automatically.
10. **No session resume.** A dropped WebSocket ends the session (`ws.onclose → endSession`), with no reconnect, so progress is lost.
11. **The Hindi and Gujarati teacher phrases are unreviewed**, by the code's own note. Some use masculine forms regardless of the child (Gujarati "વાંચતો રહે" for "keep reading").

## 9. How the agent organisation should plug in (no rewrite needed)

- **Browser agents** can use Playwright with Chromium flags `--use-fake-ui-for-media-stream --use-fake-device-for-media-stream --use-file-for-fake-audio-capture=<wav>`, so a persona's synthetic reading goes through the real mic → Prisma → tutor path. Pre-grant the consent with `localStorage rb.consent=1`, or let young personas fail at it on purpose.
- **Zero-credit mode** (recommended default for agent runs): add an optional `STT_BACKEND=replay` (or `fake`) in `backend/gnani.py` / `main.py` that feeds scripted transcripts from the persona plan instead of opening Prisma. Real-STT runs are reserved for small, budgeted batches and for the Phase 7 audio evaluation.
- **Audio evaluation** builds on `eval/run_stt.py` + `eval/replay.py`: extend variants with persona-driven ones (slow, whisper, repeated word, self-correction, L1-accented substitutions), and add WER, false-correction rate, missed-error rate, alignment accuracy and latency reports per language.
- **Engineering** edits are confined to small, owned files (tutor.py, aligner.py, normalize.py, content/*.json, frontend/app.js), with `tests/` + `eval.replay` as the QA regression gate.
