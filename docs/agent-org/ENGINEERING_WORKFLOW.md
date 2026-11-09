# Engineering workflow

The Engineering team implements **approved** requirements from `PRODUCT_REQUIREMENTS.md`. It does not invent features or change product direction. If it disagrees with a requirement, it records that in the change record, and the PM decides.

## Roles and ownership

| Role | Owns (see `agent_org/engineering/ownership.json`) |
|---|---|
| AI/ML Engineer | tutor decision logic and thresholds (`backend/tutor.py`), aligner tuning, `eval/`, audio evaluation |
| Speech AI Engineer | STT/TTS integration (`backend/gnani.py`), Buddy's phrases (`backend/phrases.py`), clip pre-generation, STT aliases |
| NLP Engineer | normalisation (`backend/normalize.py`), alignment (`backend/aligner.py`), Hindi/Gujarati handling, break vocabulary |
| Backend Engineer | session handling (`backend/main.py`), tutor state machine, tests |
| Frontend Engineer | everything in `frontend/`: interaction, accessibility, audio controls, reading experience |
| Data Engineer | `content/`, audio assets in `cache/`, test sets |
| Integration Engineer | dependencies, Docker/Render config, API compatibility, deployment readiness (deploys need human approval) |

At submit time, a change that touches files outside its owning roles' areas is flagged for review. `.env` can never be committed.

## Per requirement

```bash
# 1. read the requirement and confirm it is approved
python -m agent_org.engineering.workflow status
# 2. isolated branch + worktree (refuses unapproved requirements)
python -m agent_org.engineering.workflow start REQ-STALL-TIMING --role "Backend Engineer"
#    -> ../rb-worktrees/REQ-STALL-TIMING  on branch eng/REQ-STALL-TIMING
# 3. inspect code, confirm the technical root cause (write it down), implement, add unit tests
# 4. submit: commits, runs pytest + offline tutor replay in the worktree, records files and results
python -m agent_org.engineering.workflow submit REQ-STALL-TIMING \
    --summary "adaptive mid-line stall threshold" --root-cause "fixed 2.0 s stall_mid_s..."
#    -> backlog status awaiting_qa; record in agent_org/engineering/changes/REQ-STALL-TIMING.json
# 5. QA validates independently (see QA_WORKFLOW.md); if returned, fix in the same worktree and submit again
# 6. after QA validation only:
python -m agent_org.engineering.workflow merge REQ-STALL-TIMING   # local merge, never push/deploy
```

## Rules

- One requirement, one branch, one worktree, so parallel engineers never edit the same checkout.
- Fix the root cause the PM described, or document why the real cause differs and fix that.
- Every behaviour change comes with a unit test (`tests/`) and must keep `python -m eval.replay` from regressing.
- Configuration over rewrites: extend `TutorConfig` and existing functions; don't replace working modules.
- Major architecture changes, content in Hindi/Gujarati (native-speaker review), privacy and consent wording, and voice-data collection need human approval before merge.
- Nothing is pushed or deployed by agents. The human pushes when ready.
