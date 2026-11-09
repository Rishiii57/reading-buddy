# QA validation: REQ-PREPRIMARY-CONTENT (round 1)

**Verdict: returned_to_engineering** · candidate `54811fcf` vs base `951b5bce` · 10 personas × 2 seeds (20 sessions per build) · 506.3 s

Personas: L01, L02, L03, L04, L05, L06, L07, L08, N01, N02

Original issue reproduced on base build: ✅

## Acceptance criteria (from the PM requirement)

| Metric | Target | Scope | Before | After | Check | Pass |
|---|---|---|---|---|---|---|
| level_mismatch_rate | <= 0.0 | pre-primary personas | 1.0 | 0.4 | 0.4 <= 0.0 | ❌ |
| coverage | >= 0.6 | pre-primary personas | 0.094 | 0.137 | 0.137 >= 0.6 | ❌ |
| stuck_rate | <= 0.1 | pre-primary personas | 0.0 | 0.0 | 0.0 <= 0.1 | ✅ |

## Regression guards (same personas)

| Metric | Before | After | Rule | Pass |
|---|---|---|---|---|
| completion_rate | 0.0 | 0.0 | >= before-0.1 | ✅ |
| abandon_rate | 0.95 | 0.9 | <= before+0.1 | ✅ |
| false_corrections_per_agent | 0.0 | 0.05 | <= before+0.25 | ✅ |
| frustration_peak_mean | 2.938 | 2.79 | <= before+0.3 | ✅ |
| harness_error_rate | 0.0 | 0.0 | <= before+0.0 | ✅ |

## Offline tutor replay (recorded Prisma transcripts, base vs candidate)

| Check | Before | After | Pass |
|---|---|---|---|
| tracking_pass | 23/24 | 23/24 | ✅ |
| errors_caught | 23/24 | 23/24 | ✅ |
| stalls_prompted | 11/12 | 11/12 | ✅ |
| false_corrections_per_50_words | 0.104 | 0.104 | ✅ |
| stall_prompt_s_max (<= 4.0) | 2.46 | 2.46 | ✅ |

Unit tests on candidate: ✅ 58 passed in 0.38s

## All metrics

| Metric | Before | After |
|---|---|---|
| session_start_rate | 0.65 | 0.65 |
| completion_rate | 0.0 | 0.0 |
| abandon_rate | 0.95 | 0.9 |
| coverage | 0.094 | 0.137 |
| stall_interruptions_per_agent | 0.65 | 0.75 |
| correction_interruptions_per_agent | 0.5 | 0.15 |
| interruptions_per_agent | 1.3 | 1.05 |
| mic_tap_pause_rate | 0.3 | 0.45 |
| unheard_words_per_agent | 0.5 | 0.5 |
| drill_repeat_rate | 0.05 | 0.0 |
| spoken_guidance_gap_rate | 1.0 | 1.0 |
| consent_blocked_rate | 0.15 | 0.15 |
| consent_self_approved_rate | 0.0 | 0.0 |
| level_mismatch_rate | 1.0 | 0.4 |
| false_corrections_per_agent | 0.0 | 0.05 |
| missed_errors_per_agent | 0.05 | 0.0 |
| long_talk_rate | 0.35 | 0.55 |
| intro_s_median | 13.2 | 13.4 |
| frustration_peak_mean | 2.938 | 2.79 |
| stuck_rate | 0.0 | 0.0 |
| break_ignored_rate | 0.0 | 0.0 |
| wrong_language_rate | 0.25 | 0.25 |
| replay_missing_rate | 0.1 | 0.1 |
| restart_failed_rate | 0.0 | 0.05 |
| harness_error_rate | 0.0 | 0.0 |

Evidence: `agent_org/runs/c01/qa/REQ-PREPRIMARY-CONTENT/r1/before-s*/` and `after-s*/` (per-agent reports, traces, server logs).
