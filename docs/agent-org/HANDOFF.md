# Task 2: status and handoff

Built in a cloud session on branch `agent-org-handoff` (pushed to `Rishiii57/reading-buddy`; not merged into `main`).

## What exists

| Deliverable | Where |
|---|---|
| Working multi-agent architecture | `agent_org/`, explained in `AGENT_ARCHITECTURE.md` |
| 50 distinct child personas | `agent_org/personas/`, `PERSONA_LIBRARY.md` |
| Independent user simulation with real browser interaction | `agent_org/child_agent/` (Playwright + Chromium, the real UI and tutor), `agent_org/orchestrator.py` |
| AI Product Manager + prioritisation engine | `agent_org/pm/`, `PRODUCT_MANAGER_GUIDELINES.md`; outputs `USER_RESEARCH_REPORT.md`, `PRODUCT_REQUIREMENTS.md`, `PRODUCT_BACKLOG.md`, `USER_JOURNEY_ANALYSIS.md`, `PRIORITISATION_REPORT.md` |
| AI Engineering team | `agent_org/engineering/`, `ENGINEERING_WORKFLOW.md` |
| Independent AI QA team | `agent_org/qa/validate.py`, `QA_WORKFLOW.md` |
| Speech and audio evaluation | `agent_org/audio_eval/` (+ existing `eval/`) |
| Central feedback collection, history, dashboard | `agent_org/runs/`, `agent_org/cycle.py`, `PRODUCT_IMPROVEMENT_HISTORY.md`, `agent_org/dashboard.py` |
| Evaluation of the whole system | `AGENT_EVALUATION_REPORT.md` |
| Setup | `RUN_INSTRUCTIONS.md` |

## Where it stands (10 Nov 2026)

- One full cycle run: 50-child baseline (c01) → PM (14 root causes) → 5 requirements engineered (2 PM-approved, 3 approved by the team) → QA (9 validation rounds; 3 validated, 2 merged on the team's directive with QA evidence) → 50-child re-test (c02).
- Like-for-like result (same children, seeds and agents): finished 18 % → 40 %, abandoned 72 % → 40 %, text covered 41 % → 63 %, peak frustration 3.15 → 1.70. Details: `AGENT_EVALUATION_REPORT.md`; dashboard: `agent_org/runs/dashboard.html`.
- Next cycle candidates (P2, deferred): long intro, talk-over-Buddy, mid-line corrections, drill loop, navigation.

## Decisions taken without the human (and why)

- **Simulated speech for agent runs.** This workspace cannot reach the Gnani API, and live sessions spend credits for their whole length. The browser, UI, WebSocket protocol, tutor, aligner and normaliser are the production code paths; only Prisma's transport is replaced (`RB_SIM=1`, off by default). Speech-recognition accuracy is measured separately.
- **Deterministic persona policies instead of LLM-driven agents.** There is no LLM API key here, and the spec asks for evidence-based, controllable cost. Behaviour is seeded and reproducible; no LLM tokens are used.
- **No framework dependency.** See `OPEN_SOURCE_RESEARCH.md`: none of the six handles a voice app; their best ideas are adopted.

## Waiting for a human decision

- `REQ-PREPRIMARY-CONTENT`: merged (13 traditional rhymes). Hindi/Gujarati text needs a native speaker's check; 10 % of pre-primary children still open a Grade text (PM flagged it again).
- `REQ-CONSENT-GATE`: consent dialog removed on the team's decision.
- `REQ-FALSE-CORRECTION-STT`, `REQ-LENIENT-MATCHING`: voice-data collection and a product decision on error tolerance.
- Credits (approved, must run where Gnani is reachable): `python -m backend.pregen --words` for the new rhymes and phrases, then the augmented audio set (see RUN_INSTRUCTIONS.md).
- Merging `agent-org-handoff` into `main` (pull request), and any deploy.

## Picking up in Claude Code (local)

Pull the branch, `pip install -r requirements-dev.txt playwright`, `python -m playwright install chromium`, then follow `RUN_INSTRUCTIONS.md`. Worktrees for engineering live in `../rb-worktrees/` (recreated by `engineering.workflow start`).
