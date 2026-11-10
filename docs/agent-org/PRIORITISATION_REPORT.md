# Prioritisation report: cycle c02 / retest

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
| P1 | REQ-PREPRIMARY-CONTENT | No reading material for Nursery, LKG and UKG | 4 | 5 (10%) | 19% | 1.42 | 2 | 3 | 3 | 60% | L | 19.73 |
| P1 | REQ-STALL-TIMING | Stall prompt fires during normal thinking pauses of slow and | 3 | 11 (22%) | 38% | 1.38 | 3 | 3 | 3 | 55% | S | 19.21 |
| P2 | REQ-NAVIGATION | Children cannot find a text or leave the reading page by acc | 3 | 18 (36%) | 62% | 1.37 | 3 | 2 | 3 | 33% | M | 18.0 |
| P2 | REQ-FALSE-CORRECTION-TUTOR | Correctly read words flagged for practice (tutor/aligner) | 3 | 5 (10%) | 4% | 1.06 | 3 | 3 | 3 | 80% | M | 17.34 |
| P2 | REQ-MIDLINE-CORRECTION | A slip followed by a thinking pause triggers word practice m | 3 | 3 (6%) | 4% | 1.1 | 2 | 3 | 2 | 100% | S | 17.2 |
| P2 | REQ-DRILL-LOOP | Word practice and line repetition loop on the same word or l | 3 | 5 (10%) | 4% | 1.08 | 3 | 2 | 3 | 80% | S | 16.55 |
| P2 | REQ-FALSE-CORRECTION-STT | Correct reading misheard by the speech model (child voices) | 3 | 2 (4%) | 0% | 1.0 | 2 | 3 | 3 | 0% | L | 14.64 |
| P2 | REQ-SPOKEN-ONBOARDING | Before a session starts, all guidance is written English; no | 3 | 1 (2%) | 4% | 1.5 | 1 | 2 | 3 | 0% | S | 14.54 |
| P2 | REQ-LONG-INTRO | Buddy's opening talk is long before the child gets a turn | 2 | 33 (66%) | 62% | 1.21 | 3 | 1 | 2 | 30% | S | 14.18 |
| P2 | REQ-TALK-OVER-BUDDY | What a child says while Buddy is talking is silently discard | 2 | 26 (52%) | 50% | 1.22 | 3 | 2 | 2 | 38% | M | 14.16 |
| P3 | REQ-LANGUAGE-SELECTION | Children end up in, or hear, a language they did not choose | 2 | 12 (24%) | 35% | 1.38 | 3 | 2 | 2 | 50% | S | 13.6 |
| P3 | REQ-RESTART | Reading the same text again does not work smoothly | 3 | 1 (2%) | 4% | 1.4 | 1 | 2 | 2 | 0% | S | 13.52 |
| P3 | REQ-REPLAY | No way to hear a line again during reading | 2 | 4 (8%) | 12% | 1.3 | 2 | 2 | 2 | 0% | S | 11.03 |
| P3 | REQ-LENIENT-MATCHING | Some misreadings are accepted as correct (vowel length, matr | 2 | 14 (28%) | 19% | 1.14 | 3 | 2 | 1 | 21% | M | 10.95 |

## Decisions this cycle

awaiting_human_approval: 3, validated_fixed: 2, deferred: 9

- REQ-PREPRIMARY-CONTENT **awaiting_human_approval**: Touches content, privacy or model/data collection: needs a human decision. (was accepted_by_human)
- REQ-STALL-TIMING **validated_fixed**: Validated fix holds: residual cases only (11 children, was 20). Kept under watch. (was validated_fixed)
- REQ-NAVIGATION **deferred**: P2: below the approval line this cycle. (was deferred)
- REQ-FALSE-CORRECTION-TUTOR **deferred**: P2: below the approval line this cycle. (was deferred)
- REQ-MIDLINE-CORRECTION **deferred**: P2: below the approval line this cycle. (was deferred)
- REQ-DRILL-LOOP **deferred**: P2: below the approval line this cycle. (was deferred)
- REQ-FALSE-CORRECTION-STT **awaiting_human_approval**: Touches content, privacy or model/data collection: needs a human decision. (was awaiting_human_approval)
- REQ-SPOKEN-ONBOARDING **validated_fixed**: Validated fix holds: residual cases only (1 children, was 35). Kept under watch. (was validated_fixed)
- REQ-LONG-INTRO **deferred**: P2: below the approval line this cycle. (was deferred)
- REQ-TALK-OVER-BUDDY **deferred**: P2: below the approval line this cycle. (was deferred)
- REQ-LANGUAGE-SELECTION **deferred**: P3: below the approval line this cycle. (was deferred)
- REQ-RESTART **deferred**: P3: below the approval line this cycle.
- REQ-REPLAY **deferred**: P3: below the approval line this cycle. (was deferred)
- REQ-LENIENT-MATCHING **awaiting_human_approval**: Touches content, privacy or model/data collection: needs a human decision. (was awaiting_human_approval)
