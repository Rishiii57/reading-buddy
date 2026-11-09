# User research report: cycle pilot / p1

Generated 2026-11-09T18:05:50 by the AI Product Manager from 5 simulated child sessions run against the real app (Playwright + real tutor engine; simulated speech channel, no credits). Simulated satisfaction is **not** speech-recognition accuracy: see the separate audio section.

## At a glance

|  |  |
|---|---|
| Agents executed | 5 |
| Got a reading session going | 4 (80%) |
| Finished the text | 1 (20%) |
| Abandoned, could not start, or left | 4 (80%) |
| Harness errors (excluded) | 0 |
| Distinct problems (root causes) | 10 |
| Unclassified symptoms | 0 |

Outcomes: abandoned_frustration 3, completed 1, could_not_start 1

## Top problems (by priority)

- **P0 No reading material for Nursery, LKG and UKG** (REQ-PREPRIMARY-CONTENT): 3/5 children (60%), pre-primary reach 100%. “The words were too hard. I can't read those yet.”
- **P0 Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass** (REQ-CONSENT-GATE): 3/5 children (60%), pre-primary reach 33%. “There was a box for parents, so I just ticked it myself.”
- **P1 Before a session starts, all guidance is written English; non-readers get no spoken instructions** (REQ-SPOKEN-ONBOARDING): 3/5 children (60%), pre-primary reach 100%. “Nobody told me what to do.”
- **P1 Stall prompt fires during normal thinking pauses of slow and hesitant readers** (REQ-STALL-TIMING): 3/5 children (60%), pre-primary reach 67%. “Buddy talked when I was thinking!”
- **P1 Tapping the big microphone during a session pauses it** (REQ-MIC-TOGGLE): 3/5 children (60%), pre-primary reach 67%. “I pressed the mic to talk and it stopped!”
- **P2 Word practice and line repetition loop on the same word or line** (REQ-DRILL-LOOP): 1/5 children (20%), pre-primary reach 0%. “Buddy made me say the same word again and again.”
- **P2 Buddy's opening talk is long before the child gets a turn** (REQ-LONG-INTRO): 4/5 children (80%), pre-primary reach 67%. “Buddy talks a lot before I get to read.”
- **P2 What a child says while Buddy is talking is silently discarded** (REQ-TALK-OVER-BUDDY): 3/5 children (60%), pre-primary reach 33%. “Buddy didn't hear me when I was talking.”
- **P2 Children end up in, or hear, a language they did not choose** (REQ-LANGUAGE-SELECTION): 1/5 children (20%), pre-primary reach 33%. “This isn't my language!”
- **P3 Some misreadings are accepted as correct (vowel length, matras, word endings, small words)** (REQ-LENIENT-MATCHING): 2/5 children (40%), pre-primary reach 0%. 

## Grade-wise findings

| Grade | n | Started | Finished | Abandoned | Covered | Interruptions/agent | Peak frustration |
|---|---|---|---|---|---|---|---|
| Nursery | 1 | 0% | 0% | 100% | 0% | 0.0 | 2.4 |
| LKG | 1 | 100% | 0% | 100% | 12% | 2.0 | 4.15 |
| UKG | 1 | 100% | 0% | 100% | 31% | 2.0 | 4.3 |
| Class 2 | 1 | 100% | 0% | 100% | 43% | 0.0 | 4.95 |
| Class 4 | 1 | 100% | 100% | 0% | 100% | 1.0 | 2.7 |

- **Nursery**: No reading material for Nursery, LKG and UKG (1); Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass (1); Before a session starts, all guidance is written English; non-readers get no spoken instructions (1)
- **LKG**: No reading material for Nursery, LKG and UKG (1); Before a session starts, all guidance is written English; non-readers get no spoken instructions (1); Stall prompt fires during normal thinking pauses of slow and hesitant readers (1)
- **UKG**: No reading material for Nursery, LKG and UKG (1); Before a session starts, all guidance is written English; non-readers get no spoken instructions (1); Stall prompt fires during normal thinking pauses of slow and hesitant readers (1)
- **Class 2**: Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass (1); Tapping the big microphone during a session pauses it (1); What a child says while Buddy is talking is silently discarded (1)
- **Class 4**: Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass (1); Stall prompt fires during normal thinking pauses of slow and hesitant readers (1); What a child says while Buddy is talking is silently discarded (1)

## Language-wise findings

| Language | n | Started | Finished | Covered | False corr./agent | Missed errors/agent | Wrong language |
|---|---|---|---|---|---|---|---|
| English | 2 | 50% | 0% | 22% | 0.0 | 1.0 | 50% |
| Gujarati | 1 | 100% | 0% | 31% | 0.0 | 0.0 | 0% |
| Hindi | 2 | 100% | 50% | 56% | 0.0 | 0.5 | 0% |

- **English**: Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass (2); No reading material for Nursery, LKG and UKG (1); Before a session starts, all guidance is written English; non-readers get no spoken instructions (1)
- **Hindi**: Stall prompt fires during normal thinking pauses of slow and hesitant readers (2); Buddy's opening talk is long before the child gets a turn (2); No reading material for Nursery, LKG and UKG (1)
- **Gujarati**: No reading material for Nursery, LKG and UKG (1); Before a session starts, all guidance is written English; non-readers get no spoken instructions (1); Stall prompt fires during normal thinking pauses of slow and hesitant readers (1)

## What children liked

- “I liked it when Buddy said well done.” (2)
- “I finished the whole poem!” (1)

## Speech and audio evaluation (measured, separate from simulated satisfaction)

No audio evaluation report found for this cycle (run `python -m agent_org.audio_eval`).

## Method and limits

- Children are deterministic persona policies (seeded), not LLMs; they perceive only the screen and Buddy's voice.
- Speech is simulated: reading errors come from the persona; recognition errors from a coarse per-language model (measured adult-TTS WER + an assumed child-voice penalty). Findings that depend on real child speech are marked for the audio evaluation.
- Uncached Buddy lines play as timed placeholder audio (no Timbre calls); timing is realistic, sound is not.
- Evidence for every claim: `agent_org/runs/pilot/p1/<agent>/` (report, trace, screenshots, server log).
