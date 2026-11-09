# Task 2: status and handoff

Built in a cloud session on branch `agent-org-handoff` (local commits; not yet pushed, pending write access to `Rishiii57/reading-buddy`).

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

## Decisions taken without the human (and why)

- **Simulated speech for agent runs.** This workspace cannot reach the Gnani API, and live sessions spend credits for their whole length. The browser, UI, WebSocket protocol, tutor, aligner and normaliser are the production code paths; only Prisma's transport is replaced (`RB_SIM=1`, off by default). Speech-recognition accuracy is measured separately.
- **Deterministic persona policies instead of LLM-driven agents.** There is no LLM API key here, and the spec asks for evidence-based, controllable cost. Behaviour is seeded and reproducible; no LLM tokens are used.
- **No framework dependency.** See `OPEN_SOURCE_RESEARCH.md`: none of the six handles a voice app; their best ideas are adopted.

## Waiting for a human decision

- `REQ-PREPRIMARY-CONTENT` (P0): pre-primary reading material. Needs content authored and native-speaker review in Hindi and Gujarati.
- `REQ-CONSENT-GATE` (P0): consent redesign. Needs privacy wording approved by the team.
- `REQ-FALSE-CORRECTION-STT`, `REQ-LENIENT-MATCHING`: voice-data collection and a product decision on error tolerance.
- Credits: streaming the augmented audio set (`audio_eval.augment`, about 1,070 s of audio) through Prisma.
- Pushing the branch, and any deploy.

## Picking up in Claude Code (local)

Pull the branch, `pip install -r requirements-dev.txt playwright`, `python -m playwright install chromium`, then follow `RUN_INSTRUCTIONS.md`. Worktrees for engineering live in `../rb-worktrees/` (recreated by `engineering.workflow start`).
