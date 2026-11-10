# Prioritisation report: cycle c01 / baseline

## Method

score = 3·severity + 6·reach·grade_weight + 3·max(0, pre-primary reach − reach) + 1.5·learning impact + UX impact + 2·abandonment among affected − 0.7·complexity cost (S 1, M 2, L 3).

- **P0**: severity 4 (blocks reading or privacy risk) and reach ≥ 15 % overall or ≥ 30 % of pre-primary children.
- **P1**: score ≥ 19, or any severity-4 problem regardless of how many children hit it (small groups are not dropped).
- **P2**: score ≥ 14. **P3**: the rest.
- Grade weights (Nursery 1.5, LKG 1.4, UKG 1.3, Class 1 1.1, others 1.0) make a problem that hits the youngest count more.
- Approval: P0/P1 in order of score until engineering capacity is used; items touching content, privacy, or data collection always need human approval.

## Scores

| P | Req | Problem | Sev | Children | Pre-primary | Grade wt | Langs | Learning | UX | Abandon (affected) | Cplx | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P0 | REQ-PREPRIMARY-CONTENT | No reading material for Nursery, LKG and UKG | 4 | 26 (52%) | 100% | 1.41 | 3 | 3 | 3 | 85% | L | 24.92 |
| P0 | REQ-CONSENT-GATE | Parent-consent box is a dead end for pre-readers and a tick- | 4 | 9 (18%) | 15% | 1.2 | 3 | 2 | 3 | 78% | M | 19.45 |
| P1 | REQ-SPOKEN-ONBOARDING | Before a session starts, all guidance is written English; no | 3 | 35 (70%) | 96% | 1.3 | 3 | 2 | 3 | 74% | S | 22.04 |
| P1 | REQ-STALL-TIMING | Stall prompt fires during normal thinking pauses of slow and | 3 | 20 (40%) | 31% | 1.18 | 3 | 3 | 3 | 70% | S | 20.03 |
| P2 | REQ-MIC-TOGGLE | Tapping the big microphone during a session pauses it | 3 | 19 (38%) | 42% | 1.23 | 3 | 2 | 3 | 79% | S | 18.82 |
| P2 | REQ-MIDLINE-CORRECTION | A slip followed by a thinking pause triggers word practice m | 3 | 13 (26%) | 31% | 1.28 | 3 | 3 | 2 | 77% | S | 18.49 |
| P2 | REQ-FALSE-CORRECTION-TUTOR | Correctly read words flagged for practice (tutor/aligner) | 3 | 4 (8%) | 8% | 1.2 | 2 | 3 | 3 | 75% | M | 17.18 |
| P2 | REQ-NAVIGATION | Children cannot find a text or leave the reading page by acc | 3 | 12 (24%) | 35% | 1.31 | 3 | 2 | 3 | 50% | M | 16.8 |
| P2 | REQ-DRILL-LOOP | Word practice and line repetition loop on the same word or l | 3 | 3 (6%) | 0% | 1.07 | 2 | 2 | 3 | 100% | S | 16.68 |
| P2 | REQ-FALSE-CORRECTION-STT | Correct reading misheard by the speech model (child voices) | 3 | 4 (8%) | 4% | 1.1 | 2 | 3 | 3 | 50% | L | 15.93 |
| P2 | REQ-LONG-INTRO | Buddy's opening talk is long before the child gets a turn | 2 | 35 (70%) | 62% | 1.2 | 3 | 1 | 2 | 60% | S | 15.03 |
| P2 | REQ-LANGUAGE-SELECTION | Children end up in, or hear, a language they did not choose | 2 | 12 (24%) | 35% | 1.38 | 3 | 2 | 2 | 100% | S | 14.6 |
| P2 | REQ-TALK-OVER-BUDDY | What a child says while Buddy is talking is silently discard | 2 | 26 (52%) | 38% | 1.17 | 3 | 2 | 2 | 65% | M | 14.56 |
| P3 | REQ-REPLAY | No way to hear a line again during reading | 2 | 4 (8%) | 12% | 1.3 | 2 | 2 | 2 | 75% | S | 12.53 |
| P3 | REQ-LENIENT-MATCHING | Some misreadings are accepted as correct (vowel length, matr | 2 | 10 (20%) | 8% | 1.09 | 3 | 2 | 1 | 50% | M | 10.91 |

## Decisions this cycle

awaiting_human_approval: 4, approved: 2, deferred: 9

- REQ-PREPRIMARY-CONTENT **awaiting_human_approval**: Touches content, privacy or model/data collection: needs a human decision.
- REQ-CONSENT-GATE **awaiting_human_approval**: Touches content, privacy or model/data collection: needs a human decision.
- REQ-SPOKEN-ONBOARDING **approved**: P1 within capacity (1/8 units).
- REQ-STALL-TIMING **approved**: P1 within capacity (2/8 units).
- REQ-MIC-TOGGLE **deferred**: P2: below the approval line this cycle.
- REQ-MIDLINE-CORRECTION **deferred**: P2: below the approval line this cycle.
- REQ-FALSE-CORRECTION-TUTOR **deferred**: P2: below the approval line this cycle.
- REQ-NAVIGATION **deferred**: P2: below the approval line this cycle.
- REQ-DRILL-LOOP **deferred**: P2: below the approval line this cycle.
- REQ-FALSE-CORRECTION-STT **awaiting_human_approval**: Touches content, privacy or model/data collection: needs a human decision.
- REQ-LONG-INTRO **deferred**: P2: below the approval line this cycle.
- REQ-LANGUAGE-SELECTION **deferred**: P2: below the approval line this cycle.
- REQ-TALK-OVER-BUDDY **deferred**: P2: below the approval line this cycle.
- REQ-REPLAY **deferred**: P3: below the approval line this cycle.
- REQ-LENIENT-MATCHING **awaiting_human_approval**: Touches content, privacy or model/data collection: needs a human decision.
