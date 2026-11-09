# Prioritisation report: cycle pilot / p1

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
| P0 | REQ-PREPRIMARY-CONTENT | No reading material for Nursery, LKG and UKG | 4 | 3 (60%) | 100% | 1.4 | 3 | 3 | 3 | 100% | L | 25.64 |
| P0 | REQ-CONSENT-GATE | Parent-consent box is a dead end for pre-readers and a tick- | 4 | 3 (60%) | 33% | 1.17 | 2 | 2 | 3 | 67% | M | 22.13 |
| P1 | REQ-SPOKEN-ONBOARDING | Before a session starts, all guidance is written English; no | 3 | 3 (60%) | 100% | 1.4 | 3 | 2 | 3 | 100% | S | 22.54 |
| P1 | REQ-STALL-TIMING | Stall prompt fires during normal thinking pauses of slow and | 3 | 3 (60%) | 67% | 1.23 | 2 | 3 | 3 | 67% | S | 21.77 |
| P1 | REQ-MIC-TOGGLE | Tapping the big microphone during a session pauses it | 3 | 3 (60%) | 67% | 1.23 | 3 | 2 | 3 | 100% | S | 20.94 |
| P2 | REQ-DRILL-LOOP | Word practice and line repetition loop on the same word or l | 3 | 1 (20%) | 0% | 1.0 | 1 | 2 | 3 | 100% | S | 17.5 |
| P2 | REQ-LONG-INTRO | Buddy's opening talk is long before the child gets a turn | 2 | 4 (80%) | 67% | 1.18 | 3 | 1 | 2 | 75% | S | 15.94 |
| P2 | REQ-TALK-OVER-BUDDY | What a child says while Buddy is talking is silently discard | 2 | 3 (60%) | 33% | 1.1 | 3 | 2 | 2 | 67% | M | 14.89 |
| P2 | REQ-LANGUAGE-SELECTION | Children end up in, or hear, a language they did not choose | 2 | 1 (20%) | 33% | 1.5 | 1 | 2 | 2 | 100% | S | 14.5 |
| P3 | REQ-LENIENT-MATCHING | Some misreadings are accepted as correct (vowel length, matr | 2 | 2 (40%) | 0% | 1.0 | 2 | 2 | 1 | 50% | M | 12.0 |

## Decisions this cycle

awaiting_human_approval: 3, approved: 3, deferred: 4

- REQ-PREPRIMARY-CONTENT **awaiting_human_approval**: Touches content, privacy or model/data collection: needs a human decision.
- REQ-CONSENT-GATE **awaiting_human_approval**: Touches content, privacy or model/data collection: needs a human decision.
- REQ-SPOKEN-ONBOARDING **approved**: P1 within capacity (1/8 units).
- REQ-STALL-TIMING **approved**: P1 within capacity (2/8 units).
- REQ-MIC-TOGGLE **approved**: P1 within capacity (3/8 units).
- REQ-DRILL-LOOP **deferred**: P2: below the approval line this cycle.
- REQ-LONG-INTRO **deferred**: P2: below the approval line this cycle.
- REQ-TALK-OVER-BUDDY **deferred**: P2: below the approval line this cycle.
- REQ-LANGUAGE-SELECTION **deferred**: P2: below the approval line this cycle.
- REQ-LENIENT-MATCHING **awaiting_human_approval**: Touches content, privacy or model/data collection: needs a human decision.
