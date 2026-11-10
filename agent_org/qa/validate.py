"""Independent QA: validate one submitted requirement against its acceptance criteria.

    python -m agent_org.qa.validate REQ-STALL-TIMING --cycle c01 [--reps 2] [--max-personas 14]

QA does not take Engineering's word for anything. For each requirement it:
  1. reproduces the original issue: re-runs the affected personas (same seeds, plus extra seeds)
     on the BASE build (a separate worktree at the commit Engineering started from);
  2. runs exactly the same personas and seeds on the CANDIDATE build (the requirement's worktree);
  3. checks every acceptance criterion from the PM requirement on before vs after;
  4. runs regressions: unit tests, the offline tutor replay (base vs candidate) and guard metrics;
  5. writes VALIDATION.md/json and moves the backlog item to validated_fixed or
     returned_to_engineering (with the evidence). Only QA can mark an item validated.

The measuring instrument (child agents, metrics) is the integration branch's code for both builds.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from .. import metrics as M
from ..engineering.workflow import WT_ROOT, record, rc_of, set_status, sh
from ..orchestrator import main as orchestrate
from ..personas.persona import load as load_personas
from ..pm.catalog import ROOT_CAUSES

PKG = Path(__file__).resolve().parent.parent
RUNS = PKG / "runs"
GUARDS = [("completion_rate", ">=", -0.1), ("abandon_rate", "<=", 0.1), ("false_corrections_per_agent", "<=", 0.25),
          ("frustration_peak_mean", "<=", 0.3), ("harness_error_rate", "<=", 0.0)]


def scope_personas(rc: dict, cycle: str, label: str, max_n: int) -> list[str]:
    analysis = json.loads((RUNS / cycle / label / "pm" / "analysis.json").read_text())
    res = next((r for r in analysis["results"] if r["rc_id"] == rc["id"]), None)
    ids = list(res["agents"]) if res else []
    sc = rc.get("scope", {})
    for p in load_personas():
        if sc.get("grades") and p.grade in sc["grades"] or \
           ("grown_up_setup" in sc and p.grown_up_setup == sc["grown_up_setup"]) or \
           ("ui_english_reading_lt" in sc and p.ui_english_reading < sc["ui_english_reading_lt"]):
            if p.id not in ids:
                ids.append(p.id)
    if len(ids) > max_n:  # keep the originally affected ones first, then a spread of the rest
        ids = ids[:max_n]
    return ids


def base_worktree(commit: str) -> Path:
    wt = WT_ROOT / f"qa-base-{commit[:8]}"
    if not wt.exists():
        sh(["git", "worktree", "add", "--detach", str(wt), commit])
    return wt


def run_set(cycle, label, app_root: Path, ids, reps, port, parallel) -> list[dict]:
    reports = []
    for k in range(reps):
        lab = f"{label}-s{k}"
        orchestrate(["--cycle", cycle, "--label", lab, "--ids", ",".join(ids), "--parallel", str(parallel),
                     "--seed-offset", str(1000 * k), "--port", str(port), "--app-root", str(app_root)])
        reports += M.load_reports(RUNS / cycle / lab)
    return reports


def replay_summary(root: Path) -> dict:
    r = subprocess.run([sys.executable, "-c", "import json; from eval.replay import score; from backend.tutor import TutorConfig; "
                        "print(json.dumps(score(TutorConfig())['summary']))"], cwd=root, capture_output=True, text=True)
    return json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else {"error": r.stderr[-300:]}


def frac(s):
    a, b = str(s).split("/")
    return int(a) / max(1, int(b))


def check(op, target, before, after):
    if isinstance(target, str) and target.startswith("x"):
        k = float(target[1:])
        ok = after <= k * before if before > 0 else after <= 0
        return ok, f"{after} {op} {k}×{before} = {round(k * before, 3)}"
    if target == "baseline":
        return after <= before + 1e-9, f"{after} ≤ baseline {before}"
    ok = after <= target if op == "<=" else after >= target
    return ok, f"{after} {op} {target}"


def validate(req: str, cycle: str, label: str, reps: int, max_n: int, parallel: int) -> dict:
    rc = next(r for r in ROOT_CAUSES if r["id"] == rc_of(req))
    rec = record(req)
    if not rec.get("rounds"):
        raise SystemExit(f"{req} has not been submitted")
    rnd = rec["rounds"][-1]
    cand = Path(rec["worktree"])
    base = base_worktree(rec["base_commit"])
    ids = scope_personas(rc, cycle, label, max_n)
    if not ids:
        raise SystemExit("no personas in scope")
    qa_cycle = f"{cycle}/qa/{req}/r{len(rec['rounds'])}"
    t0 = time.monotonic()
    before = run_set(qa_cycle, "before", base, ids, reps, 8801, parallel)
    after = run_set(qa_cycle, "after", cand, ids, reps, 8802, parallel)
    mb, ma = M.compute(before), M.compute(after)
    criteria = []
    for metric, op, target, scope in rc["acceptance"]:
        ok, how = check(op, target, mb[metric], ma[metric])
        criteria.append({"metric": metric, "target": f"{op} {target}", "scope": scope, "before": mb[metric],
                         "after": ma[metric], "pass": ok, "how": how, "reproduced": mb[metric] > 0 if op == "<=" else True})
    guards = []
    for metric, op, tol in GUARDS:
        ok = ma[metric] >= mb[metric] + tol if op == ">=" else ma[metric] <= mb[metric] + tol
        guards.append({"metric": metric, "before": mb[metric], "after": ma[metric], "pass": ok, "rule": f"{op} before{tol:+}"})
    rb, ra = replay_summary(base), replay_summary(cand)
    replay = []
    if "error" not in rb and "error" not in ra:
        for k in ("tracking_pass", "errors_caught", "stalls_prompted"):
            replay.append({"check": k, "before": rb[k], "after": ra[k], "pass": frac(ra[k]) >= frac(rb[k])})
        replay.append({"check": "false_corrections_per_50_words", "before": rb["false_corrections_per_50_words"],
                       "after": ra["false_corrections_per_50_words"],
                       "pass": ra["false_corrections_per_50_words"] <= rb["false_corrections_per_50_words"] + 0.05})
        replay.append({"check": "stall_prompt_s_max (<= 4.0)", "before": rb["stall_prompt_s_max"], "after": ra["stall_prompt_s_max"],
                       "pass": (ra["stall_prompt_s_max"] or 0) <= 4.0})
    else:
        replay.append({"check": "replay ran", "pass": False, "before": rb.get("error"), "after": ra.get("error")})
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=cand, capture_output=True, text=True)
    tests_ok = tests.returncode == 0
    reproduced = any(c["reproduced"] for c in criteria) if criteria else False
    passed = bool(criteria) and all(c["pass"] for c in criteria) and all(g["pass"] for g in guards) \
        and all(r["pass"] for r in replay) and tests_ok
    verdict = "validated_fixed" if passed else "returned_to_engineering"
    out = {"requirement": req, "round": len(rec["rounds"]), "candidate_commit": rnd["commit"], "base_commit": rec["base_commit"],
           "personas": ids, "reps": reps, "agents_before": len(before), "agents_after": len(after),
           "issue_reproduced_on_base": reproduced, "criteria": criteria, "guards": guards, "replay": replay,
           "unit_tests": {"passed": tests_ok, "tail": tests.stdout.strip().splitlines()[-1:]},
           "metrics_before": mb, "metrics_after": ma, "verdict": verdict,
           "wall_s": round(time.monotonic() - t0, 1), "runs": f"agent_org/runs/{qa_cycle}"}
    d = RUNS / qa_cycle
    d.mkdir(parents=True, exist_ok=True)
    (d / "VALIDATION.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    (d / "VALIDATION.md").write_text(render(out, rc), encoding="utf-8")
    set_status(rc["id"], verdict, f"QA round {out['round']}: {verdict} ({sum(c['pass'] for c in criteria)}/{len(criteria)} criteria)")
    rec.setdefault("qa", []).append({"round": out["round"], "verdict": verdict, "report": f"agent_org/runs/{qa_cycle}/VALIDATION.md"})
    from ..engineering.workflow import save_record
    save_record(req, rec)
    return out


def render(o, rc) -> str:
    yes = lambda b: "✅" if b else "❌"
    L = [f"# QA validation: {o['requirement']} (round {o['round']})", "",
         f"**Verdict: {o['verdict']}** · candidate `{o['candidate_commit'][:8]}` vs base `{o['base_commit'][:8]}` · "
         f"{len(o['personas'])} personas × {o['reps']} seeds ({o['agents_after']} sessions per build) · {o['wall_s']} s", "",
         f"Personas: {', '.join(o['personas'])}", "",
         f"Original issue reproduced on base build: {yes(o['issue_reproduced_on_base'])}", "",
         "## Acceptance criteria (from the PM requirement)", "",
         "| Metric | Target | Scope | Before | After | Check | Pass |", "|---|---|---|---|---|---|---|"]
    L += [f"| {c['metric']} | {c['target']} | {c['scope']} | {c['before']} | {c['after']} | {c['how']} | {yes(c['pass'])} |" for c in o["criteria"]]
    if not o["criteria"]:
        L.append("| (none measurable) | | | | | | ❌ |")
    L += ["", "## Regression guards (same personas)", "", "| Metric | Before | After | Rule | Pass |", "|---|---|---|---|---|"]
    L += [f"| {g['metric']} | {g['before']} | {g['after']} | {g['rule']} | {yes(g['pass'])} |" for g in o["guards"]]
    L += ["", "## Offline tutor replay (recorded Prisma transcripts, base vs candidate)", "",
          "| Check | Before | After | Pass |", "|---|---|---|---|"]
    L += [f"| {r['check']} | {r['before']} | {r['after']} | {yes(r['pass'])} |" for r in o["replay"]]
    L += ["", f"Unit tests on candidate: {yes(o['unit_tests']['passed'])} {' '.join(o['unit_tests']['tail'])}", "",
          "## All metrics", "", "| Metric | Before | After |", "|---|---|---|"]
    L += [f"| {k} | {o['metrics_before'][k]} | {o['metrics_after'][k]} |" for k in o["metrics_before"]]
    L += ["", f"Evidence: `{o['runs']}/before-s*/` and `after-s*/` (per-agent reports, traces, server logs)."]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("req")
    ap.add_argument("--cycle", required=True)
    ap.add_argument("--label", default="baseline", help="the PM analysis run the requirement came from")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--max-personas", type=int, default=14)
    ap.add_argument("--parallel", type=int, default=4)
    a = ap.parse_args(argv)
    o = validate(a.req, a.cycle, a.label, a.reps, a.max_personas, a.parallel)
    print(json.dumps({k: o[k] for k in ("requirement", "verdict", "criteria")}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
