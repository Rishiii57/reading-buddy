# Product improvement history

Written by `python -m agent_org.cycle history` from the PM analyses, QA validations and engineering change records. Each cycle is a full user study (simulated children on the real app); fixes between cycles are only counted when QA validated them.

## c01 / baseline (2026-11-09T18:37:11, 50 children)

Baseline. Problems found: P0 RC-PREPRIMARY-CONTENT, P0 RC-CONSENT-GATE, P1 RC-SPOKEN-ONBOARDING, P1 RC-STALL-TIMING, P2 RC-MIDLINE-CORRECTION, P2 RC-MIC-TOGGLE, P2 RC-TALK-OVER-BUDDY, P2 RC-LONG-INTRO, P2 RC-DRILL-LOOP, P2 RC-FALSE-CORRECTION-TUTOR, P2 RC-FALSE-CORRECTION-STT, P3 RC-LENIENT-MATCHING, P2 RC-LANGUAGE-SELECTION, P2 RC-NAVIGATION, P3 RC-REPLAY.

### Engineering and QA after this study

| Requirement | Round | Verdict | Criteria | Files changed |
|---|---|---|---|---|
| REQ-CONSENT-GATE | 1 | **returned_to_engineering** | consent_blocked_rate 0.4→0.0 ✅; consent_self_approved_rate 0.4→0.0 ✅ | SETUP.md, frontend/app.js, frontend/index.html |
| REQ-CONSENT-GATE | 2 | **returned_to_engineering** | consent_blocked_rate 0.4→0.0 ✅; consent_self_approved_rate 0.4→0.0 ✅ | SETUP.md, frontend/app.js, frontend/index.html |
| REQ-MIC-TOGGLE | 2 | **validated_fixed** | mic_tap_pause_rate 0.55→0.0 ✅ | frontend/app.js, frontend/styles.css |
| REQ-PREPRIMARY-CONTENT | 1 | **returned_to_engineering** | level_mismatch_rate 1.0→0.4 ❌; coverage 0.094→0.137 ❌; stuck_rate 0.0→0.0 ✅ | backend/content.py, backend/main.py, backend/tutor.py, content/en-IN.json, content/gu-IN.json, content/hi-IN.json, frontend/app.js, frontend/styles.css, tests/test_tutor.py |
| REQ-PREPRIMARY-CONTENT | 2 | **returned_to_engineering** | level_mismatch_rate 1.0→0.2 ❌; coverage 0.1→0.407 ❌; stuck_rate 0.0→0.0 ✅ | backend/content.py, backend/main.py, backend/tutor.py, content/en-IN.json, content/gu-IN.json, content/hi-IN.json, frontend/app.js, frontend/styles.css, tests/test_tutor.py |
| REQ-PREPRIMARY-CONTENT | 3 | **returned_to_engineering** | level_mismatch_rate 0.9→0.2 ❌; coverage 0.079→0.362 ❌; stuck_rate 0.0→0.0 ✅ | backend/content.py, backend/main.py, backend/tutor.py, content/en-IN.json, content/gu-IN.json, content/hi-IN.json, frontend/app.js, frontend/styles.css, tests/test_tutor.py |
| REQ-PREPRIMARY-CONTENT | 4 | **returned_to_engineering** | level_mismatch_rate 1.0→0.2 ❌; coverage 0.155→0.412 ❌; stuck_rate 0.0→0.0 ✅ | backend/content.py, backend/main.py, backend/tutor.py, content/en-IN.json, content/gu-IN.json, content/hi-IN.json, frontend/app.js, frontend/styles.css, tests/test_tutor.py |
| REQ-SPOKEN-ONBOARDING | 1 | **validated_fixed** | spoken_guidance_gap_rate 1.0→0.0 ✅ | backend/main.py, backend/phrases.py, frontend/app.js, tests/test_phrases.py |
| REQ-STALL-TIMING | 1 | **returned_to_engineering** | stall_interruptions_per_agent 0.714→0.536 ❌; stuck_rate 0.0→0.0 ✅ | backend/tutor.py, tests/test_tutor.py |
| REQ-STALL-TIMING | 2 | **validated_fixed** | stall_interruptions_per_agent 0.55→0.25 ✅; stuck_rate 0.0→0.0 ✅ | backend/tutor.py, tests/test_tutor.py |

## c02 / retest (2026-11-10T11:37:02, 50 children)

- **Newly discovered:** RC-RESTART
- **Still unresolved:** RC-PREPRIMARY-CONTENT (26→5 children), RC-SPOKEN-ONBOARDING (35→1 children), RC-STALL-TIMING (20→11 children), RC-MIDLINE-CORRECTION (13→3 children), RC-TALK-OVER-BUDDY (26→26 children), RC-LONG-INTRO (35→33 children), RC-DRILL-LOOP (3→5 children), RC-FALSE-CORRECTION-TUTOR (4→5 children), RC-FALSE-CORRECTION-STT (4→2 children), RC-LENIENT-MATCHING (10→14 children), RC-LANGUAGE-SELECTION (12→12 children), RC-NAVIGATION (12→18 children), RC-REPLAY (4→4 children)
- **Successfully fixed (QA-validated, not observed now):** RC-MIC-TOGGLE
- **Not observed now but not validated:** RC-CONSENT-GATE
- **Fixed with residual cases (QA-validated, fewer children affected):** RC-SPOKEN-ONBOARDING (35→1), RC-STALL-TIMING (20→11)
- **Regressions (validated earlier, no fewer children affected now):** none

### Usability

| Metric | Previous → now |
|---|---|
| session_start_rate | 0.84 → 0.88 (+0.04) ▲ better |
| abandon_rate | 0.68 → 0.4 (-0.28) ▲ better |
| mic_tap_pause_rate | 0.38 → 0.0 (-0.38) ▲ better |
| spoken_guidance_gap_rate | 0.7 → 0.0 (-0.7) ▲ better |
| consent_blocked_rate | 0.1 → 0.0 (-0.1) ▲ better |
| unheard_words_per_agent | 3.44 → 2.6 (-0.84) ▲ better |
| long_talk_rate | 0.7 → 0.66 (-0.04) ▲ better |
| intro_s_median | 14.0 → 13.8 (-0.2) ▲ better |
| frustration_peak_mean | 2.943 → 1.704 (-1.239) ▲ better |

### Learning experience

| Metric | Previous → now |
|---|---|
| completion_rate | 0.2 → 0.4 (+0.2) ▲ better |
| coverage | 0.408 → 0.626 (+0.218) ▲ better |
| interruptions_per_agent | 1.08 → 0.68 (-0.4) ▲ better |
| stall_interruptions_per_agent | 0.62 → 0.36 (-0.26) ▲ better |
| correction_interruptions_per_agent | 0.32 → 0.08 (-0.24) ▲ better |
| drill_repeat_rate | 0.06 → 0.1 (+0.04) ▼ worse |
| false_corrections_per_agent | 0.16 → 0.16 (+0.0) = |
| missed_errors_per_agent | 0.38 → 0.34 (-0.04) ▲ better |
| stuck_rate | 0.0 → 0.0 (+0.0) = |

### By grade (completion, coverage, interruptions/agent, peak frustration)

| Grade | Completion | Coverage | Interruptions/agent | Peak frustration |
|---|---|---|---|---|
| Nursery | 0.0 → 0.0 (+0.0) = | 0.095 → 0.185 (+0.09) ▲ better | 0.8 → 0.6 (-0.2) ▲ better | 3.285 → 1.835 (-1.45) ▲ better |
| LKG | 0.0 → 0.0 (+0.0) = | 0.068 → 0.35 (+0.282) ▲ better | 1.125 → 1.375 (+0.25) ▼ worse | 2.856 → 2.288 (-0.568) ▲ better |
| UKG | 0.0 → 0.375 (+0.375) ▲ better | 0.196 → 0.661 (+0.465) ▲ better | 1.125 → 0.875 (-0.25) ▲ better | 3.288 → 1.281 (-2.007) ▲ better |
| Class 1 | 0.0 → 0.833 (+0.833) ▲ better | 0.331 → 0.9 (+0.569) ▲ better | 1.5 → 0.167 (-1.333) ▲ better | 3.458 → 1.592 (-1.866) ▲ better |
| Class 2 | 0.167 → 0.333 (+0.166) ▲ better | 0.708 → 0.753 (+0.045) ▲ better | 1.0 → 0.5 (-0.5) ▲ better | 3.65 → 2.192 (-1.458) ▲ better |
| Class 3 | 0.833 → 0.667 (-0.166) ▼ worse | 0.974 → 0.911 (-0.063) ▼ worse | 2.167 → 1.0 (-1.167) ▲ better | 2.575 → 1.242 (-1.333) ▲ better |
| Class 4 | 0.667 → 1.0 (+0.333) ▲ better | 0.878 → 1.0 (+0.122) ▲ better | 0.0 → 0.0 (+0.0) = | 1.175 → 1.358 (+0.183) ▼ worse |

### By language

| Language | Completion | Coverage | False corr./agent | Wrong language |
|---|---|---|---|---|
| English | 0.118 → 0.235 (+0.117) ▲ better | 0.416 → 0.601 (+0.185) ▲ better | 0.118 → 0.235 (+0.117) ▼ worse | 0.294 → 0.294 (+0.0) = |
| Hindi | 0.235 → 0.471 (+0.236) ▲ better | 0.396 → 0.601 (+0.205) ▲ better | 0.059 → 0.059 (+0.0) = | 0.176 → 0.176 (+0.0) = |
| Gujarati | 0.25 → 0.5 (+0.25) ▲ better | 0.413 → 0.681 (+0.268) ▲ better | 0.312 → 0.188 (-0.124) ▲ better | 0.188 → 0.188 (+0.0) = |

## Backlog now

- RC-PREPRIMARY-CONTENT: awaiting_human_approval (P1)
- RC-CONSENT-GATE: accepted_by_human (P0)
- RC-SPOKEN-ONBOARDING: validated_fixed (P2)
- RC-STALL-TIMING: validated_fixed (P1)
- RC-MIDLINE-CORRECTION: deferred (P2)
- RC-MIC-TOGGLE: validated_fixed (P2)
- RC-TALK-OVER-BUDDY: deferred (P2)
- RC-LONG-INTRO: deferred (P2)
- RC-DRILL-LOOP: deferred (P2)
- RC-FALSE-CORRECTION-TUTOR: deferred (P2)
- RC-FALSE-CORRECTION-STT: awaiting_human_approval (P2)
- RC-LENIENT-MATCHING: awaiting_human_approval (P3)
- RC-LANGUAGE-SELECTION: deferred (P3)
- RC-NAVIGATION: deferred (P2)
- RC-REPLAY: deferred (P3)
- RC-RESTART: deferred (P3)
