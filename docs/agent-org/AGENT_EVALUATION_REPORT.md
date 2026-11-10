# Agent evaluation report

Initial product (`95fd951`, run `c01/baseline-v2`) vs improved product (`b51d5cc`, run `c02/retest`): the same 50 simulated children, the same seeds, and the same child-agent code, so differences come from the app. Harness errors (excluded): 0 before, 0 after.

> Simulated children and simulated speech: these numbers measure the interface, the tutor's behaviour and the learning loop as children of different levels experience them. They are not speech-recognition accuracy (see the audio section) and not results from real children.

## Headline results

| Measure | Initial | Improved | Change |
|---|---|---|---|
| share of agents who got a reading session going | 0.84 | 0.88 | ▲ better |
| share of agents who finished the text | 0.18 | 0.4 | ▲ better |
| share of agents who gave up, could not start, or left | 0.72 | 0.4 | ▲ better |
| average share of the text covered (read or helped) | 0.408 | 0.626 | ▲ better |
| all interruptions of thinking pauses | 1.2 | 0.68 | ▲ better |
| stall prompts that cut into a child's thinking pause | 0.8 | 0.36 | ▲ better |
| share of agents whose session paused when they tapped the mic to talk | 0.42 | 0.0 | ▲ better |
| share of agents who met written-only instructions they could not read | 0.7 | 0.0 | ▲ better |
| share of agents stopped by the grown-up consent box | 0.1 | 0.0 | ▲ better |
| share of agents (children) who ticked the parent box themselves | 0.08 | 0.0 | ▲ better |
| share of agents with no text at their level | 0.52 | 0.1 | ▲ better |
| words the child said that were dropped because the mic was muted | 3.12 | 2.6 | ▲ better |
| share of agents asked to repeat the same word 3+ times | 0.2 | 0.1 | ▲ better |
| corrections of words the child read right | 0.24 | 0.16 | ▲ better |
| child misreadings accepted as correct | 0.14 | 0.34 | ▼ worse |
| share of agents who sat through 12 s+ of Buddy talking in one go | 0.64 | 0.66 | ▼ worse |
| median seconds from tapping the mic to the child's first turn | 14.2 | 13.8 | ▲ better |
| mean peak frustration | 3.152 | 1.704 | ▲ better |

## By grade

| Grade | n | Started | Finished | Covered | Interruptions/child | Peak frustration |
|---|---|---|---|---|---|---|
| Nursery | 10 | 0.7 → 0.7 | 0.0 → 0.0 | 0.069 → 0.185 | 0.7 → 0.6 | 3.19 → 1.835 |
| LKG | 8 | 0.75 → 0.75 | 0.0 → 0.0 | 0.131 → 0.35 | 1.0 → 1.375 | 3.131 → 2.288 |
| UKG | 8 | 0.75 → 0.875 | 0.0 → 0.375 | 0.252 → 0.661 | 1.75 → 0.875 | 3.675 → 1.281 |
| Class 1 | 6 | 0.833 → 1.0 | 0.0 → 0.833 | 0.417 → 0.9 | 2.0 → 0.167 | 3.858 → 1.592 |
| Class 2 | 6 | 1.0 → 1.0 | 0.0 → 0.333 | 0.485 → 0.753 | 1.0 → 0.5 | 3.65 → 2.192 |
| Class 3 | 6 | 1.0 → 1.0 | 0.5 → 0.667 | 0.872 → 0.911 | 1.667 → 1.0 | 2.9 → 1.242 |
| Class 4 | 6 | 1.0 → 1.0 | 1.0 → 1.0 | 1.0 → 1.0 | 0.5 → 0.0 | 1.467 → 1.358 |

## By language

| Language | n | Started | Finished | Covered | False corrections/child | Missed errors/child |
|---|---|---|---|---|---|---|
| English | 17 | 0.882 → 0.941 | 0.118 → 0.235 | 0.33 → 0.601 | 0.235 → 0.235 | 0.059 → 0.235 |
| Hindi | 17 | 0.765 → 0.765 | 0.176 → 0.471 | 0.401 → 0.601 | 0.118 → 0.059 | 0.176 → 0.235 |
| Gujarati | 16 | 0.875 → 0.938 | 0.25 → 0.5 | 0.498 → 0.681 | 0.375 → 0.188 | 0.188 → 0.562 |

## Outcomes

| Outcome | Initial | Improved |
|---|---|---|
| abandoned_attention | 2 | 9 |
| abandoned_frustration | 26 | 5 |
| completed | 9 | 20 |
| could_not_start | 2 | 0 |
| ended_early | 5 | 10 |
| left_before_start | 6 | 6 |

## Children affected per symptom

| Symptom | Initial | Improved |
|---|---|---|
| NO_SPOKEN_GUIDANCE_BEFORE_START | 35 | 0 |
| LONG_TUTOR_TALK | 32 | 33 |
| INTERRUPTED_WHILE_THINKING | 31 | 17 |
| SPEECH_IGNORED_WHILE_BUDDY_TALKS | 29 | 26 |
| NO_TEXT_FOR_MY_LEVEL | 26 | 5 |
| MIC_TAP_PAUSED_SESSION | 21 | 0 |
| WRONG_LANGUAGE_TEXT | 11 | 11 |
| LEFT_READING_BY_ACCIDENT | 11 | 18 |
| SAME_WORD_ASKED_AGAIN_AND_AGAIN | 10 | 5 |
| BUDDY_LANGUAGE_NOT_UNDERSTOOD | 8 | 8 |
| FALSE_CORRECTION | 6 | 5 |
| FALSE_CORRECTION_STT | 6 | 2 |
| CONSENT_BLOCKS_CHILD | 5 | 0 |
| NO_REPLAY_CONTROL | 4 | 4 |
| CONSENT_SELF_APPROVED | 4 | 0 |
| MISSED_ERROR | 4 | 14 |
| COULD_NOT_START_SESSION | 2 | 0 |
| LISTEN_FIRST_NOT_FOUND | 1 | 1 |
| RESTART_NOT_FOUND | 1 | 1 |

## What changed between the two builds

- **REQ-CONSENT-GATE** (Frontend Engineer): Round 2: branch refreshed onto the integration build (spoken onboarding, stall timing, mic fix merged); consent removal unchanged · 2 engineering round(s), QA: returned_to_engineering, returned_to_engineering · merged as accepted by human directive (QA evidence attached)
- **REQ-MIC-TOGGLE** (Frontend Engineer): keep mic icon visible on hover while listening · 2 engineering round(s), QA: validated_fixed · merged as QA-validated
- **REQ-PREPRIMARY-CONTENT** (Data Engineer): Round 4: shorter echo demonstration (line + 'your turn' only) · 4 engineering round(s), QA: returned_to_engineering, returned_to_engineering, returned_to_engineering, returned_to_engineering · merged as accepted by human directive (QA evidence attached)
- **REQ-SPOKEN-ONBOARDING** (Frontend Engineer): Buddy speaks a short hint (cached phrase) when a text opens; reader bubbles in the text's language · 1 engineering round(s), QA: validated_fixed · merged as QA-validated
- **REQ-STALL-TIMING** (Backend Engineer): Round 2: mid-line stall threshold 3.0 s for all texts (3.4 s for Grade 1/pre-primary); adaptive learning kept on top · 2 engineering round(s), QA: returned_to_engineering, validated_fixed · merged as QA-validated

## Speech and audio (measured separately)

Measured on synthetic adult voices: clean WER is highest for Gujarati (0.073); noise and hesitation cut tracking to 0.281–0.656 of checkpoints. Text-level: a 2.5 s mid-line thinking pause is interrupted in English 0.0, Gujarati 0.0, Hindi 0.0 of cases. Child-voice accuracy is unmeasured.

| Language | WER clean | WER noise+hesitation | Alignment | Missed error rate | False corr./50 words | Latency ms |
|---|---|---|---|---|---|---|
| English | 0.014 | 0.083 | 1.0 | 0.0 | 0.0 | 119 |
| Hindi | 0.0 | 0.155 | 1.0 | 0.0 | 0.0 | 120 |
| Gujarati | 0.073 | 0.292 | 0.875 | 0.125 | 0.325 | 109 |

Text-level tutor test, share of 2.5 s / 3.5 s mid-line pauses interrupted: English 0.0 / 0.19, Gujarati 0.0 / 0.12, Hindi 0.0 / 0.25 (app `4be878d`).

## Evaluation of the agent system

| Check | Result |
|---|---|
| Personas | 50 (Nursery 10, LKG 8, UKG 8, Class 1–4 six each; en/hi/gu 17/17/16) |
| Behaviour distance between personas (19 traits) | min 0.05, median 1.227; identical pairs: 0 |
| Distinct (outcome, symptom-set) experiences in one 50-child run | 40 of 50 |
| Real product interaction | Playwright/Chromium on the real UI, WebSocket protocol and tutor engine; coordinate taps, scrolling |
| Blindness | agents read only the screen and Buddy's voice; no code, docs or other reports |
| Harness errors | 0 / 0 (excluded from findings, retried once) |
| Cost of a 50-child run | 1359.4 s wall time, Gnani credits 0, LLM tokens 0 |
| Would-be live STT for the same sessions | 4316.8 s of audio |

## Reading the results

- Biggest gains: finishing a text (Class 1 0 → 83 %, UKG 0 → 38 %), abandonment, coverage, frustration, and the complete removal of the mic-tap pause, written-only onboarding and consent dead ends.
- Worse: misreadings accepted as correct rose. Most of this is intended: pre-primary rhymes now accept imperfect repetition (echo reading), and children simply read more words. For Class 2-4 it is REQ-LENIENT-MATCHING (awaiting a product decision).
- Unchanged problems (deferred, next cycle): Buddy's long opening talk, speech lost while Buddy talks, Nursery children still not finishing a rhyme, and children leaving the reading page by accident.

## Honest limits

- The children are deterministic, seeded behaviour policies, not people and not LLMs. Their speech and the speech model's errors are modelled. Findings that depend on real children's voices (accuracy, accent, pitch) need consented recordings or the credit-spending audio steps in RUN_INSTRUCTIONS.md.
- Uncached Buddy lines play as timed placeholders in simulation (no Timbre access from the build machine). The 13 new rhymes and the new phrases need `python -m backend.pregen --words` once on a machine with the key.
- Sessions run in real time; parallel runs on a 2-CPU machine add timing noise, so QA compares the same personas and seeds on both builds and uses two seeds per persona.
- During the cycle the measuring instrument was fixed several times (tap detection, hearing, level tags, on-screen preference). This comparison re-ran the initial build with the final instrument for that reason.
- Two changes were merged on the human's directive although QA returned them (consent removal, pre-primary rhymes); the QA evidence and reasons are in the backlog and PRODUCT_IMPROVEMENT_HISTORY.md.
