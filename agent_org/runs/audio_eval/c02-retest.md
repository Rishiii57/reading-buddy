# Speech and audio evaluation: c02-retest

Generated 2026-11-10T11:36:41 from app commit `4be878d`.

> Measured speech-recognition numbers (Part A) and tutor-decision numbers on scripted transcripts (Part B) are reported separately from the simulated children's satisfaction. Neither includes real children's voices.

**Headline:** Measured on synthetic adult voices: clean WER is highest for Gujarati (0.073); noise and hesitation cut tracking to 0.281–0.656 of checkpoints. Text-level: a 2.5 s mid-line thinking pause is interrupted in English 0.0, Gujarati 0.0, Hindi 0.0 of cases. Child-voice accuracy is unmeasured.

## Part A: Prisma on recorded synthetic speech (measured)

| Language | WER clean | WER sub | WER skip | WER stall | WER noise+hesitation | Latency ms | Transcript after speech s | Alignment acc. | Alignment acc. (noisy) | Missed errors | False corr./50 | False corr./50 (noisy) | Stalls detected |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| English | 0.014 | 0.034 | 0.018 | 0.01 | 0.083 | 119 | 0.32 | 1.0 | 0.281 | 0.0 | 0.0 | 2.049 | 4/4 |
| Hindi | 0.0 | 0.015 | 0.0 | 0.0 | 0.155 | 120 | 0.23 | 1.0 | 0.656 | 0.0 | 0.0 | 1.064 | 4/4 |
| Gujarati | 0.073 | 0.1 | 0.061 | 0.112 | 0.292 | 109 | 0.31 | 0.875 | 0.438 | 0.125 | 0.325 | 1.623 | 3/4 |

96 recordings (12 texts × 8 variants, 2 synthetic voices). WER is against the words actually spoken (a substituted word counts as what was said).

## Part B: tutor decisions on scripted transcripts (text level, no audio)

Line 1 of every text, 3 random variants per condition. `false corr./50`: corrections of correctly read words per 50 such words. `missed`: injected reading errors never practised. `pause interrupted`: share of mid-line pauses during which Buddy spoke (stall prompt or correction).

### English

| Condition | Lines | False corr./50 | Missed error rate | Pause interrupted |
|---|---|---|---|---|
| clean | 27 | 0.0 | - | - |
| pause_1.5 | 27 | 0.0 | - | 0.0 |
| pause_2.5 | 27 | 0.0 | - | 0.0 |
| pause_3.5 | 27 | 0.0 | - | 0.19 |
| repeat_word | 27 | 0.0 | - | - |
| self_correct | 27 | 0.0 | - | - |
| skip_small | 27 | 0.0 | 0.43 | - |
| slow_word_by_word | 27 | 0.0 | - | 0.0 |
| substitute | 27 | 0.0 | 0.59 | - |

### Gujarati

| Condition | Lines | False corr./50 | Missed error rate | Pause interrupted |
|---|---|---|---|---|
| clean | 24 | 0.0 | - | - |
| matra_variant | 24 | 0.0 | 0.62 | - |
| pause_1.5 | 24 | 0.0 | - | 0.0 |
| pause_2.5 | 24 | 0.0 | - | 0.0 |
| pause_3.5 | 24 | 0.0 | - | 0.12 |
| repeat_word | 24 | 0.0 | - | - |
| self_correct | 24 | 0.0 | - | - |
| skip_small | 24 | 2.08 | 0.75 | - |
| slow_word_by_word | 24 | 0.0 | - | 0.0 |
| substitute | 24 | 0.0 | 0.5 | - |

### Hindi

| Condition | Lines | False corr./50 | Missed error rate | Pause interrupted |
|---|---|---|---|---|
| clean | 24 | 0.0 | - | - |
| matra_variant | 24 | 0.0 | 0.92 | - |
| pause_1.5 | 24 | 0.0 | - | 0.0 |
| pause_2.5 | 24 | 0.0 | - | 0.0 |
| pause_3.5 | 24 | 0.0 | - | 0.25 |
| repeat_word | 24 | 0.0 | - | - |
| self_correct | 24 | 0.0 | - | - |
| skip_small | 24 | 0.0 | 0.76 | - |
| slow_word_by_word | 24 | 0.0 | - | 0.0 |
| substitute | 24 | 0.0 | 0.5 | - |

## Not yet measured

- Children's voices (pitch, articulation): needs consented, safeguarded recordings (human approval).
- Whispering, fast/slow speech and accents on real audio: `python -m agent_org.audio_eval.augment` builds these variants offline from cached readings; streaming them through Prisma costs credits (`eval/run_stt.py`).
