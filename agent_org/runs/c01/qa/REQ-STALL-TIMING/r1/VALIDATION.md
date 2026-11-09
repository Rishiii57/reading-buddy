# QA validation: REQ-STALL-TIMING (round 1)

**Verdict: returned_to_engineering** · candidate `1182cee3` vs base `0706bcae` · 14 personas × 2 seeds (28 sessions per build) · 2053.4 s

Personas: C1-01, C1-02, C1-03, C1-06, C2-02, C2-03, C2-04, C2-06, C3-02, C3-03, C3-04, C3-06, L01, L05

Original issue reproduced on base build: ✅

## Acceptance criteria (from the PM requirement)

| Metric | Target | Scope | Before | After | Check | Pass |
|---|---|---|---|---|---|---|
| stall_interruptions_per_agent | <= x0.5 | affected personas | 0.714 | 0.536 | 0.536 <= 0.5×0.714 = 0.357 | ❌ |
| stuck_rate | <= baseline | no new stuck children | 0.0 | 0.0 | 0.0 ≤ baseline 0.0 | ✅ |

## Regression guards (same personas)

| Metric | Before | After | Rule | Pass |
|---|---|---|---|---|
| completion_rate | 0.25 | 0.25 | >= before-0.1 | ✅ |
| abandon_rate | 0.571 | 0.536 | <= before+0.1 | ✅ |
| false_corrections_per_agent | 0.5 | 0.429 | <= before+0.25 | ✅ |
| frustration_peak_mean | 3.746 | 3.141 | <= before+0.3 | ✅ |
| harness_error_rate | 0.0 | 0.0 | <= before+0.0 | ✅ |

## Offline tutor replay (recorded Prisma transcripts, base vs candidate)

| Check | Before | After | Pass |
|---|---|---|---|
| tracking_pass | 23/24 | 23/24 | ✅ |
| errors_caught | 23/24 | 23/24 | ✅ |
| stalls_prompted | 11/12 | 11/12 | ✅ |
| false_corrections_per_50_words | 0.104 | 0.104 | ✅ |
| stall_prompt_s_max (<= 4.0) | 2.46 | 3.46 | ✅ |

Unit tests on candidate: ✅ 45 passed in 0.31s

## All metrics

| Metric | Before | After |
|---|---|---|
| session_start_rate | 0.964 | 0.964 |
| completion_rate | 0.25 | 0.25 |
| abandon_rate | 0.571 | 0.536 |
| coverage | 0.541 | 0.562 |
| stall_interruptions_per_agent | 0.714 | 0.536 |
| correction_interruptions_per_agent | 0.536 | 0.286 |
| interruptions_per_agent | 1.429 | 1.143 |
| mic_tap_pause_rate | 0.571 | 0.607 |
| unheard_words_per_agent | 4.893 | 5.357 |
| drill_repeat_rate | 0.214 | 0.357 |
| spoken_guidance_gap_rate | 0.5 | 0.5 |
| consent_blocked_rate | 0.0 | 0.0 |
| consent_self_approved_rate | 0.143 | 0.143 |
| level_mismatch_rate | 0.143 | 0.143 |
| false_corrections_per_agent | 0.5 | 0.429 |
| missed_errors_per_agent | 0.214 | 0.429 |
| long_talk_rate | 0.786 | 0.75 |
| intro_s_median | 14.6 | 14.0 |
| frustration_peak_mean | 3.746 | 3.141 |
| stuck_rate | 0.0 | 0.0 |
| break_ignored_rate | 0.0 | 0.0 |
| wrong_language_rate | 0.107 | 0.107 |
| replay_missing_rate | 0.0 | 0.0 |
| restart_failed_rate | 0.0 | 0.0 |
| harness_error_rate | 0.0 | 0.0 |

Evidence: `agent_org/runs/c01/qa/REQ-STALL-TIMING/r1/before-s*/` and `after-s*/` (per-agent reports, traces, server logs).
