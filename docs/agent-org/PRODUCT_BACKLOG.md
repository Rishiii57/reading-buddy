# Product backlog

Maintained by the AI Product Manager across cycles. Status flow: deferred / awaiting_human_approval / approved → in_progress → awaiting_qa → validated_fixed (or returned_to_engineering). A validated item that reappears becomes *regressed*.

| Req | Problem | P | Status | First seen | Recent history (run:children) |
|---|---|---|---|---|---|
| REQ-PREPRIMARY-CONTENT | No reading material for Nursery, LKG and UKG | P0 | awaiting_human_approval | c01/baseline | baseline:26 |
| REQ-CONSENT-GATE | Parent-consent box is a dead end for pre-readers and a tick-box any re | P0 | awaiting_human_approval | c01/baseline | baseline:9 |
| REQ-SPOKEN-ONBOARDING | Before a session starts, all guidance is written English; non-readers  | P1 | approved | c01/baseline | baseline:35 |
| REQ-STALL-TIMING | Stall prompt fires during normal thinking pauses of slow and hesitant  | P1 | approved | c01/baseline | baseline:20 |
| REQ-MIDLINE-CORRECTION | A slip followed by a thinking pause triggers word practice mid-line | P2 | deferred | c01/baseline | baseline:13 |
| REQ-MIC-TOGGLE | Tapping the big microphone during a session pauses it | P2 | deferred | c01/baseline | baseline:19 |
| REQ-TALK-OVER-BUDDY | What a child says while Buddy is talking is silently discarded | P2 | deferred | c01/baseline | baseline:26 |
| REQ-LONG-INTRO | Buddy's opening talk is long before the child gets a turn | P2 | deferred | c01/baseline | baseline:35 |
| REQ-DRILL-LOOP | Word practice and line repetition loop on the same word or line | P2 | deferred | c01/baseline | baseline:3 |
| REQ-FALSE-CORRECTION-TUTOR | Correctly read words flagged for practice (tutor/aligner) | P2 | deferred | c01/baseline | baseline:4 |
| REQ-FALSE-CORRECTION-STT | Correct reading misheard by the speech model (child voices) | P2 | awaiting_human_approval | c01/baseline | baseline:4 |
| REQ-LANGUAGE-SELECTION | Children end up in, or hear, a language they did not choose | P2 | deferred | c01/baseline | baseline:12 |
| REQ-NAVIGATION | Children cannot find a text or leave the reading page by accident | P2 | deferred | c01/baseline | baseline:12 |
| REQ-LENIENT-MATCHING | Some misreadings are accepted as correct (vowel length, matras, word e | P3 | awaiting_human_approval | c01/baseline | baseline:10 |
| REQ-REPLAY | No way to hear a line again during reading | P3 | deferred | c01/baseline | baseline:4 |

## Unresolved problems

- REQ-PREPRIMARY-CONTENT No reading material for Nursery, LKG and UKG (awaiting_human_approval)
- REQ-CONSENT-GATE Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass (awaiting_human_approval)
- REQ-SPOKEN-ONBOARDING Before a session starts, all guidance is written English; non-readers get no spoken instructions (approved)
- REQ-STALL-TIMING Stall prompt fires during normal thinking pauses of slow and hesitant readers (approved)
- REQ-MIDLINE-CORRECTION A slip followed by a thinking pause triggers word practice mid-line (deferred)
- REQ-MIC-TOGGLE Tapping the big microphone during a session pauses it (deferred)
- REQ-TALK-OVER-BUDDY What a child says while Buddy is talking is silently discarded (deferred)
- REQ-LONG-INTRO Buddy's opening talk is long before the child gets a turn (deferred)
- REQ-DRILL-LOOP Word practice and line repetition loop on the same word or line (deferred)
- REQ-FALSE-CORRECTION-TUTOR Correctly read words flagged for practice (tutor/aligner) (deferred)
- REQ-FALSE-CORRECTION-STT Correct reading misheard by the speech model (child voices) (awaiting_human_approval)
- REQ-LANGUAGE-SELECTION Children end up in, or hear, a language they did not choose (deferred)
- REQ-NAVIGATION Children cannot find a text or leave the reading page by accident (deferred)
- REQ-LENIENT-MATCHING Some misreadings are accepted as correct (vowel length, matras, word endings, small words) (awaiting_human_approval)
- REQ-REPLAY No way to hear a line again during reading (deferred)

## Cycles

- c01/baseline at 2026-11-09T18:37:11: 50 children, 15 root causes, 3 unclassified
