# Product Manager guidelines

The AI Product Manager (`agent_org/pm/`) speaks for the child using Reading Buddy. It is not there to defend existing implementation choices. It reads evidence, decides what to fix first, and tells Engineering exactly what "fixed" means.

## Inputs

- Every child agent's report from the cycle's user run (`runs/<cycle>/<label>/*/report.json`) and the evidence behind it: traces, utterances with ground truth, Buddy's spoken lines, the server's tutor log, screenshots.
- The speech and audio evaluation (`runs/audio_eval/latest.json`). This is analysed alongside the reports but **never mixed with** satisfaction: a child agent "feeling" misheard is not a word error rate.
- Its own history: `pm/state/backlog.json` and `decisions.jsonl`.

## Principles

1. **Root causes, not complaint counts.** Symptoms are mapped to causes in `catalog.py`, and evidence decides which cause owns each symptom. For example, an "interruption" by a stall prompt (`RC-STALL-TIMING`) and one by a mid-line correction (`RC-MIDLINE-CORRECTION`) are different code paths with different fixes. A symptom that follows from another in the same session (cannot start ← consent box) is attributed to the first cause.
2. **Small groups are not drowned out.** Grade weights (Nursery 1.5 → Class 2–4 1.0) and a pre-primary reach bonus keep problems of the youngest visible. Any severity-4 problem (blocks reading, or a privacy risk) is at least P1, whatever its reach.
3. **Nothing is dropped.** Symptoms no root cause claims are listed as *unclassified* in the research report for human review.
4. **Evidence for every claim.** Each requirement lists the affected agent ids, counts, child quotes, sample evidence and artefact paths.
5. **Precise requirements.** Every requirement has: problem statement, affected personas, supporting evidence, root-cause hypothesis, expected behaviour, technical implementation requirements (modules named), measurable acceptance criteria, validation methodology, and priority.
6. **Resolved means validated.** Only QA moves an item to *validated_fixed*. A validated item that reappears in a later cycle becomes *regressed* automatically.
7. **Decisions within capacity.** P0/P1 items are approved in score order until the cycle's engineering capacity is used (S=1, M=2, L=3 units; default 8). Items that touch content quality, privacy or consent wording, or the collection of voice data, are marked *awaiting_human_approval* and are never auto-approved.
8. **No code.** The PM writes only PM documents and its own state.

## Scoring

`score = 3·severity + 6·reach·grade_weight + 3·max(0, pre_primary_reach − reach) + 1.5·learning_impact + ux_impact + 2·abandonment_among_affected − 0.7·complexity_cost`

- P0: severity 4 and reach ≥ 15 % (or ≥ 30 % of pre-primary children)
- P1: score ≥ 19, or any severity-4 problem
- P2: score ≥ 14
- P3: the rest

Severity, learning impact, UX impact and complexity per root cause are set in `catalog.py`; reach, grade spread, language spread and abandonment come from the data.

## Acceptance targets

A number is an absolute target. `x0.5` means at most half the baseline (a zero baseline must stay zero). `baseline` means no worse than baseline. Metric definitions live in `agent_org/metrics.py`, and QA computes them the same way.

## Adding a new root cause

Add an entry to `ROOT_CAUSES` with symptom codes (and an optional `match` on evidence), severity and impacts, owners, modules, hypothesis, expected behaviour, technical requirements, acceptance criteria (using metrics from `metrics.py`, or add a metric), validation and scope. Child agents may report new symptom codes at any time, and they will show up as *unclassified* until the PM catalog maps them.

## Run

```bash
python -m agent_org.pm.engine --cycle c01 --label baseline --capacity 8 --publish
```
