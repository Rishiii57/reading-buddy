"""The AI Product Manager: aggregates child reports, finds root causes, prioritises, and writes
technical requirements. It reads runs and writes PM documents and its own state. It never touches
source code (enforced by only writing under agent_org/runs, agent_org/pm/state and docs/agent-org).

    python -m agent_org.pm.engine --cycle c01 --label baseline
    python -m agent_org.pm.engine --cycle c01 --label baseline --capacity 6 --publish

Decisions are deterministic given the inputs. Every number in the output points back to agent ids
and artefact paths, so a human can check any claim.
"""
import argparse
import json
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path

from .. import metrics as M
from ..personas.persona import PRE_PRIMARY, load as load_personas
from .catalog import COMPLEXITY_COST, ROOT_CAUSES

PKG = Path(__file__).resolve().parent.parent
RUNS = PKG / "runs"
STATE = PKG / "pm" / "state"
DOCS = PKG.parent / "docs" / "agent-org"

# a symptom caused by another symptom in the same session belongs to the cause of the first
CONSEQUENCES = {"COULD_NOT_START_SESSION": ["CONSENT_BLOCKS_CHILD"],
                "HARD_TO_RESUME": ["MIC_TAP_PAUSED_SESSION", "BREAK_REQUEST_IGNORED"]}
GRADE_WEIGHT = {"Nursery": 1.5, "LKG": 1.4, "UKG": 1.3, "Class 1": 1.1, "Class 2": 1.0, "Class 3": 1.0, "Class 4": 1.0}


def instances(reports: list[dict]) -> list[dict]:
    out = []
    for r in reports:
        codes = {i["code"] for i in r["experience"]["issues"]}
        for i in r["experience"]["issues"]:
            out.append({"agent": r["agent_id"], "grade": r["persona"]["grade"],
                        "lang": r["persona"]["language_preference"], "outcome": r["outcome"],
                        "code": i["code"], "count": i["count"], "evidence": i.get("evidence", []),
                        "details": i.get("details", []), "quote": i.get("child_quote", ""),
                        "level": i.get("evidence_level"), "co_codes": codes, "dir": r.get("_dir"),
                        "screens": r.get("artefacts", {}).get("screens", [])})
    return out


def assign(insts: list[dict]) -> tuple[dict, list]:
    by_rc = defaultdict(list)
    unclassified = []
    for inst in insts:
        code = inst["code"]
        cause_codes = CONSEQUENCES.get(code, [])
        linked = next((c for c in cause_codes if c in inst["co_codes"]), None)
        effective = linked or code
        placed = False
        for rc in ROOT_CAUSES:
            if effective not in rc["codes"]:
                continue
            match = rc.get("match")
            if match and inst["evidence"]:
                ev = [e for e in inst["evidence"] if match(e)]
                if not ev:
                    continue
                share = len(ev) / len(inst["evidence"])
                by_rc[rc["id"]].append({**inst, "evidence": ev, "count": max(1, round(inst["count"] * share)),
                                        "via": linked})
            else:
                by_rc[rc["id"]].append({**inst, "via": linked})
            placed = True
        if not placed:
            unclassified.append(inst)
    return by_rc, unclassified


def score(rc: dict, items: list[dict], reports: list[dict]) -> dict:
    n = len(reports)
    agents = sorted({i["agent"] for i in items})
    grades = Counter(i["grade"] for i in {i["agent"]: i for i in items}.values())
    langs = Counter(i["lang"] for i in {i["agent"]: i for i in items}.values())
    pre_total = sum(1 for r in reports if r["persona"]["grade"] in PRE_PRIMARY) or 1
    pre_aff = sum(v for g, v in grades.items() if g in PRE_PRIMARY)
    reach = len(agents) / max(1, n)
    pre_reach = pre_aff / pre_total
    affected = [r for r in reports if r["agent_id"] in agents]
    abandon_aff = M.METRICS["abandon_rate"][0](affected) if affected else 0
    weight = statistics.mean(GRADE_WEIGHT[g] for g in grades.elements()) if grades else 1.0
    s = (3 * rc["severity"] + 6 * reach * weight + 3 * max(0.0, pre_reach - reach) + 1.5 * rc["learning_impact"]
         + rc["ux_impact"] + 2 * abandon_aff - 0.7 * COMPLEXITY_COST[rc["complexity"]])
    if rc["severity"] >= 4 and (reach >= 0.15 or pre_reach >= 0.3):
        prio = "P0"
    elif s >= 19 or rc["severity"] >= 4:
        prio = "P1"
    elif s >= 14:
        prio = "P2"
    else:
        prio = "P3"
    return {"agents": agents, "n_agents": len(agents), "instances": sum(i["count"] for i in items),
            "reach": round(reach, 3), "pre_primary_reach": round(pre_reach, 3), "grades": dict(grades),
            "languages": dict(langs), "abandon_rate_affected": round(abandon_aff, 3),
            "grade_weight": round(weight, 2), "score": round(s, 2), "priority": prio}


def load_state() -> dict:
    f = STATE / "backlog.json"
    return json.loads(f.read_text()) if f.exists() else {"items": {}, "cycles": []}


def save_state(state: dict):
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "backlog.json").write_text(json.dumps(state, indent=1, ensure_ascii=False))


def decide(cycle: str, results: list[dict], state: dict, capacity: int) -> list[dict]:
    """Approve within engineering capacity (S=1, M=2, L=3 units), highest priority first."""
    used = 0
    decisions = []
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    for res in sorted(results, key=lambda r: (order[r["priority"]], -r["score"])):
        rc = res["rc"]
        prev = state["items"].get(rc["id"], {})
        prev_status = prev.get("status")
        cost = COMPLEXITY_COST[rc["complexity"]]
        if prev_status == "validated_fixed":
            status, why = "regressed", "QA had validated a fix, but the symptom is back in this cycle."
        elif rc["needs_human"]:
            status, why = "awaiting_human_approval", "Touches content, privacy or model/data collection: needs a human decision."
        elif res["priority"] in ("P0", "P1") and used + cost <= capacity:
            status, why = "approved", f"{res['priority']} within capacity ({used + cost}/{capacity} units)."
            used += cost
        elif res["priority"] in ("P0", "P1"):
            status, why = "deferred", f"{res['priority']} but over this cycle's capacity ({capacity} units)."
        else:
            status, why = "deferred", f"{res['priority']}: below the approval line this cycle."
        if not res.get("testable") and status == "approved":
            status, why = "deferred", "No measurable acceptance criterion yet."
        decisions.append({"rc": rc["id"], "priority": res["priority"], "status": status, "why": why,
                          "previous": prev_status})
    return decisions


def run(cycle: str, label: str, capacity: int, publish: bool, audio: Path | None = None) -> dict:
    run_dir = RUNS / cycle / label
    reports = [r for r in M.load_reports(run_dir) if r.get("outcome") != "harness_error"]
    harness = [r for r in M.load_reports(run_dir) if r.get("outcome") == "harness_error"]
    if not reports:
        raise SystemExit(f"no reports in {run_dir}")
    personas = {p.id: p for p in load_personas()}
    insts = instances(reports)
    by_rc, unclassified = assign(insts)
    results = []
    for rc in ROOT_CAUSES:
        items = by_rc.get(rc["id"])
        if not items:
            continue
        sc = score(rc, items, reports)
        quotes = Counter(i["quote"] for i in items if i["quote"]).most_common(3)
        samples = []
        for i in items[:8]:
            samples.append({"agent": i["agent"], "grade": i["grade"], "lang": i["lang"], "code": i["code"],
                            "detail": i["details"][0] if i["details"] else "", "evidence": i["evidence"][:2],
                            "artefacts": f"{Path(i['dir']).relative_to(PKG.parent)}" if i.get("dir") else None,
                            "via": i.get("via")})
        results.append({"rc": rc, **sc, "quotes": [q for q, _ in quotes], "samples": samples,
                        "codes": dict(Counter(i["code"] for i in items)), "testable": bool(rc["acceptance"])})
    state = load_state()
    decisions = decide(cycle, results, state, capacity)
    dmap = {d["rc"]: d for d in decisions}
    seen = {r["rc"]["id"] for r in results}
    # issues that were open before and did not show up now
    for rc_id, item in state["items"].items():
        if rc_id not in seen and item.get("status") in ("approved", "in_progress", "awaiting_qa", "deferred",
                                                          "awaiting_human_approval", "returned_to_engineering"):
            item.setdefault("history", []).append({"cycle": cycle, "label": label, "event": "not_observed"})
    for res in results:
        rc_id = res["rc"]["id"]
        d = dmap[rc_id]
        item = state["items"].setdefault(rc_id, {"id": rc_id, "title": res["rc"]["title"], "first_seen": f"{cycle}/{label}",
                                                 "history": []})
        # status changes only through PM decisions or QA validation; don't downgrade an in-flight item
        if item.get("status") not in ("in_progress", "awaiting_qa") or d["status"] == "regressed":
            item["status"] = d["status"]
        item["priority"] = res["priority"]
        item["history"].append({"cycle": cycle, "label": label, "priority": res["priority"], "status": item["status"],
                                "agents": res["n_agents"], "instances": res["instances"], "score": res["score"]})
    state["cycles"].append({"cycle": cycle, "label": label, "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                            "agents": len(reports), "root_causes": len(results), "unclassified": len(unclassified)})
    out = {"cycle": cycle, "label": label, "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "agents": len(reports), "harness_errors": [r["agent_id"] for r in harness],
           "metrics": M.compute(reports),
           "by_grade": M.by_group(reports, lambda r: r["persona"]["grade"]),
           "by_language": M.by_group(reports, lambda r: r["persona"]["language_preference"]),
           "outcomes": dict(Counter(r["outcome"] for r in reports)),
           "results": [{**{k: v for k, v in r.items() if k != "rc"}, "rc_id": r["rc"]["id"]} for r in results],
           "decisions": decisions,
           "unclassified": [{"agent": u["agent"], "code": u["code"], "detail": u["details"][:1]} for u in unclassified],
           "audio_eval": json.loads(audio.read_text()) if audio and audio.exists() else None}
    pm_dir = run_dir / "pm"
    pm_dir.mkdir(parents=True, exist_ok=True)
    (pm_dir / "analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
    with open(_mk(STATE) / "decisions.jsonl", "a") as f:
        for d in decisions:
            f.write(json.dumps({"cycle": cycle, "label": label, "at": out["generated"], **d}) + "\n")
    save_state(state)
    from .render import render_all
    render_all(out, results, state, reports, personas, pm_dir, publish)
    return out


def _mk(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", required=True)
    ap.add_argument("--label", default="baseline")
    ap.add_argument("--capacity", type=int, default=8, help="engineering units this cycle (S=1, M=2, L=3)")
    ap.add_argument("--publish", action="store_true", help="also write the PM documents into docs/agent-org/")
    ap.add_argument("--audio", default=str(PKG / "runs" / "audio_eval" / "latest.json"))
    a = ap.parse_args(argv)
    out = run(a.cycle, a.label, a.capacity, a.publish, Path(a.audio))
    print(json.dumps({"agents": out["agents"], "decisions": out["decisions"]}, indent=1))


if __name__ == "__main__":
    main()
