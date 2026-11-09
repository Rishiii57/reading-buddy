# Task 2 handoff: status and plan

Moved from a cloud session to Claude Code on 9 Nov 2026.

## Done

- Phase 1, codebase audit: `docs/agent-org/ARCHITECTURE_AUDIT.md` (architecture, STT/TTS, content, tutor state machine, tests, 11 limitations).
- Spec copied to `docs/agent-org/TASK2_SPEC.md`; rules for Claude Code in `/CLAUDE.md`.
- Verified locally: `pytest` → 42 passed.

## Not done yet (pick up here)

- **Phase 1, open-source research**: verify the 6 repos in spec Part 7 (humanish, autouser, persona-ux-test, test-pilot-loop, braintrust-simulator, human-experience). Check that each exists, its licence, last commit, what the code actually does, and whether it suits a voice app driven through a fake mic. Write `OPEN_SOURCE_RESEARCH.md`. Expect most to be thin wrappers around LLM + Playwright; adopt patterns, not dependencies, unless one clearly fits.
- Phases 2–9 as in the spec.

## Decisions to confirm with the human before Phase 3

1. **Which LLM powers the agents** (child personas, PM, engineers, QA): Claude Code subagents (no extra API key; agents defined in `.claude/agents/`) or a scripted runner calling the Anthropic API (needs `ANTHROPIC_API_KEY`, gives token accounting). A hybrid works well: deterministic Playwright behaviour policies per persona generate the evidence, and LLM agents write the reports, PM analysis, engineering and QA.
2. **Gnani credit budget for Task 2.** Suggested: zero-credit mode for all routine agent runs; ≤ ~300 credits total for real-STT spot checks (5 personas × 3 languages) and Phase 7.
3. **Branching**: work on `agent-org` and open PRs to `main`, or commit directly.

## Recommended architecture (summary; formalise in AGENT_ARCHITECTURE.md)

```
agent_org/
  personas/            50 persona YAML/JSON files + schema (Nursery 10, LKG 8, UKG 8, Class 1–4 × 6)
  child_agent/         Playwright driver + per-persona behaviour policy (blind: sees only the UI + a child-level intro)
  speech/              persona → synthetic reading plan (skips, subs, hesitations, repeats, whisper, speed)
                       → WAV via cached Timbre (fake mic) OR scripted transcripts (zero-credit STT_BACKEND)
  orchestrator.py      batches, --agents N, --parallel K, retries, status file, cost/token ledger
  pm/                  aggregate reports → cluster root causes → score (severity × reach × grade weight …) → P0–P3 → requirements
  engineering/         role ownership map, requirement → branch/worktree, change log
  qa/                  reproduce → verify → regression (pytest + eval.replay + targeted persona re-runs) → validation report
  audio_eval/          extends eval/: WER, false-correction, missed-error, alignment, latency per language
  dashboard/           static HTML generated from runs/*.json
  runs/<cycle-id>/     everything one cycle produced (history kept)
```

Key implementation notes:
- **Real mic path**: Chromium `--use-fake-ui-for-media-stream --use-fake-device-for-media-stream --use-file-for-fake-audio-capture=<persona.wav>`. Audio loops in Chromium, so pad the WAV with silence and end the session from the agent.
- **Zero-credit path**: add an opt-in `STT_BACKEND=script` in `backend/` that replays a per-session transcript plan (sent in the `start` message or looked up by an agent token) with realistic timings. It must be off by default and never reachable in production.
- **Evidence per agent**: screenshots at key steps, the WebSocket message log (state/say/heard/summary), `engine.log` via `SAVE_SESSIONS=1` (synthetic personas only), timings, and the final summary. Reports must cite this evidence.
- **Blindness**: child-agent prompts get only the app URL, the persona and a one-paragraph child-level intro. They never see the repo, the docs, other agents' reports or PM output.
- **Start with 5 personas → 10 → 50**, as the spec requires.

## Likely first findings to validate with agents (not assumed)

No pre-primary content; English-only on-screen instructions; fixed stall timing for every child; 10 mistakes before a line is skipped; weak robustness to noise and hesitation; only line 1 demonstrated; no replay-line control; default language Gujarati; no reconnect after a drop. Details are in the audit, §8.
