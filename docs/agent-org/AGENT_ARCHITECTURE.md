# Agent architecture: Reading Buddy's AI product organisation

A repeatable product-improvement loop. Simulated children use the **real** app, a Product Manager turns their evidence into requirements, Engineering implements approved requirements on isolated branches, and an independent QA validates every change before it counts as fixed.

```
             ┌────────────────────────── cycle N ──────────────────────────┐
 personas ─▶ │ orchestrator ─▶ 50 child agents ─▶ real app (UI + tutor)     │
 (50, data)  │      │             │  Playwright/Chromium   RB_SIM speech    │
             │      ▼             ▼                                         │
             │  status/ledger   individual reports + evidence              │
             │                    │                                         │
             │ audio evaluation ──┤  (measured Prisma + text-level tutor)   │
             │                    ▼                                         │
             │              AI Product Manager                              │
             │     aggregate → root causes → score → P0–P3 → requirements   │
             │                    │ approved (capacity) / human approval     │
             │                    ▼                                         │
             │   Engineering roles: branch + worktree per requirement       │
             │     inspect → root cause → implement → unit + replay tests   │
             │                    ▼ submit                                  │
             │   Independent QA: base vs candidate, same personas & seeds,  │
             │     acceptance criteria + regression guards → verdict        │
             │                    ▼ validated → merge (no push, no deploy)  │
             └──────── re-test all 50 on the merged build = cycle N+1 ──────┘
```

## Components and where they live

| Component | Code | Output |
|---|---|---|
| Simulation hooks in the app (off by default) | `backend/sim.py`, small hooks in `backend/main.py`, `backend/gnani.py` | — |
| Persona library (50) | `agent_org/personas/` (`build_library.py` → `library.json`, `persona.py` validation) | `PERSONA_LIBRARY.md` |
| Child agent | `agent_org/child_agent/driver.py` (browser behaviour), `speech_model.py` (what the child says and what STT writes), `affect.py` (objective frustration), `report.py` | `runs/<cycle>/<label>/<agent>/report.{json,md}`, `trace.jsonl`, `ws.jsonl`, `utterances.json`, `server_record.json`, `screens/` |
| Orchestrator | `agent_org/orchestrator.py` | `status.json`, `ledger.json`, `run.json`, `server.log` |
| Shared metrics | `agent_org/metrics.py` | used by PM and QA |
| AI Product Manager | `agent_org/pm/` (`catalog.py` root-cause knowledge, `engine.py`, `render.py`); state in `agent_org/pm/state/` | `USER_RESEARCH_REPORT.md`, `PRODUCT_REQUIREMENTS.md`, `PRODUCT_BACKLOG.md`, `USER_JOURNEY_ANALYSIS.md`, `PRIORITISATION_REPORT.md`, `decisions.jsonl`, `backlog.json` |
| Engineering team | `agent_org/engineering/workflow.py`, `ownership.json`, `changes/REQ-*.json` | branches `eng/REQ-*`, worktrees in `../rb-worktrees/` |
| Independent QA | `agent_org/qa/validate.py` | `runs/<cycle>/qa/<REQ>/r<n>/VALIDATION.{md,json}` |
| Speech/audio evaluation | `agent_org/audio_eval/run.py`, `augment.py` (+ existing `eval/`) | `runs/audio_eval/<label>.{md,json}` |
| Cycle runner and dashboard | `agent_org/cycle.py`, `agent_org/dashboard.py` | `PRODUCT_IMPROVEMENT_HISTORY.md`, `agent_org/runs/dashboard.html` |

## How a child agent experiences the product

1. **Isolated session**: its own browser context (cookies, localStorage), its own session token, seeded randomness. Agents never see each other's reports or any PM output.
2. **Blind**: no repo, docs or tutor internals. It perceives only the screen (visible buttons and labels, the speech bubble, the highlighted word, whether Buddy is animating) and Buddy's voice (the lines Buddy speaks). Labels are readable only as far as the persona reads English or that script; otherwise it taps by size and colour.
3. **Acts like a child**: taps by coordinates (animations and overlays matter, as on a tablet), scrolls, picks a language and a story, may meet the consent box, may tap the mic again "to talk", talks over Buddy, pauses to think, misreads, skips, repeats, self-corrects, says "I'm tired", taps curiously, gives up.
4. **Speaks** through the simulated speech channel (`POST /api/sim/utter`): the child's words, after a recognition-noise model, reach the real tutor engine with Prisma-like timing. Words spoken while the mic is muted are lost, as in the real frontend.
5. **Reports** what happened in its own words and as structured issues with evidence (timestamps, what it said, what the speech model wrote, what Buddy did, screenshots).

## Why simulation for speech (and what that costs us)

This workspace cannot reach the Gnani API, and a live session streams to Prisma for its whole length, so 50 agents × several cycles would eat the team's 5,000 credits. The `RB_SIM=1` hook replaces only the transport: the browser, frontend, WebSocket protocol, tutor engine, aligner and normaliser are the production code paths. Recognition accuracy is therefore **not** what the user simulation measures; it is measured separately (audio evaluation), and the PM keeps the two apart.

## Roles, rights and safety

| Role | May | May not |
|---|---|---|
| Child agents | use the UI; speak via the sim channel | read code/docs/other reports |
| Product Manager | read runs and evidence; write PM docs and backlog | edit source code |
| Engineering | work on approved requirements in `eng/REQ-*` worktrees; commit locally | start unapproved work; touch `.env`; push; deploy |
| QA | run base and candidate builds; set *validated_fixed* / *returned_to_engineering* | accept Engineering's word without measurement |
| Human team | approve content, privacy, data collection, architecture changes, pushes, releases | — |

Enforced in code: simulation runs drop `GNANI_API_KEY` from the app's environment; `engineering start` refuses unapproved requirements; `submit` refuses failing tests and `.env`; `merge` refuses anything QA has not validated; nothing pushes or deploys. No real child data is collected: personas are synthetic, and session logs (`SAVE_SESSIONS`) stay off.

## Resource controls

`--agents N` (spread across grades and languages), `--parallel K` (≤ 6, default 2–4), batches through a semaphore, `--retries` for harness errors (reported separately from product findings), live `status.json`, a per-run `ledger.json` (wall time, Gnani credits = 0 in sim mode, the seconds that *would* stream if run live, LLM tokens = 0). Persona contexts stay independent; only the app server is shared.
