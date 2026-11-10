"""Run the repeatable parts of a product cycle, and write the cross-cycle history.

    python -m agent_org.cycle study   --cycle c02 --label retest [--agents 50 --parallel 4]
        user study (orchestrator) -> audio evaluation -> Product Manager (published)
    python -m agent_org.cycle history
        PRODUCT_IMPROVEMENT_HISTORY.md from every PM analysis, QA validation and change record

Engineering (implementing approved requirements) and QA (`agent_org.qa.validate`) sit between two
studies; see ENGINEERING_WORKFLOW.md and QA_WORKFLOW.md.
"""
import argparse
import json
from pathlib import Path

from . import metrics as M
from .personas.persona import GRADES

PKG = Path(__file__).resolve().parent
RUNS = PKG / "runs"
DOCS = PKG.parent / "docs" / "agent-org"
LANG = {"en-IN": "English", "hi-IN": "Hindi", "gu-IN": "Gujarati"}
USABILITY = ["session_start_rate", "abandon_rate", "mic_tap_pause_rate", "spoken_guidance_gap_rate", "consent_blocked_rate",
             "unheard_words_per_agent", "long_talk_rate", "intro_s_median", "frustration_peak_mean"]
LEARNING = ["completion_rate", "coverage", "interruptions_per_agent", "stall_interruptions_per_agent",
            "correction_interruptions_per_agent", "drill_repeat_rate", "false_corrections_per_agent",
            "missed_errors_per_agent", "stuck_rate"]


def study(cycle, label, agents, parallel, capacity):
    from .audio_eval.run import main as audio
    from .orchestrator import main as orchestrate
    from .pm.engine import run as pm
    orchestrate(["--cycle", cycle, "--label", label, "--agents", str(agents), "--parallel", str(parallel)])
    audio(["--label", f"{cycle}-{label}"])
    pm(cycle, label, capacity, True, RUNS / "audio_eval" / "latest.json")
    history()


def _analyses():
    state = json.loads((PKG / "pm" / "state" / "backlog.json").read_text())
    out = []
    for c in state["cycles"]:
        f = RUNS / c["cycle"] / c["label"] / "pm" / "analysis.json"
        if f.exists():
            out.append(json.loads(f.read_text()))
    return state, out


def _delta(a, b, k, lower_better):
    x, y = a.get(k), b.get(k)
    if x is None or y is None:
        return "-"
    d = round(y - x, 3)
    better = (d < 0) if lower_better else (d > 0)
    mark = "▲ better" if better and d else ("▼ worse" if d else "=")
    return f"{x} → {y} ({d:+}) {mark}"


def history():
    state, analyses = _analyses()
    L = ["# Product improvement history", "",
         "Written by `python -m agent_org.cycle history` from the PM analyses, QA validations and engineering change records. "
         "Each cycle is a full user study (simulated children on the real app); fixes between cycles are only counted when QA "
         "validated them.", ""]
    for i, a in enumerate(analyses):
        cur = {r["rc_id"]: r for r in a["results"]}
        L += [f"## {a['cycle']} / {a['label']} ({a['generated']}, {a['agents']} children)", ""]
        if i == 0:
            L += ["Baseline. Problems found: " + ", ".join(f"{r['priority']} {r['rc_id']}" for r in a["results"]) + ".", ""]
        else:
            prev = analyses[i - 1]
            pr = {r["rc_id"]: r for r in prev["results"]}
            items = state["items"]
            new = [k for k in cur if k not in pr]
            still = [k for k in cur if k in pr]
            gone = [k for k in pr if k not in cur]
            fixed = [k for k in gone if items.get(k, {}).get("status") == "validated_fixed"
                     or any(h.get("event") == "validated_fixed" for h in items.get(k, {}).get("history", []))]
            validated = [k for k in cur if any(h.get("event") == "validated_fixed" for h in items.get(k, {}).get("history", []))]
            regressed = [k for k in validated if k in pr and cur[k]["n_agents"] >= pr[k]["n_agents"]]
            residual = [k for k in validated if k not in regressed]
            L += [f"- **Newly discovered:** {', '.join(new) or 'none'}",
                  "- **Still unresolved:** " + (", ".join(f"{k} ({pr[k]['n_agents']}→{cur[k]['n_agents']} children)" for k in still) or "none"),
                  f"- **Successfully fixed (QA-validated, not observed now):** {', '.join(fixed) or 'none'}",
                  f"- **Not observed now but not validated:** {', '.join(k for k in gone if k not in fixed) or 'none'}",
                  "- **Fixed with residual cases (QA-validated, fewer children affected):** "
                  + (", ".join(f"{k} ({pr[k]['n_agents']}→{cur[k]['n_agents']})" for k in residual if k in pr) or "none"),
                  "- **Regressions (validated earlier, no fewer children affected now):** " + (", ".join(f"{k} ({cur[k]['n_agents']} children)" for k in regressed) or "none"), ""]
            for title, keys in (("Usability", USABILITY), ("Learning experience", LEARNING)):
                L += [f"### {title}", "", "| Metric | Previous → now |", "|---|---|"]
                L += [f"| {k} | {_delta(prev['metrics'], a['metrics'], k, M.METRICS[k][1])} |" for k in keys]
                L.append("")
            L += ["### By grade (completion, coverage, interruptions/agent, peak frustration)", "",
                  "| Grade | Completion | Coverage | Interruptions/agent | Peak frustration |", "|---|---|---|---|---|"]
            for g in GRADES:
                p, c = prev["by_grade"].get(g), a["by_grade"].get(g)
                if p and c:
                    L.append(f"| {g} | {_delta(p, c, 'completion_rate', False)} | {_delta(p, c, 'coverage', False)} | "
                             f"{_delta(p, c, 'interruptions_per_agent', True)} | {_delta(p, c, 'frustration_peak_mean', True)} |")
            L += ["", "### By language", "", "| Language | Completion | Coverage | False corr./agent | Wrong language |", "|---|---|---|---|---|"]
            for k in LANG:
                p, c = prev["by_language"].get(k), a["by_language"].get(k)
                if p and c:
                    L.append(f"| {LANG[k]} | {_delta(p, c, 'completion_rate', False)} | {_delta(p, c, 'coverage', False)} | "
                             f"{_delta(p, c, 'false_corrections_per_agent', True)} | {_delta(p, c, 'wrong_language_rate', True)} |")
            L.append("")
        qa = sorted((RUNS / a["cycle"] / "qa").glob("*/r*/VALIDATION.json")) if (RUNS / a["cycle"] / "qa").exists() else []
        if qa:
            L += ["### Engineering and QA after this study", "", "| Requirement | Round | Verdict | Criteria | Files changed |", "|---|---|---|---|---|"]
            for f in qa:
                v = json.loads(f.read_text())
                ch = json.loads((PKG / "engineering" / "changes" / f"{v['requirement']}.json").read_text())
                files = next((r["files"] for r in ch["rounds"] if r["commit"] == v["candidate_commit"]), [])
                crit = "; ".join(f"{c['metric']} {c['before']}→{c['after']} {'✅' if c['pass'] else '❌'}" for c in v["criteria"])
                L.append(f"| {v['requirement']} | {v['round']} | **{v['verdict']}** | {crit} | {', '.join(files)} |")
            L.append("")
    L += ["## Backlog now", ""] + [f"- {i['id']}: {i.get('status')} ({i.get('priority')})" for i in state["items"].values()]
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "PRODUCT_IMPROVEMENT_HISTORY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(DOCS / "PRODUCT_IMPROVEMENT_HISTORY.md")


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("study")
    s.add_argument("--cycle", required=True); s.add_argument("--label", default="baseline")
    s.add_argument("--agents", type=int, default=50); s.add_argument("--parallel", type=int, default=4)
    s.add_argument("--capacity", type=int, default=8)
    sub.add_parser("history")
    a = ap.parse_args(argv)
    if a.cmd == "study":
        study(a.cycle, a.label, a.agents, a.parallel, a.capacity)
    else:
        history()


if __name__ == "__main__":
    main()
