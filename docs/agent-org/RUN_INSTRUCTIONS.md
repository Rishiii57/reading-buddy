# Run instructions: the AI product organisation

Everything below runs offline and costs **no Gnani credits and no LLM tokens** unless a step says otherwise.

## 1. Setup (once)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/pip install playwright && .venv/bin/python -m playwright install chromium   # skip if Playwright+Chromium already exist
.venv/bin/python -m pytest -q                                                        # 42+ tests, all offline
```

The simulated runs never use `GNANI_API_KEY`: the orchestrator removes it from the app's environment. `.env` is only needed to run the app for real people, or for the credit-spending audio steps.

## 2. A user study (child agents on the real app)

```bash
# start small, as the rollout plan says: 5, then 10, then 50
.venv/bin/python -m agent_org.orchestrator --cycle c01 --label pilot --agents 5 --parallel 2
.venv/bin/python -m agent_org.orchestrator --cycle c01 --label n10 --agents 10 --parallel 4
.venv/bin/python -m agent_org.orchestrator --cycle c01 --label baseline --agents 50 --parallel 4   # ~30 min
# or particular personas / grades
.venv/bin/python -m agent_org.orchestrator --cycle dbg --label x --ids N01,C4-02 --parallel 1
.venv/bin/python -m agent_org.orchestrator --cycle dbg --label y --grades Nursery,LKG
```

It starts the app itself in simulation mode (`RB_SIM=1 RB_TTS_OFFLINE=1`) on port 8790; `--app-root` tests another checkout (a worktree). Live progress is in `agent_org/runs/<cycle>/<label>/status.json`. Results per child are in `<agent>/report.md`, with evidence beside them. `ledger.json` gives wall time, credits (0), and the seconds of audio the same sessions would have streamed live.

Each agent runs in real time (Buddy's speech, pauses and timeouts are real), so 50 agents at `--parallel 4` take about half an hour on 2 CPUs. Keep `--parallel` ≤ 6.

## 3. Speech and audio evaluation

```bash
.venv/bin/python -m agent_org.audio_eval.run --label c01-baseline        # measured Prisma recordings + text-level tutor tests
.venv/bin/python -m eval.make_testset && .venv/bin/python -m agent_org.audio_eval.augment   # build fast/slow/whisper/child-like/noisy WAVs (offline)
# CREDITS: stream the augmented audio through Prisma (human-approved step; needs .env)
.venv/bin/python -m eval.run_stt --variants aug_fast,aug_slow,aug_whisper,aug_childlike,aug_classroom
```

## 4. Product Manager

```bash
.venv/bin/python -m agent_org.pm.engine --cycle c01 --label baseline --capacity 8 --publish
```

This writes `USER_RESEARCH_REPORT.md`, `USER_JOURNEY_ANALYSIS.md`, `PRODUCT_REQUIREMENTS.md`, `PRIORITISATION_REPORT.md` and `PRODUCT_BACKLOG.md` (into `docs/agent-org/` with `--publish`, and always into the run's `pm/` folder), and updates `agent_org/pm/state/`.

## 5. Engineering and QA (per approved requirement)

```bash
.venv/bin/python -m agent_org.engineering.workflow status
.venv/bin/python -m agent_org.engineering.workflow start REQ-MIC-TOGGLE --role "Frontend Engineer"
#   ... implement in ../rb-worktrees/REQ-MIC-TOGGLE, add tests ...
.venv/bin/python -m agent_org.engineering.workflow submit REQ-MIC-TOGGLE --summary "..." --root-cause "..."
.venv/bin/python -m agent_org.qa.validate REQ-MIC-TOGGLE --cycle c01 --reps 2
.venv/bin/python -m agent_org.engineering.workflow merge REQ-MIC-TOGGLE      # only after validated_fixed
```

## 6. Next cycle, history and dashboard

```bash
.venv/bin/python -m agent_org.cycle study --cycle c02 --label retest --agents 50 --parallel 4   # study + audio eval + PM
.venv/bin/python -m agent_org.cycle history        # docs/agent-org/PRODUCT_IMPROVEMENT_HISTORY.md
.venv/bin/python -m agent_org.dashboard            # agent_org/runs/dashboard.html
```

## Steps that spend Gnani credits (run on your machine, with `.env`)

The cloud workspace that built this system cannot reach `api.vachana.ai`, so these steps were prepared but not run there. The team approved using credits within the 5,000 limit. Check the balance at https://app.gnani.ai/voice before and after.

```bash
# 1. Buddy's voice for the 13 new pre-primary rhymes, the new phrases (reader hint) and every rhyme word (~250 Timbre calls, one-off; cached in cache/tts)
.venv/bin/python -m backend.pregen --words
git add cache/tts && git commit -m "TTS cache for pre-primary rhymes"     # so nobody pays for them again

# 2. Real-speech evaluation of fast / slow / whisper / child-like / classroom-noise audio (~1,070 s streamed to Prisma)
.venv/bin/python -m eval.make_testset            # offline: rebuilds WAVs from the cache
.venv/bin/python -m agent_org.audio_eval.augment # offline: builds the variants
.venv/bin/python -m eval.run_stt --variants aug_fast,aug_slow,aug_whisper,aug_childlike,aug_classroom
.venv/bin/python -m agent_org.audio_eval.run --label real-variants   # now includes the measured variants
```

`cache/usage.json` keeps a local tally of TTS calls and streamed STT seconds.

## Adding personas

Add a row to `ROWS` in `agent_org/personas/build_library.py`, then run `python -m agent_org.personas.build_library` (validates) and `python -m agent_org.personas.render_doc`.

## Running against real speech (optional, costs credits)

Start the app normally with `.env` and use it yourself. The child agents can't produce real audio, so real-speech checks go through the audio evaluation (step 3) and consenting adult team members. Never record children without written parental consent and safeguards.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `app did not start` | see `runs/<cycle>/<label>/server.log`; port busy → `--port 8791` |
| many `harness_error` outcomes | read `report.json` → `harness_error`; these are excluded from PM analysis and retried once |
| fonts look different in screenshots | Google Fonts are blocked in sandboxes; layout is otherwise unaffected |
