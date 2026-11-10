# User research report: cycle c02 / retest

Generated 2026-11-10T11:37:02 by the AI Product Manager from 50 simulated child sessions run against the real app (Playwright + real tutor engine; simulated speech channel, no credits). Simulated satisfaction is **not** speech-recognition accuracy: see the separate audio section.

## At a glance

|  |  |
|---|---|
| Agents executed | 50 |
| Got a reading session going | 44 (88%) |
| Finished the text | 20 (40%) |
| Abandoned, could not start, or left | 20 (40%) |
| Harness errors (excluded) | 0 |
| Distinct problems (root causes) | 14 |
| Unclassified symptoms | 4 |

Outcomes: completed 20, ended_early 10, abandoned_attention 9, left_before_start 6, abandoned_frustration 5

## Top problems (by priority)

- **P1 No reading material for Nursery, LKG and UKG** (REQ-PREPRIMARY-CONTENT): 5/50 children (10%), pre-primary reach 19%. “The words were too hard. I can't read those yet.”
- **P1 Stall prompt fires during normal thinking pauses of slow and hesitant readers** (REQ-STALL-TIMING): 11/50 children (22%), pre-primary reach 38%. “Buddy talked when I was thinking!”
- **P2 Children cannot find a text or leave the reading page by accident** (REQ-NAVIGATION): 18/50 children (36%), pre-primary reach 62%. “Where did my poem go?”
- **P2 Correctly read words flagged for practice (tutor/aligner)** (REQ-FALSE-CORRECTION-TUTOR): 5/50 children (10%), pre-primary reach 4%. “Buddy said I got a word wrong but I read it right.”
- **P2 A slip followed by a thinking pause triggers word practice mid-line** (REQ-MIDLINE-CORRECTION): 3/50 children (6%), pre-primary reach 4%. “I was just thinking and Buddy jumped in.”
- **P2 Word practice and line repetition loop on the same word or line** (REQ-DRILL-LOOP): 5/50 children (10%), pre-primary reach 4%. “Buddy made me say the same word again and again.”
- **P2 Correct reading misheard by the speech model (child voices)** (REQ-FALSE-CORRECTION-STT): 2/50 children (4%), pre-primary reach 0%. “I read it right but Buddy heard something else.”
- **P2 Before a session starts, all guidance is written English; non-readers get no spoken instructions** (REQ-SPOKEN-ONBOARDING): 1/50 children (2%), pre-primary reach 4%. “I wanted it to read to me first.”
- **P2 Buddy's opening talk is long before the child gets a turn** (REQ-LONG-INTRO): 33/50 children (66%), pre-primary reach 62%. “Buddy talks a lot before I get to read.”
- **P2 What a child says while Buddy is talking is silently discarded** (REQ-TALK-OVER-BUDDY): 26/50 children (52%), pre-primary reach 50%. “Buddy didn't hear me when I was talking.”

## Grade-wise findings

| Grade | n | Started | Finished | Abandoned | Covered | Interruptions/agent | Peak frustration |
|---|---|---|---|---|---|---|---|
| Nursery | 10 | 70% | 0% | 70% | 18% | 0.6 | 1.835 |
| LKG | 8 | 75% | 0% | 50% | 35% | 1.375 | 2.288 |
| UKG | 8 | 88% | 38% | 38% | 66% | 0.875 | 1.281 |
| Class 1 | 6 | 100% | 83% | 0% | 90% | 0.167 | 1.592 |
| Class 2 | 6 | 100% | 33% | 67% | 75% | 0.5 | 2.192 |
| Class 3 | 6 | 100% | 67% | 33% | 91% | 1.0 | 1.242 |
| Class 4 | 6 | 100% | 100% | 0% | 100% | 0.0 | 1.358 |

- **Nursery**: Children end up in, or hear, a language they did not choose (7); Buddy's opening talk is long before the child gets a turn (6); Children cannot find a text or leave the reading page by accident (6)
- **LKG**: Children cannot find a text or leave the reading page by accident (6); What a child says while Buddy is talking is silently discarded (5); Buddy's opening talk is long before the child gets a turn (5)
- **UKG**: Buddy's opening talk is long before the child gets a turn (5); What a child says while Buddy is talking is silently discarded (4); Children cannot find a text or leave the reading page by accident (4)
- **Class 1**: What a child says while Buddy is talking is silently discarded (4); Buddy's opening talk is long before the child gets a turn (3); Some misreadings are accepted as correct (vowel length, matras, word endings, small words) (3)
- **Class 2**: Buddy's opening talk is long before the child gets a turn (4); What a child says while Buddy is talking is silently discarded (3); Word practice and line repetition loop on the same word or line (3)
- **Class 3**: Buddy's opening talk is long before the child gets a turn (6); Some misreadings are accepted as correct (vowel length, matras, word endings, small words) (3); What a child says while Buddy is talking is silently discarded (2)
- **Class 4**: What a child says while Buddy is talking is silently discarded (4); Buddy's opening talk is long before the child gets a turn (4); Correct reading misheard by the speech model (child voices) (2)

## Language-wise findings

| Language | n | Started | Finished | Covered | False corr./agent | Missed errors/agent | Wrong language |
|---|---|---|---|---|---|---|---|
| English | 17 | 94% | 24% | 60% | 0.235 | 0.235 | 29% |
| Gujarati | 16 | 94% | 50% | 68% | 0.188 | 0.562 | 19% |
| Hindi | 17 | 76% | 47% | 60% | 0.059 | 0.235 | 18% |

- **English**: What a child says while Buddy is talking is silently discarded (12); Buddy's opening talk is long before the child gets a turn (9); Stall prompt fires during normal thinking pauses of slow and hesitant readers (6)
- **Hindi**: Buddy's opening talk is long before the child gets a turn (12); Children cannot find a text or leave the reading page by accident (8); What a child says while Buddy is talking is silently discarded (7)
- **Gujarati**: Buddy's opening talk is long before the child gets a turn (12); What a child says while Buddy is talking is silently discarded (7); Some misreadings are accepted as correct (vowel length, matras, word endings, small words) (7)

## What children liked

- “I liked it when Buddy said well done.” (23)
- “I finished the whole poem!” (17)
- “Buddy said yay! I liked that.” (8)
- “When I got stuck Buddy told me the words.” (7)
- “Buddy helped me with the hard word.” (6)
- “I did it!” (4)

## Unclassified symptoms (kept for review)

- C1-03: INTERRUPTED_WHILE_THINKING Buddy started talking 3.4 s into a planned 3.49 s thinking pause.
- C2-05: INTERRUPTED_WHILE_THINKING Buddy started talking 0.2 s into a planned 2.56 s thinking pause.
- L03: INTERRUPTED_WHILE_THINKING Buddy started talking 0.2 s into a planned 4.09 s thinking pause.
- N02: INTERRUPTED_WHILE_THINKING Buddy started talking 0.2 s into a planned 2.16 s thinking pause.

## Speech and audio evaluation (measured, separate from simulated satisfaction)

| Language | WER (clean) | False corr./50 words | Missed error rate | Alignment acc. | Latency ms |
|---|---|---|---|---|---|
| English | 0.014 | 0.0 | 0.0 | 1.0 | 119 |
| Hindi | 0.0 | 0.0 | 0.0 | 1.0 | 120 |
| Gujarati | 0.073 | 0.325 | 0.125 | 0.875 | 109 |

Measured on synthetic adult voices: clean WER is highest for Gujarati (0.073); noise and hesitation cut tracking to 0.281–0.656 of checkpoints. Text-level: a 2.5 s mid-line thinking pause is interrupted in English 0.0, Gujarati 0.0, Hindi 0.0 of cases. Child-voice accuracy is unmeasured.

## Method and limits

- Children are deterministic persona policies (seeded), not LLMs; they perceive only the screen and Buddy's voice.
- Speech is simulated: reading errors come from the persona; recognition errors from a coarse per-language model (measured adult-TTS WER + an assumed child-voice penalty). Findings that depend on real child speech are marked for the audio evaluation.
- Uncached Buddy lines play as timed placeholder audio (no Timbre calls); timing is realistic, sound is not.
- Evidence for every claim: `agent_org/runs/c02/retest/<agent>/` (report, trace, screenshots, server log).
