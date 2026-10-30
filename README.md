# Voice Reading Tutor

A web app that listens to a child read a poem or short story aloud in **Gujarati, English or Hindi**, and helps the way a patient human tutor does:

- it **highlights the child's place** in the text as they read,
- it **says the next few words** when the child gets stuck,
- it **goes back two or three words** when a word is read wrong or skipped ("Let's try that again… *little star*"),
- and at the end it shows the parent **words read, words helped with, and words to practise**.

Built for Gnani.ai's Great Indian AI Internship Challenge 2026 on two Gnani models:

| Gnani model | What it does here |
|---|---|
| **Prisma v2.5** speech-to-text (streaming WebSocket) | Live transcript of the child, in `gu-IN`, `en-IN` or `hi-IN` |
| **Timbre v3.0** text-to-speech (REST, voice *Lakshmi*) | Every greeting, prompt, practice word, whole-line demonstration, praise line and "Listen first" reading; cached so each phrase is paid for once |

## Run it

**Setting it up on a new computer (Mac, Windows or Linux)? Follow [SETUP.md](SETUP.md).** The short version for macOS/Linux, with Python 3.10+:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
```

```bash
cp .env.example .env   # then put your Gnani API key in .env
```

```bash
.venv/bin/uvicorn backend.main:app --port 8765
```

Open http://localhost:8765, pick a language and a text, press **Start reading** and read aloud. Use headphones or speakers at a normal volume. The microphone is muted while the tutor speaks, so the tutor never hears itself.

The first time, a parent or guardian is asked to agree before the microphone is used.

No microphone handy? Press **Demo reader**. An interactive synthetic child (the Timbre voice "Riyaa", never a real child) reads with one scripted wrong word and one mid-line stop. It also answers Buddy: it says the practice word, then re-reads the line. Its audio goes through the same Prisma → tutor → Timbre pipeline, so you can watch the whole teaching loop.

## How it works

```
Browser mic ──16 kHz PCM16, 1024-byte frames──▶ FastAPI /ws/session ──▶ Prisma v2.5 streaming STT
                                                    │  speech_start / transcript events
                                                    ▼
                                       aligner  ──▶  tutor rules  ──▶  "say" actions
                                       (where is      (stall, wrong,     │
                                        the child?)    skip, praise)     ▼
Browser ◀── highlight state + cached Timbre clips ◀── Timbre TTS (disk cache)
```

- **`backend/normalize.py`**: normalises both sides before matching. English: case, punctuation, digits to words. Gujarati and Hindi: nukta, chandrabindu/anusvara, ZWJ, danda. A *loose* key also folds vowel length and nasal marks, and words sharing a stem count as close enough.
- **`backend/aligner.py`**: a small semi-global edit-distance alignment of each transcript segment against the next few expected words. It allows re-reading (going back is free-ish), skipped words (affine gaps), extra words and fillers, and words the speech model wrote together or apart ("પતંગલાલને" = "પતંગ લાલ ને").
- **`backend/tutor.py`**: Buddy the reading teacher, an explicit state machine following the Reading Buddy teaching spec. It is clock-injected, so the same code runs live and in offline replay:

| Situation | Detected by | Buddy does |
|---|---|---|
| Session start | the mic goes live | "Hello! Welcome to Reading Buddy!", names the poem, reads the opening line, "Now it's your turn. Read it with me!" |
| Reading correctly | words match | highlights silently; short praise at the end of a verse |
| Stuck mid-line | no speech for 2 s after the child stops (4 s at a line start) | "Listen…" + the next 2–3 words as a phrase (never past a comma) |
| Still stuck | 3.5 s more | reads the rest of the line, "Now you try!" |
| Still silent | 3.5 s more | "Take your time. I'm here to help." then waits. Silence is never a mistake |
| Line finished with wrong or skipped words | strict matching of every word in the line | **word practice**: "Let's practise this word together." + the word alone; retries are the word alone; "Yes! Very nice!" between words |
| All practice words right | | reads the complete original line, "Now you say the whole line."; the line is checked again |
| Line read right again | | "Wonderful! Let's move to the next line." |
| More than 10 confirmed mistakes on a line | per-line counter | "That's okay! Leave this line. We should move on." Named again at the end and in the parent summary |
| Unclear transcript | under half the segment matches the text | "I didn't quite hear that. Can you read it again?" Not a mistake; at most once per 10 s |
| Child asks to stop | "stop", "tired", "बस", "થાકી ગયો" | "That's okay. We can take a little break." and the session pauses |
| Re-reads / restarts | the transcript jumps back | follows the child |

**What counts as a mistake:** a confirmed wrong or skipped word in a reading, or a wrong attempt at a practice word. Silence, noise, unclear transcripts, fillers ("umm", "अ", "અ"), quick self-corrections, and speech that overlapped Buddy's own voice never count.

**Strict matching** accepts only spelling and script variants that come from the speech model, not near-misses: case, punctuation, nukta, anusvara, vowel length, words written together ("પતંગલાલને"), and known Prisma mishearings. `content/stt_aliases.json` lists those mishearings, learned by `eval/build_aliases.py` from correct synthetic readings, for example "aunt" for "ant". In word practice, the same close-sounding form heard three times in a row is accepted as how the speech model hears that child. A different word, such as "bike" for "kite", never passes.

- **`backend/main.py`**: the FastAPI app. It proxies audio to Prisma (keeping the API key server-side), runs the engine and a 100 ms ticker for stall timing, and turns `say` actions into cached Timbre clips: phrases, the poem title, single practice words (slower) and whole lines. It pre-fetches what Buddy may say next. Nothing about a session is written to disk unless `SAVE_SESSIONS=1` is set, for team test rounds with consenting readers.
- **`frontend/`** ("Reading Buddy"): plain HTML/CSS/JS with no build step or dependencies.
  - `app.js`: hash-routed screens (home → language → library → reader → summary, plus About), the mic pipeline (an AudioWorklet and a streaming resampler to 16 kHz PCM16), tutor clip playback through Web Audio, the animated word marker, progress, pause/resume, and the parent summary built from the real session data.
  - `art.js`: every illustration as hand-built SVG, so there are no image files: Buddy the owl with idle, listening, hearing, talking, happy and sleepy expressions; the children; a scene per story; the language cards; the hero.
  - `cursor.js`: the playful cursor (a smiling star, and a cartoon hand over buttons) with a sparkle trail and click bursts. It runs only on fine-pointer devices and only after it has initialised, so the system cursor is always the fallback. Text fields and selectable text keep the I-beam, and touch screens get tap ripples instead.
  - Reduced-motion settings switch off the confetti, trails and looping animations.
- **`content/*.json`**: 12 self-written texts (4 per language, grades 1–4), split into stanzas and lines.

## Testing

```bash
.venv/bin/python -m pytest -q        # 42 unit tests: normaliser, aligner, every teaching rule, two recorded live sessions (no API calls)
```

The synthetic test set follows the challenge's data rule: no real children's voices.

```bash
.venv/bin/python -m eval.make_testset   # Timbre voices read every text: clean x2, wrong word, skipped word, mid-line stall, demo
```

```bash
.venv/bin/python -m eval.run_stt        # stream every reading through Prisma at real-time pace; record events
```

```bash
.venv/bin/python -m eval.replay         # replay the events through the tutor engine offline and write eval/RESULTS.md
```

`eval.replay` makes no API calls, so the tutor can be tuned for free. To try other settings: `--set stall_mid_s=2.5 align.match_thr=0.65 --no-write`.

**Results on the synthetic set** (full table in [eval/RESULTS.md](eval/RESULTS.md)). A scripted reader can't do word practice, so each reading is scored up to Buddy's first correction:

| Objective | Target | Measured |
|---|---|---|
| Track the reader's place | 9 of 10 readings | 23/24 |
| Prompt on a stall | within 2.5 s, none at line ends | 11/12, median 2.39 s; 0 prompts in 24 clean readings (incl. 3 s line-end pauses) |
| Catch a wrong or skipped word | 7 of 10 | 23/24 (11/12 substitutions, 12/12 skips), median 0.41 s after the line ends |
| Few false corrections | < 1 per 50 correctly read words | 0.10 per 50 (3 of 1,441 words flagged); 1 of 12 held-out clean readings had one ("મારું" heard for "મારો") |
| "Can you read it again?" on clean readings | rare | 0 in 60 clean and error readings |
| Three languages | gu, en, hi | all three |

Strictness has a cost under noise. With ~10 dB SNR noise and a 1–1.8 s hesitation cut into every line, the held-out stress set flags **2.2 correctly read words per 50** for practice (0.85 with the earlier forgiving rules), and asks "can you read it again?" 7 times in 24 readings. Because silence never counts as a mistake, and clear asides are treated as unclear audio, the >10-mistake skip is reached only by repeated confirmed wrong answers.

## Deploy

The app is one service and needs WebSocket support (Render, Railway, Fly.io and similar). It also needs HTTPS, because browsers only give the microphone to secure pages.

```bash
docker build -t reading-tutor . && docker run -p 8000:8000 -e GNANI_API_KEY=... reading-tutor
```

On Render: *New → Blueprint*, point it at this repo (it reads `render.yaml`), and set `GNANI_API_KEY` in the dashboard. The image ships the pre-generated tutor audio in `cache/tts/*.mp3` (`python -m backend.pregen`), so a fresh deploy doesn't spend credits re-creating it.

## Credits used

`cache/usage.json` keeps an approximate local ledger (the server and eval scripts both write to it). Building and testing everything here took about 230 Timbre calls (~5,900 characters) and about 28 minutes of streamed Prisma audio across ~90 sessions. Check the real balance in the Gnani dashboard: the per-unit credit cost isn't published.

## Known limits

- **Prisma can quietly fix a child's mistake.** Its language model sometimes writes the word that *should* be there. The tutor can only catch errors that reach the transcript, so it handles wrong, skipped and stalled words, not pronunciation or sounds.
- **Tested on synthetic adult voices, not children.** Children's voices, accents and reading speed will lower Prisma's accuracy. The next step is test rounds with consenting team members and family (set `SAVE_AUDIO=1` to keep session audio for replay).
- **Feedback comes at pauses.** Prisma streaming returns text when the reader pauses (VAD), not word by word, so the highlight moves in phrase-sized steps. Buddy checks a line once it is finished.
- **Strict matching plus noise means extra practice.** In our noisy stress set, about 2 correctly read words per 50 get flagged for practice. The three-in-a-row rule keeps a child from being stuck on a word the speech model keeps mishearing.
- **Half-duplex:** while Buddy speaks the mic is muted, so words read over Buddy are lost, and misses at the start of such a segment are never counted.
- **No expression scoring.** Buddy demonstrates rhythm and tone with Timbre, but does not measure the child's expression, accent or pronunciation; it checks recognised words only.
- The Gujarati and Hindi texts and tutor phrases were written by us and should be reviewed by a native-speaking teacher before use with children.
