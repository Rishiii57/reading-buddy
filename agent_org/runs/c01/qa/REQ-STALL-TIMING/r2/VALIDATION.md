# QA validation: REQ-STALL-TIMING (round 2)

**Verdict: validated_fixed** · candidate `69518f37` vs base `0706bcae` · 10 personas × 2 seeds (20 sessions per build) · 1629.4 s

Personas: C1-01, C1-02, C1-03, C1-06, C2-02, C2-03, C2-04, C2-06, C3-02, C3-03

Original issue reproduced on base build: ✅

## Acceptance criteria (from the PM requirement)

| Metric | Target | Scope | Before | After | Check | Pass |
|---|---|---|---|---|---|---|
| stall_interruptions_per_agent | <= x0.5 | affected personas | 0.55 | 0.25 | 0.25 <= 0.5×0.55 = 0.275 | ✅ |
| stuck_rate | <= baseline | no new stuck children | 0.0 | 0.0 | 0.0 ≤ baseline 0.0 | ✅ |

## Regression guards (same personas)

| Metric | Before | After | Rule | Pass |
|---|---|---|---|---|
| completion_rate | 0.35 | 0.45 | >= before-0.1 | ✅ |
| abandon_rate | 0.5 | 0.45 | <= before+0.1 | ✅ |
| false_corrections_per_agent | 0.4 | 0.6 | <= before+0.25 | ✅ |
| frustration_peak_mean | 3.348 | 2.768 | <= before+0.3 | ✅ |
| harness_error_rate | 0.0 | 0.0 | <= before+0.0 | ✅ |

## Offline tutor replay (recorded Prisma transcripts, base vs candidate)

| Check | Before | After | Pass |
|---|---|---|---|
| tracking_pass | 23/24 | 23/24 | ✅ |
| errors_caught | 23/24 | 23/24 | ✅ |
| stalls_prompted | 11/12 | 11/12 | ✅ |
| false_corrections_per_50_words | 0.104 | 0.104 | ✅ |
| stall_prompt_s_max (<= 4.0) | 2.46 | 3.91 | ✅ |

Unit tests on candidate: ✅ 45 passed in 0.35s

## All metrics

| Metric | Before | After |
|---|---|---|
| session_start_rate | 0.95 | 0.95 |
| completion_rate | 0.35 | 0.45 |
| abandon_rate | 0.5 | 0.45 |
| coverage | 0.615 | 0.718 |
| stall_interruptions_per_agent | 0.55 | 0.25 |
| correction_interruptions_per_agent | 0.35 | 0.05 |
| interruptions_per_agent | 1.2 | 0.6 |
| mic_tap_pause_rate | 0.45 | 0.55 |
| unheard_words_per_agent | 7.55 | 7.1 |
| drill_repeat_rate | 0.15 | 0.3 |
| spoken_guidance_gap_rate | 0.5 | 0.5 |
| consent_blocked_rate | 0.0 | 0.0 |
| consent_self_approved_rate | 0.1 | 0.1 |
| level_mismatch_rate | 0.0 | 0.0 |
| false_corrections_per_agent | 0.4 | 0.6 |
| missed_errors_per_agent | 0.6 | 0.55 |
| long_talk_rate | 0.85 | 0.75 |
| intro_s_median | 13.9 | 14.5 |
| frustration_peak_mean | 3.348 | 2.768 |
| stuck_rate | 0.0 | 0.0 |
| break_ignored_rate | 0.0 | 0.0 |
| wrong_language_rate | 0.15 | 0.15 |
| replay_missing_rate | 0.0 | 0.0 |
| restart_failed_rate | 0.0 | 0.0 |
| harness_error_rate | 0.0 | 0.0 |

Evidence: `agent_org/runs/c01/qa/REQ-STALL-TIMING/r2/before-s*/` and `after-s*/` (per-agent reports, traces, server logs).
