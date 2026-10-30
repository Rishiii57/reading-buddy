# Voice Reading Tutor: project explanation

*Entry to Gnani.ai's Great Indian AI Internship Challenge 2026 · Team: [Member A name], [Member B name]*

## The problem

A child learning to read needs someone sitting next to them: someone who notices when they get stuck and gently says the next word, and who hears a wrong word and has them go back and try again. Most children in grades 1–5 don't have that person every evening, least of all in their home language. We are building a digital learning board for children, and its reading module needs a tutor that can hear a child read aloud in Gujarati, Hindi or English.

## Who it is for

Children from nursery to grade 5 reading short poems and passages from the screen, or reciting from memory. A parent starts the session and reads the summary at the end.

## What it does

Buddy behaves like a primary-school reading teacher sitting beside the child:

- **Starts like a teacher:** greets the child, names the poem, reads the opening line aloud, and says "Now it's your turn. Read it with me!"
- **Follows along**, highlighting the child's place, without interrupting correct reading.
- **Helps when the child is stuck:** after about 2 seconds of silence mid-line, Buddy says the next 2–3 words as a phrase. If the child is still stuck, Buddy reads the rest of the line. If they're still silent: "Take your time. I'm here to help."
- **Teaches every mistake, word by word:** when a line is finished with wrong or skipped words, Buddy says each word on its own and the child repeats it until it's right. Then Buddy reads the whole original line in its natural rhythm, and the child reads it again.
- **Knows when to move on:** after more than 10 confirmed mistakes on one line, Buddy says "That's okay! Leave this line. We should move on." It reminds the child of that line at the end.
- **Never blames the child for the machine:** silence, noise, unclear transcripts and talk are never counted as mistakes. Buddy asks "Can you read it again?" instead, and known speech-model mishearings are accepted.
- **Respects the child:** never says "wrong"; pauses when the child asks to stop; and asks a parent or guardian for permission before using the microphone.
- **Reports honestly:** the child sees words read, words practised, and lines completed or left for another time. Parents get the facts, including each skipped line with its number and the words to practise.

It works in **Gujarati, English and Hindi**, three different scripts, with the same engine.

## Gnani models used

| Model | Used for | How |
|---|---|---|
| **Prisma v2.5** (speech-to-text) | Live transcript of the child reading | Streaming WebSocket (`wss://api.vachana.ai/stt/v3/stream`), 16 kHz PCM, language fixed by the chosen text (`gu-IN`, `en-IN`, `hi-IN`), VAD tuned for a clean web mic (threshold 0.5, 300 ms end-of-speech silence) |
| **Timbre v3.0** (text-to-speech) | Every greeting, prompt, practice word, whole-line demonstration, praise line and the "Listen first" reading | REST (`/api/v1/tts/inference`), voice *Lakshmi* in all three languages, 0.9× speed for words a child should repeat; every clip cached on disk so each phrase costs one call, ever |

We also used Timbre to **build our test set**: two other Timbre voices (Riyaa, Devansh) read every text cleanly, with a deliberate wrong word, with a skipped word and with a mid-line stall. That gave us measurable readings without recording any children, as the challenge's data rule requires.

## How it works

1. The browser captures the microphone with an AudioWorklet, resamples it to 16 kHz 16-bit PCM and streams 1024-byte frames to our FastAPI server.
2. The server forwards the audio to **Prisma v2.5**, keeping the API key off the client. Prisma returns `speech_start` events and a transcript at each pause.
3. Our **aligner** normalises both sides (script variants such as nukta and anusvara, vowel length, punctuation, numbers). It then aligns the transcript against the next expected words with a small edit-distance search, so it can tell a correct read from a substitution, a skip, an extra word, a restart, or words Prisma wrote together.
4. Our **tutor rules** decide what to do: stay silent, prompt, start word practice, demonstrate the line, or praise. A 100 ms timer handles stalls.
5. The tutor's words come from **Timbre**, cached. The next likely prompt is pre-fetched, so a stall prompt plays with no synthesis delay. The microphone is muted while the tutor speaks, so the tutor never hears itself.

## Results

Measured on our synthetic test set: 72 Timbre readings across the 12 texts, streamed through Prisma at real-time pace, then replayed through the tutor engine.

| Objective | Our target | Result |
|---|---|---|
| Track the reader's place | 9 of 10 readings | **23 / 24** clean readings |
| Prompt when stalled, not at line ends | within 2.5 s | **11 / 12** stalls, median **2.39 s**; **0** prompts in 24 clean readings, including 3-second line-end pauses |
| Catch a wrong or skipped word (starts word practice) | 7 of 10 | **23 / 24** (11 substitutions, 12 skips) |
| Few false corrections, with strict matching | < 1 per 50 correctly read words | **0.10** per 50 (3 of 1,441 words) |
| Three languages | gu, en, hi | all three; Prisma word error rate on clean readings: en 1.4%, hi 0.0%, gu 7.3% |

Prisma's own latency was a median 117 ms; a transcript arrives about 0.35 s after the reader pauses.

**Stress test.** We added ~10 dB SNR background noise and cut a 1–1.8 s hesitation into every line. Strict matching then flags about **2.2 correctly read words per 50** for practice on the held-out stress set (0.85 with our earlier forgiving rules). This is the price of not letting real mistakes slip; noisy rooms are the main thing to improve.

**First live reading.** A team member read चिड़िया का घोंसला aloud through the browser microphone. Tracking, the stall prompt and the finish all worked live. It also exposed a bug: when the reader talked to Buddy mid-session ("मतलब पीछे से पढ़ते हैं"), a stray matching word moved the place on. We fixed this: segments that are mostly not the text are now treated as chatter. A second live test on *My Little Kite* checked the fix: a deliberate "bike" for "kite" (caught), a mid-line stop (prompted), and off-script talk in English and Hindi ("wait what", "abhi tak"). It also exposed asides being taken as misreads, praise after a repeated slip, and a too-loose rule for tiny words, all now fixed. Both sessions are kept as regression tests (`tests/fixtures/`).

## Known limits (honestly)

- **The speech model can hide a mistake.** Prisma sometimes writes the word that should be there even when the child said something else. So the tutor targets wrong, skipped and stalled words, not pronunciation.
- **No children's voices yet.** All tests use synthetic adult voices. Children's speech will be harder for Prisma; our next step is test rounds with consenting family members.
- **Feedback at pauses, not mid-word.** Streaming transcripts arrive at each pause, so the highlight moves in phrase-sized steps and a mistake inside a fluent line is caught at the next pause.
- **Noise** raises false corrections, as shown above.
- Our Gujarati and Hindi texts and phrases are self-written and need review by a native-speaking teacher.

## Who did what

- **[Member A]**: speech and tutor engine: Gnani API integration (Prisma streaming, Timbre TTS and caching), text alignment, stall and error detection, tutor rules, credit tracking.
- **[Member B]**: app, content and testing: web UI (highlighting, mic controls, summary), the 12 texts in three languages, the synthetic test set and results, demo video, this write-up and social posts.

*(Edit to match how you actually split the work. Each of you will be interviewed separately, so both should be able to explain the whole system.)*
