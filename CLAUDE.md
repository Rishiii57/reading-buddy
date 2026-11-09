# Reading Buddy: notes for Claude Code

Voice reading tutor for children (Nursery to Class 4) in English, Hindi and Gujarati. FastAPI backend + vanilla JS frontend, on Gnani Prisma v2.5 (streaming STT) and Timbre v3.0 (TTS).

**AI product organisation** (Task 2, spec in `docs/agent-org/TASK2_SPEC.md`): `agent_org/` holds 50 simulated child users, the AI Product Manager, the Engineering workflow, independent QA and the audio evaluation. Start with `docs/agent-org/AGENT_ARCHITECTURE.md` and `docs/agent-org/RUN_INSTRUCTIONS.md`. Status and handoff notes are in `docs/agent-org/HANDOFF.md`.

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt   # + playwright/chromium for agent runs
.venv/bin/python -m pytest -q                         # offline tests; must stay green
.venv/bin/python -m eval.replay --no-write            # offline tutor scoring on recorded Prisma events
.venv/bin/uvicorn backend.main:app --port 8765        # the app for real use (needs GNANI_API_KEY in .env)
.venv/bin/python -m agent_org.orchestrator --cycle dbg --label x --agents 5 --parallel 2   # simulated children, zero credits
```

## Hard rules

- **Never** print, log, commit or copy `GNANI_API_KEY`. It lives only in `.env` (git-ignored).
- **Credits are finite** (5,000 for the team). Live sessions (mic **or** Demo reader) stream to Prisma for their whole length. Agent runs use `RB_SIM=1` (simulated STT) and `RB_TTS_OFFLINE=1`; the orchestrator removes the API key from the app's environment. `eval/run_stt.py` and `eval/make_testset.py` (for uncached lines) cost credits and need human approval.
- `RB_SIM` / `RB_TTS_OFFLINE` must stay off by default and are for automated testing only.
- Never record or store real children's voices. Personas are synthetic.
- Product Manager code never edits source; Engineering works only on PM-approved requirements (`agent_org.engineering.workflow start` enforces it); only QA (`agent_org.qa.validate`) marks an item validated; merge only after validation; nothing pushes or deploys without the human.
- Don't rewrite working modules: extend `TutorConfig`, add files, keep tests passing.
