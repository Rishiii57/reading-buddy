# Reading Buddy: notes for Claude Code

Voice reading tutor for children (Nursery to Class 4) in English, Hindi and Gujarati. FastAPI backend + vanilla JS frontend, on Gnani Prisma v2.5 (streaming STT) and Timbre v3.0 (TTS).

Current work: **Task 2, an AI product organisation** (50 simulated child users, AI Product Manager, Engineering team, independent QA). Spec: `docs/agent-org/TASK2_SPEC.md`. Status and next steps: `docs/agent-org/HANDOFF.md`. Codebase audit: `docs/agent-org/ARCHITECTURE_AUDIT.md`. Read all three before starting.

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt   # Windows: py -m venv .venv; .venv\Scripts\pip ...
.venv/bin/python -m pytest -q                       # 42 offline tests, no API calls; must stay green
.venv/bin/python -m eval.replay --no-write          # offline tutor scoring from recorded Prisma events, no credits
.venv/bin/uvicorn backend.main:app --port 8765      # run the app (needs GNANI_API_KEY in .env)
```

## Hard rules

- **Never** print, log, commit or copy `GNANI_API_KEY`. It lives only in `.env` (git-ignored). Don't put it in reports, agent prompts, screenshots or test fixtures.
- **Credits are finite** (5,000 for the whole team). Any live session (mic **or** Demo reader) streams to Prisma for its full duration, and new utterances cost Timbre calls. Default every agent run to the zero-credit STT mode. Real-STT runs need an explicit budget flag and a cost estimate printed first. Never run 50 live sessions.
- `eval/run_stt.py` and `eval/make_testset.py` call the API; `eval/replay.py` and `tests/` don't.
- Never record or store real children's voices. Personas are synthetic; test audio is synthetic TTS or consenting adult team members only.
- Don't rewrite working modules. Extend `TutorConfig`, add files, keep the existing tests passing.
- Work on a branch (not `main`), and commit in small, reviewable steps. Major architecture changes and any deploy (`render.yaml`) need the human's approval.
- Follow the phase order in the spec. Don't claim a feature works unless it was run and checked.
- PM agents never edit source code; Engineering works only from approved requirements; QA validates independently, with before/after evidence.

## Where things go

- New agent system: `agent_org/` (Python package), outputs under `agent_org/runs/<cycle-id>/` (git-ignore bulky artefacts such as screenshots and traces).
- Required docs (AGENT_ARCHITECTURE.md, PERSONA_LIBRARY.md, … RUN_INSTRUCTIONS.md): `docs/agent-org/`.
