# QA validation: REQ-PREPRIMARY-CONTENT (round 2)

**Verdict: returned_to_engineering** · candidate `2249bb97` vs base `ef4a0bee` · 10 personas × 2 seeds (20 sessions per build) · 914.6 s

Personas: L01, L02, L03, L04, L05, L06, L07, L08, N01, N02

Original issue reproduced on base build: ✅

## Acceptance criteria (from the PM requirement)

| Metric | Target | Scope | Before | After | Check | Pass |
|---|---|---|---|---|---|---|
| level_mismatch_rate | <= 0.0 | pre-primary personas | 1.0 | 0.2 | 0.2 <= 0.0 | ❌ |
| coverage | >= 0.6 | pre-primary personas | 0.19 | 0.219 | 0.219 >= 0.6 | ❌ |
| stuck_rate | <= 0.1 | pre-primary personas | 0.0 | 0.0 | 0.0 <= 0.1 | ✅ |

## Regression guards (same personas)

| Metric | Before | After | Rule | Pass |
|---|---|---|---|---|
| completion_rate | 0.0 | 0.0 | >= before-0.1 | ✅ |
| abandon_rate | 0.95 | 0.95 | <= before+0.1 | ✅ |
| false_corrections_per_agent | 0.05 | 0.0 | <= before+0.25 | ✅ |
| frustration_peak_mean | 2.792 | 2.708 | <= before+0.3 | ✅ |
| harness_error_rate | 0.0 | 0.0 | <= before+0.0 | ✅ |

## Offline tutor replay (recorded Prisma transcripts, base vs candidate)

| Check | Before | After | Pass |
|---|---|---|---|
| tracking_pass | 23/24 | 23/24 | ✅ |
| errors_caught | 23/24 | 23/24 | ✅ |
| stalls_prompted | 11/12 | 11/12 | ✅ |
| false_corrections_per_50_words | 0.104 | 0.104 | ✅ |
| stall_prompt_s_max (<= 4.0) | 3.91 | 3.91 | ✅ |

Unit tests on candidate: ✅ 63 passed in 0.85s

## All metrics

| Metric | Before | After |
|---|---|---|
| session_start_rate | 0.7 | 0.65 |
| completion_rate | 0.0 | 0.0 |
| abandon_rate | 0.95 | 0.95 |
| coverage | 0.19 | 0.219 |
| stall_interruptions_per_agent | 0.8 | 0.75 |
| correction_interruptions_per_agent | 0.25 | 0.5 |
| interruptions_per_agent | 1.3 | 1.45 |
| mic_tap_pause_rate | 0.0 | 0.0 |
| unheard_words_per_agent | 0.8 | 0.85 |
| drill_repeat_rate | 0.25 | 0.15 |
| spoken_guidance_gap_rate | 0.0 | 0.0 |
| consent_blocked_rate | 0.15 | 0.2 |
| consent_self_approved_rate | 0.0 | 0.0 |
| level_mismatch_rate | 1.0 | 0.2 |
| false_corrections_per_agent | 0.05 | 0.0 |
| missed_errors_per_agent | 0.35 | 0.3 |
| long_talk_rate | 0.4 | 0.25 |
| intro_s_median | 13.2 | 12.3 |
| frustration_peak_mean | 2.792 | 2.708 |
| stuck_rate | 0.0 | 0.0 |
| break_ignored_rate | 0.0 | 0.0 |
| wrong_language_rate | 0.25 | 0.25 |
| replay_missing_rate | 0.1 | 0.1 |
| restart_failed_rate | 0.0 | 0.05 |
| harness_error_rate | 0.0 | 0.0 |

Evidence: `agent_org/runs/c01/qa/REQ-PREPRIMARY-CONTENT/r2/before-s*/` and `after-s*/` (per-agent reports, traces, server logs).
