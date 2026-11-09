# QA validation: REQ-MIC-TOGGLE (round 2)

**Verdict: validated_fixed** · candidate `50384d0c` vs base `951b5bce` · 10 personas × 2 seeds (20 sessions per build) · 1594.0 s

Personas: C1-01, C1-06, C2-02, C2-03, C2-04, C2-05, C2-06, C3-01, L03, L05

Original issue reproduced on base build: ✅

## Acceptance criteria (from the PM requirement)

| Metric | Target | Scope | Before | After | Check | Pass |
|---|---|---|---|---|---|---|
| mic_tap_pause_rate | <= 0.0 | all personas | 0.55 | 0.0 | 0.0 <= 0.0 | ✅ |

## Regression guards (same personas)

| Metric | Before | After | Rule | Pass |
|---|---|---|---|---|
| completion_rate | 0.2 | 0.3 | >= before-0.1 | ✅ |
| abandon_rate | 0.7 | 0.65 | <= before+0.1 | ✅ |
| false_corrections_per_agent | 0.15 | 0.25 | <= before+0.25 | ✅ |
| frustration_peak_mean | 3.157 | 2.862 | <= before+0.3 | ✅ |
| harness_error_rate | 0.0 | 0.0 | <= before+0.0 | ✅ |

## Offline tutor replay (recorded Prisma transcripts, base vs candidate)

| Check | Before | After | Pass |
|---|---|---|---|
| tracking_pass | 23/24 | 23/24 | ✅ |
| errors_caught | 23/24 | 23/24 | ✅ |
| stalls_prompted | 11/12 | 11/12 | ✅ |
| false_corrections_per_50_words | 0.104 | 0.104 | ✅ |
| stall_prompt_s_max (<= 4.0) | 2.46 | 2.46 | ✅ |

Unit tests on candidate: ✅ 42 passed in 0.36s

## All metrics

| Metric | Before | After |
|---|---|---|
| session_start_rate | 0.85 | 0.85 |
| completion_rate | 0.2 | 0.3 |
| abandon_rate | 0.7 | 0.65 |
| coverage | 0.489 | 0.54 |
| stall_interruptions_per_agent | 1.1 | 0.65 |
| correction_interruptions_per_agent | 0.4 | 0.5 |
| interruptions_per_agent | 1.6 | 1.3 |
| mic_tap_pause_rate | 0.55 | 0.0 |
| unheard_words_per_agent | 3.5 | 4.4 |
| drill_repeat_rate | 0.3 | 0.4 |
| spoken_guidance_gap_rate | 0.5 | 0.5 |
| consent_blocked_rate | 0.1 | 0.1 |
| consent_self_approved_rate | 0.1 | 0.1 |
| level_mismatch_rate | 0.2 | 0.2 |
| false_corrections_per_agent | 0.15 | 0.25 |
| missed_errors_per_agent | 0.35 | 0.4 |
| long_talk_rate | 0.6 | 0.6 |
| intro_s_median | 14.1 | 13.5 |
| frustration_peak_mean | 3.157 | 2.862 |
| stuck_rate | 0.0 | 0.0 |
| break_ignored_rate | 0.0 | 0.0 |
| wrong_language_rate | 0.15 | 0.15 |
| replay_missing_rate | 0.0 | 0.0 |
| restart_failed_rate | 0.0 | 0.0 |
| harness_error_rate | 0.0 | 0.0 |

Evidence: `agent_org/runs/c01/qa/REQ-MIC-TOGGLE/r2/before-s*/` and `after-s*/` (per-agent reports, traces, server logs).
