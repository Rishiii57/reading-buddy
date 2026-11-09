# QA validation: REQ-CONSENT-GATE (round 1)

**Verdict: returned_to_engineering** · candidate `39e909bc` vs base `951b5bce` · 10 personas × 2 seeds (20 sessions per build) · 950.2 s

Personas: C1-05, C2-01, C2-06, C3-06, C4-01, L03, N01, N03, U04, N08

Original issue reproduced on base build: ✅

## Acceptance criteria (from the PM requirement)

| Metric | Target | Scope | Before | After | Check | Pass |
|---|---|---|---|---|---|---|
| consent_blocked_rate | <= 0.0 | personas without grown-up setup who cannot read English | 0.4 | 0.0 | 0.0 <= 0.0 | ✅ |
| consent_self_approved_rate | <= 0.0 | personas without grown-up setup who read English | 0.4 | 0.0 | 0.0 <= 0.0 | ✅ |

## Regression guards (same personas)

| Metric | Before | After | Rule | Pass |
|---|---|---|---|---|
| completion_rate | 0.25 | 0.1 | >= before-0.1 | ❌ |
| abandon_rate | 0.7 | 0.75 | <= before+0.1 | ✅ |
| false_corrections_per_agent | 0.35 | 0.5 | <= before+0.25 | ✅ |
| frustration_peak_mean | 2.29 | 3.302 | <= before+0.3 | ❌ |
| harness_error_rate | 0.0 | 0.0 | <= before+0.0 | ✅ |

## Offline tutor replay (recorded Prisma transcripts, base vs candidate)

| Check | Before | After | Pass |
|---|---|---|---|
| tracking_pass | 23/24 | 23/24 | ✅ |
| errors_caught | 23/24 | 23/24 | ✅ |
| stalls_prompted | 11/12 | 11/12 | ✅ |
| false_corrections_per_50_words | 0.104 | 0.104 | ✅ |
| stall_prompt_s_max (<= 4.0) | 2.46 | 2.46 | ✅ |

Unit tests on candidate: ✅ 42 passed in 0.32s

## All metrics

| Metric | Before | After |
|---|---|---|
| session_start_rate | 0.5 | 0.85 |
| completion_rate | 0.25 | 0.1 |
| abandon_rate | 0.7 | 0.75 |
| coverage | 0.321 | 0.31 |
| stall_interruptions_per_agent | 0.35 | 0.35 |
| correction_interruptions_per_agent | 0.05 | 0.05 |
| interruptions_per_agent | 0.4 | 0.6 |
| mic_tap_pause_rate | 0.15 | 0.4 |
| unheard_words_per_agent | 3.45 | 6.3 |
| drill_repeat_rate | 0.1 | 0.2 |
| spoken_guidance_gap_rate | 0.6 | 0.6 |
| consent_blocked_rate | 0.4 | 0.0 |
| consent_self_approved_rate | 0.4 | 0.0 |
| level_mismatch_rate | 0.5 | 0.5 |
| false_corrections_per_agent | 0.35 | 0.5 |
| missed_errors_per_agent | 0.15 | 0.15 |
| long_talk_rate | 0.45 | 0.7 |
| intro_s_median | 13.8 | 14.6 |
| frustration_peak_mean | 2.29 | 3.302 |
| stuck_rate | 0.0 | 0.0 |
| break_ignored_rate | 0.0 | 0.0 |
| wrong_language_rate | 0.3 | 0.3 |
| replay_missing_rate | 0.0 | 0.0 |
| restart_failed_rate | 0.0 | 0.0 |
| harness_error_rate | 0.0 | 0.0 |

Evidence: `agent_org/runs/c01/qa/REQ-CONSENT-GATE/r1/before-s*/` and `after-s*/` (per-agent reports, traces, server logs).
