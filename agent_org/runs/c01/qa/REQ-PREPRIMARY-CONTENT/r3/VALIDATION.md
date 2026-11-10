# QA validation: REQ-PREPRIMARY-CONTENT (round 3)

**Verdict: returned_to_engineering** · candidate `c78f125f` vs base `af436556` · 10 personas × 2 seeds (20 sessions per build) · 948.3 s

Personas: L01, L02, L03, L04, L05, L06, L07, L08, N01, N02

Original issue reproduced on base build: ✅

## Acceptance criteria (from the PM requirement)

| Metric | Target | Scope | Before | After | Check | Pass |
|---|---|---|---|---|---|---|
| level_mismatch_rate | <= 0.0 | pre-primary personas | 0.9 | 0.2 | 0.2 <= 0.0 | ❌ |
| coverage | >= 0.6 | pre-primary personas | 0.079 | 0.362 | 0.362 >= 0.6 | ❌ |
| stuck_rate | <= 0.1 | pre-primary personas | 0.0 | 0.0 | 0.0 <= 0.1 | ✅ |

## Regression guards (same personas)

| Metric | Before | After | Rule | Pass |
|---|---|---|---|---|
| completion_rate | 0.0 | 0.25 | >= before-0.1 | ✅ |
| abandon_rate | 0.65 | 0.65 | <= before+0.1 | ✅ |
| false_corrections_per_agent | 0.0 | 0.0 | <= before+0.25 | ✅ |
| frustration_peak_mean | 1.693 | 2.312 | <= before+0.3 | ❌ |
| harness_error_rate | 0.1 | 0.05 | <= before+0.0 | ✅ |

## Offline tutor replay (recorded Prisma transcripts, base vs candidate)

| Check | Before | After | Pass |
|---|---|---|---|
| tracking_pass | 23/24 | 23/24 | ✅ |
| errors_caught | 23/24 | 23/24 | ✅ |
| stalls_prompted | 11/12 | 11/12 | ✅ |
| false_corrections_per_50_words | 0.104 | 0.104 | ✅ |
| stall_prompt_s_max (<= 4.0) | 3.91 | 3.91 | ✅ |

Unit tests on candidate: ✅ 64 passed in 0.83s

## All metrics

| Metric | Before | After |
|---|---|---|
| session_start_rate | 0.6 | 0.75 |
| completion_rate | 0.0 | 0.25 |
| abandon_rate | 0.65 | 0.65 |
| coverage | 0.079 | 0.362 |
| stall_interruptions_per_agent | 0.25 | 0.6 |
| correction_interruptions_per_agent | 0.3 | 0.15 |
| interruptions_per_agent | 0.7 | 1.05 |
| mic_tap_pause_rate | 0.0 | 0.0 |
| unheard_words_per_agent | 0.55 | 1.2 |
| drill_repeat_rate | 0.1 | 0.1 |
| spoken_guidance_gap_rate | 0.0 | 0.0 |
| consent_blocked_rate | 0.15 | 0.0 |
| consent_self_approved_rate | 0.0 | 0.0 |
| level_mismatch_rate | 0.9 | 0.2 |
| false_corrections_per_agent | 0.0 | 0.0 |
| missed_errors_per_agent | 0.0 | 0.3 |
| long_talk_rate | 0.45 | 0.5 |
| intro_s_median | 14.0 | 13.9 |
| frustration_peak_mean | 1.693 | 2.312 |
| stuck_rate | 0.0 | 0.0 |
| break_ignored_rate | 0.0 | 0.0 |
| wrong_language_rate | 0.25 | 0.25 |
| replay_missing_rate | 0.1 | 0.1 |
| restart_failed_rate | 0.0 | 0.05 |
| harness_error_rate | 0.1 | 0.05 |

Evidence: `agent_org/runs/c01/qa/REQ-PREPRIMARY-CONTENT/r3/before-s*/` and `after-s*/` (per-agent reports, traces, server logs).
