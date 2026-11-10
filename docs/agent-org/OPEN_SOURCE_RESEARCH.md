# Open-source research: simulated-user frameworks

Checked on 9 Nov 2026. Each repository was shallow-cloned and its code read. Nothing was installed or executed: the clones were inspected as untrusted data. The README pages were read separately so their claims could be compared with the code.

## Summary

| Repo | Exists | Licence | Last commit | Size | What it really is | Decision |
|---|---|---|---|---|---|---|
| [danielgwilson/humanish](https://github.com/danielgwilson/humanish) | yes | MIT | 2026-11-05 (release 0.158.0, very active) | 3,034 files, TypeScript/Node 20–22 | Mature synthetic-participant "study" runner; computer-use actors on E2B hosted desktops, OpenAI computer-use provider, evidence bundles, per-lane spend caps, share-safety redaction | **Patterns adopted, not a dependency** |
| [renjie-liu/autouser](https://github.com/renjie-liu/autouser) | yes | MIT | 2026-06-18 (2 commits) | ~7.7k lines Python | Playwright + LLM plan→execute→reflect loop; persona archetypes with 5 dimensions; objective frustration model; audit pass; friction logs | **Patterns adopted (closest fit), not a dependency** |
| [Ericwong5021/persona-ux-test](https://github.com/Ericwong5021/persona-ux-test) | yes | MIT | 2026-07-30 (1 commit) | 5 files (SKILL.md, YAML) | A prompt/skill: blind-test contract, isolated persona subagent, Observed/Inferred/Unverified labels, P0–P3 report | **Methodology adopted** |
| [suhuandds/test-pilot-loop](https://github.com/suhuandds/test-pilot-loop) | yes | MIT | 2026-04-03 | 34 files, docs only ("not a packaged software library", per its own README) | Process templates: Cold → Guided → Insider test flights, debrief, fix, verification flight | **Loop structure adopted** |
| [Innex/braintrust-simulator](https://github.com/Innex/braintrust-simulator) | yes | README says MIT; **no LICENSE file in the repo** | 2026-02-08 (3 commits) | Next.js app | Multi-turn *chat* simulator for conversational agents, logs to Braintrust; needs OpenAI + Braintrust keys; **no browser automation** | **Rejected** |
| [andrew-shwetzer/human-experience](https://github.com/andrew-shwetzer/human-experience) | yes | MIT | 2026-03-10 (4 commits) | 19 files; Claude Code skill + Playwright `capture.mjs` | Single-page visual UX audit (screenshots at 3 viewports, 7-dimension score); persona = a `--persona` string only | **Rejected** (one idea borrowed) |

## Why none is used as a runtime dependency

Reading Buddy is a **voice** app. Its core interaction is a child speaking while a tutor listens, interrupts and corrects in real time. None of the six frameworks can produce or inject speech into a page's microphone. All of them model a user as clicks and typing judged from screenshots or DOM. All of the agentic ones also need a vision- or computer-use LLM at every step: OpenAI computer-use plus E2B for humanish, an Anthropic or Gemini key or a local CLI for autouser. That adds cost per step, makes runs non-reproducible, and doesn't fit the brief's "do not run 50 expensive model instances". This workspace also has no LLM API key.

So the agent organisation is built in this repo (`agent_org/`) on Playwright, which the app's Chromium already supports, plus a server-side speech simulation hook. The ideas below are carried over from the frameworks.

## What was adopted, from where

| Idea | Source | How it appears in `agent_org` |
|---|---|---|
| Persona = behavioural dimensions, not a name; seeded jitter around archetypes; seed 0 = unjittered baseline | autouser (`persona/`, `study.py`) | 50 persona specs with numeric traits; every run takes `--seed` |
| **Objective frustration**: built from observable trace events (failed actions, clicks with no effect, repeats, being interrupted), never from the agent's self-reported emotion; patience scales both the threshold and the time budget | autouser `affect.py` | `child_agent/affect.py`: frustration from interruptions, unheard speech, dead clicks, repeated corrections; abandonment when it crosses `patience` |
| Abandonment is a product finding, not a harness failure | humanish README | Abandoned sessions are recorded as outcomes with the trigger and evidence |
| False-success check: the persona thinks it finished, but an objective predicate disagrees | autouser | Reports compare the child's belief with the tutor's own summary (words read, lines completed) |
| Blind testing: no source, no docs, a fresh context per persona | persona-ux-test | The child driver sees only rendered DOM text, visible controls and Buddy's spoken lines; agents never read the repo or other reports |
| Findings labelled Observed / Inferred / Unverified | persona-ux-test | Every issue carries `evidence_level` |
| P0–P3 ranking | persona-ux-test | PM prioritisation engine |
| Evidence bundle per lane (screenshots, action trace, funnel) | humanish | `runs/<cycle>/agents/<id>/`: screenshots, `trace.jsonl`, `ws.jsonl`, `report.json` |
| Per-lane spend caps; N lanes ⇒ N × cap | humanish | Ledger with a Gnani credit cap per run; real-STT mode refuses to start above the cap |
| Second, persona-free reviewer classifies findings as real / artifact | autouser `--audit` | PM marks simulation artefacts (e.g. placeholder audio) separately from product issues |
| Cold → Guided → Insider flights; verification flight after fixes | test-pilot-loop | Cycle = blind baseline run → PM → engineering → QA → re-test of the same personas and seeds |
| Dimension scorecard | human-experience | Per-session UX scores (discoverability, guidance, interruption load, correction quality, completion) |

## Rejected, and why

- **braintrust-simulator**: tests text chat agents through HTTP endpoints. There's no browser and no audio, and it depends on two paid SaaS keys. The LICENSE file is missing even though the README says MIT, so licensing is unclear.
- **human-experience**: audits a single page visually. It has no multi-step journeys beyond scripted flows, no persona model and no orchestration.
- **humanish as a dependency**: high quality, but heavy (TypeScript monorepo, E2B desktops, OpenAI computer-use, Node 22). It would bring a second runtime and two paid services into a Python project to do something it can't do anyway (speak into the mic).
- **autouser as a dependency**: the closest match, Python and Playwright. But an LLM drives every step, it has no audio channel, and it is two commits old with no releases. We take its mechanisms instead of its runtime.

## Revisit later

If an Anthropic API key becomes available, the child driver's `narrate()` hook could be backed by an LLM that writes the child-voice narrative from the recorded evidence, autouser-style. The behaviour and the measurements would stay deterministic, so runs stay reproducible and cheap.
