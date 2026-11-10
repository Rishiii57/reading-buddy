# Product backlog

Maintained by the AI Product Manager across cycles. Status flow: deferred / awaiting_human_approval / approved → in_progress → awaiting_qa → validated_fixed (or returned_to_engineering). A validated item that reappears becomes *regressed*.

| Req | Problem | P | Status | First seen | Recent history (run:children) |
|---|---|---|---|---|---|
| REQ-CONSENT-GATE | Parent-consent box is a dead end for pre-readers and a tick-box any re | P0 | accepted_by_human | c01/baseline | in_progress:- → awaiting_qa:- → returned_to_engineering:- → human_accepted_by_human:- |
| REQ-PREPRIMARY-CONTENT | No reading material for Nursery, LKG and UKG | P1 | awaiting_human_approval | c01/baseline | awaiting_qa:- → returned_to_engineering:- → human_accepted_by_human:- → retest:5 |
| REQ-MIDLINE-CORRECTION | A slip followed by a thinking pause triggers word practice mid-line | P2 | deferred | c01/baseline | baseline:13 → retest:3 |
| REQ-TALK-OVER-BUDDY | What a child says while Buddy is talking is silently discarded | P2 | deferred | c01/baseline | baseline:26 → retest:26 |
| REQ-LONG-INTRO | Buddy's opening talk is long before the child gets a turn | P2 | deferred | c01/baseline | baseline:35 → retest:33 |
| REQ-DRILL-LOOP | Word practice and line repetition loop on the same word or line | P2 | deferred | c01/baseline | baseline:3 → retest:5 |
| REQ-FALSE-CORRECTION-TUTOR | Correctly read words flagged for practice (tutor/aligner) | P2 | deferred | c01/baseline | baseline:4 → retest:5 |
| REQ-FALSE-CORRECTION-STT | Correct reading misheard by the speech model (child voices) | P2 | awaiting_human_approval | c01/baseline | baseline:4 → retest:2 |
| REQ-NAVIGATION | Children cannot find a text or leave the reading page by accident | P2 | deferred | c01/baseline | baseline:12 → retest:18 |
| REQ-LENIENT-MATCHING | Some misreadings are accepted as correct (vowel length, matras, word e | P3 | awaiting_human_approval | c01/baseline | baseline:10 → retest:14 |
| REQ-LANGUAGE-SELECTION | Children end up in, or hear, a language they did not choose | P3 | deferred | c01/baseline | baseline:12 → retest:12 |
| REQ-REPLAY | No way to hear a line again during reading | P3 | deferred | c01/baseline | baseline:4 → retest:4 |
| REQ-RESTART | Reading the same text again does not work smoothly | P3 | deferred | c02/retest | retest:1 |
| REQ-STALL-TIMING | Stall prompt fires during normal thinking pauses of slow and hesitant  | P1 | validated_fixed | c01/baseline | returned_to_engineering:- → awaiting_qa:- → validated_fixed:- → retest:11 |
| REQ-SPOKEN-ONBOARDING | Before a session starts, all guidance is written English; non-readers  | P2 | validated_fixed | c01/baseline | in_progress:- → awaiting_qa:- → validated_fixed:- → retest:1 |
| REQ-MIC-TOGGLE | Tapping the big microphone during a session pauses it | P2 | validated_fixed | c01/baseline | in_progress:- → awaiting_qa:- → awaiting_qa:- → validated_fixed:- |

## Unresolved problems

- REQ-CONSENT-GATE Parent-consent box is a dead end for pre-readers and a tick-box any reader can pass (accepted_by_human)
- REQ-PREPRIMARY-CONTENT No reading material for Nursery, LKG and UKG (awaiting_human_approval)
- REQ-MIDLINE-CORRECTION A slip followed by a thinking pause triggers word practice mid-line (deferred)
- REQ-TALK-OVER-BUDDY What a child says while Buddy is talking is silently discarded (deferred)
- REQ-LONG-INTRO Buddy's opening talk is long before the child gets a turn (deferred)
- REQ-DRILL-LOOP Word practice and line repetition loop on the same word or line (deferred)
- REQ-FALSE-CORRECTION-TUTOR Correctly read words flagged for practice (tutor/aligner) (deferred)
- REQ-FALSE-CORRECTION-STT Correct reading misheard by the speech model (child voices) (awaiting_human_approval)
- REQ-NAVIGATION Children cannot find a text or leave the reading page by accident (deferred)
- REQ-LENIENT-MATCHING Some misreadings are accepted as correct (vowel length, matras, word endings, small words) (awaiting_human_approval)
- REQ-LANGUAGE-SELECTION Children end up in, or hear, a language they did not choose (deferred)
- REQ-REPLAY No way to hear a line again during reading (deferred)
- REQ-RESTART Reading the same text again does not work smoothly (deferred)

## Cycles

- c01/baseline at 2026-11-09T18:37:11: 50 children, 15 root causes, 3 unclassified
- c02/retest at 2026-11-10T11:37:02: 50 children, 14 root causes, 4 unclassified
