# User research report: cycle c01 / baseline

Generated 2026-11-09T18:37:11 by the AI Product Manager from 50 simulated child sessions run against the real app (Playwright + real tutor engine; simulated speech channel, no credits). Simulated satisfaction is **not** speech-recognition accuracy: see the separate audio section.

## At a glance

|  |  |
|---|---|
| Agents executed | 50 |
| Got a reading session going | 42 (84%) |
| Finished the text | 10 (20%) |
| Abandoned, could not start, or left | 34 (68%) |
| Harness errors (excluded) | 0 |
| Distinct problems (root causes) | 15 |
| Unclassified symptoms | 3 |

Outcomes: abandoned_frustration 23, completed 10, ended_early 6, left_before_start 6, abandoned_attention 3, could_not_start 2

## Top problems (by priority)

- **P0 No reading material for Nursery, LKG and UKG** (REQ-PREPRIMARY-CONTENT): 26/50 children (52%), pre-primary reach 100%. “The words were too hard. I can't read those yet.”
- **P0 Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass** (REQ-CONSENT-GATE): 9/50 children (18%), pre-primary reach 15%. “There was a box for parents, so I just ticked it myself.”
- **P1 Before a session starts, all guidance is written English; non-readers get no spoken instructions** (REQ-SPOKEN-ONBOARDING): 35/50 children (70%), pre-primary reach 96%. “Nobody told me what to do.”
- **P1 Stall prompt fires during normal thinking pauses of slow and hesitant readers** (REQ-STALL-TIMING): 20/50 children (40%), pre-primary reach 31%. “I was just thinking and Buddy jumped in.”
- **P2 Tapping the big microphone during a session pauses it** (REQ-MIC-TOGGLE): 19/50 children (38%), pre-primary reach 42%. “I pressed the mic to talk and it stopped!”
- **P2 A slip followed by a thinking pause triggers word practice mid-line** (REQ-MIDLINE-CORRECTION): 13/50 children (26%), pre-primary reach 31%. “Buddy talked when I was thinking!”
- **P2 Correctly read words flagged for practice (tutor/aligner)** (REQ-FALSE-CORRECTION-TUTOR): 4/50 children (8%), pre-primary reach 8%. “Buddy said I got a word wrong but I read it right.”
- **P2 Children cannot find a text or leave the reading page by accident** (REQ-NAVIGATION): 12/50 children (24%), pre-primary reach 35%. “Where did my poem go?”
- **P2 Word practice and line repetition loop on the same word or line** (REQ-DRILL-LOOP): 3/50 children (6%), pre-primary reach 0%. “Buddy made me say the same word again and again.”
- **P2 Correct reading misheard by the speech model (child voices)** (REQ-FALSE-CORRECTION-STT): 4/50 children (8%), pre-primary reach 4%. “I read it right but Buddy heard something else.”

## Grade-wise findings

| Grade | n | Started | Finished | Abandoned | Covered | Interruptions/agent | Peak frustration |
|---|---|---|---|---|---|---|---|
| Nursery | 10 | 70% | 0% | 100% | 10% | 0.8 | 3.285 |
| LKG | 8 | 75% | 0% | 75% | 7% | 1.125 | 2.856 |
| UKG | 8 | 75% | 0% | 75% | 20% | 1.125 | 3.288 |
| Class 1 | 6 | 83% | 0% | 83% | 33% | 1.5 | 3.458 |
| Class 2 | 6 | 100% | 17% | 83% | 71% | 1.0 | 3.65 |
| Class 3 | 6 | 100% | 83% | 17% | 97% | 2.167 | 2.575 |
| Class 4 | 6 | 100% | 67% | 17% | 88% | 0.0 | 1.175 |

- **Nursery**: No reading material for Nursery, LKG and UKG (10); Before a session starts, all guidance is written English; non-readers get no spoken instructions (10); Children end up in, or hear, a language they did not choose (7)
- **LKG**: No reading material for Nursery, LKG and UKG (8); Before a session starts, all guidance is written English; non-readers get no spoken instructions (8); Buddy's opening talk is long before the child gets a turn (5)
- **UKG**: No reading material for Nursery, LKG and UKG (8); Before a session starts, all guidance is written English; non-readers get no spoken instructions (7); Tapping the big microphone during a session pauses it (5)
- **Class 1**: Stall prompt fires during normal thinking pauses of slow and hesitant readers (4); Buddy's opening talk is long before the child gets a turn (4); Before a session starts, all guidance is written English; non-readers get no spoken instructions (3)
- **Class 2**: Buddy's opening talk is long before the child gets a turn (6); Tapping the big microphone during a session pauses it (5); Stall prompt fires during normal thinking pauses of slow and hesitant readers (4)
- **Class 3**: What a child says while Buddy is talking is silently discarded (5); Buddy's opening talk is long before the child gets a turn (5); Stall prompt fires during normal thinking pauses of slow and hesitant readers (4)
- **Class 4**: What a child says while Buddy is talking is silently discarded (4); Buddy's opening talk is long before the child gets a turn (4); Before a session starts, all guidance is written English; non-readers get no spoken instructions (2)

## Language-wise findings

| Language | n | Started | Finished | Covered | False corr./agent | Missed errors/agent | Wrong language |
|---|---|---|---|---|---|---|---|
| English | 17 | 88% | 12% | 42% | 0.118 | 0.471 | 29% |
| Gujarati | 16 | 88% | 25% | 41% | 0.312 | 0.438 | 19% |
| Hindi | 17 | 76% | 24% | 40% | 0.059 | 0.235 | 18% |

- **English**: What a child says while Buddy is talking is silently discarded (12); Buddy's opening talk is long before the child gets a turn (11); No reading material for Nursery, LKG and UKG (9)
- **Hindi**: Before a session starts, all guidance is written English; non-readers get no spoken instructions (15); Buddy's opening talk is long before the child gets a turn (12); No reading material for Nursery, LKG and UKG (9)
- **Gujarati**: Before a session starts, all guidance is written English; non-readers get no spoken instructions (12); Buddy's opening talk is long before the child gets a turn (12); No reading material for Nursery, LKG and UKG (8)

## What children liked

- “I liked it when Buddy said well done.” (18)
- “I finished the whole poem!” (11)
- “When I got stuck Buddy told me the words.” (10)
- “Buddy said yay! I liked that.” (2)

## Unclassified symptoms (kept for review)

- C1-04: INTERRUPTED_WHILE_THINKING Buddy started talking 0.2 s into a planned 2.91 s thinking pause.
- C3-01: INTERRUPTED_WHILE_THINKING Buddy started talking 0.2 s into a planned 2.21 s thinking pause.
- U07: INTERRUPTED_WHILE_THINKING Buddy started talking 0.2 s into a planned 3.31 s thinking pause.

## Speech and audio evaluation (measured, separate from simulated satisfaction)

| Language | WER (clean) | False corr./50 words | Missed error rate | Alignment acc. | Latency ms |
|---|---|---|---|---|---|
| English | 0.014 | 0.0 | 0.0 | 1.0 | 119 |
| Hindi | 0.0 | 0.0 | 0.0 | 1.0 | 120 |
| Gujarati | 0.073 | 0.325 | 0.125 | 0.875 | 109 |

Measured on synthetic adult voices: clean WER is highest for Gujarati (0.073); noise and hesitation cut tracking to 0.281–0.688 of checkpoints. Text-level: a 2.5 s mid-line thinking pause is interrupted in English 0.83, Gujarati 0.58, Hindi 0.92 of cases. Child-voice accuracy is unmeasured.

## Method and limits

- Children are deterministic persona policies (seeded), not LLMs; they perceive only the screen and Buddy's voice.
- Speech is simulated: reading errors come from the persona; recognition errors from a coarse per-language model (measured adult-TTS WER + an assumed child-voice penalty). Findings that depend on real child speech are marked for the audio evaluation.
- Uncached Buddy lines play as timed placeholder audio (no Timbre calls); timing is realistic, sound is not.
- Evidence for every claim: `agent_org/runs/c01/baseline/<agent>/` (report, trace, screenshots, server log).
