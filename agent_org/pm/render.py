"""PM documents, written from the analysis. Plain Markdown so they diff well across cycles."""
import json
import statistics
from collections import Counter
from pathlib import Path

from ..personas.persona import GRADES
from .catalog import ROOT_CAUSES

DOCS = Path(__file__).resolve().parent.parent.parent / "docs" / "agent-org"
RC = {rc["id"]: rc for rc in ROOT_CAUSES}
LANG = {"en-IN": "English", "hi-IN": "Hindi", "gu-IN": "Gujarati"}
PRETTY = {
    "session_start_rate": "Started a session", "completion_rate": "Finished the text", "abandon_rate": "Abandoned / failed",
    "coverage": "Text covered", "interruptions_per_agent": "Interruptions / agent", "mic_tap_pause_rate": "Mic tap paused",
    "unheard_words_per_agent": "Unheard words / agent", "false_corrections_per_agent": "False corrections / agent",
    "missed_errors_per_agent": "Missed errors / agent", "frustration_peak_mean": "Mean peak frustration",
}


def target_text(op, val, base):
    if isinstance(val, str) and val.startswith("x"):
        return f"{op} {val[1:]} × baseline"
    if val == "baseline":
        return f"{op} baseline (no worse)"
    return f"{op} {val}"


def req_id(rc_id: str) -> str:
    return "REQ-" + rc_id[3:]


def pct(x):
    return f"{round(100 * x)}%"


def _table(rows, head):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def research(out, results, reports) -> str:
    n = out["agents"]
    m = out["metrics"]
    started = round(m["session_start_rate"] * n)
    L = [f"# User research report: cycle {out['cycle']} / {out['label']}", "",
         f"Generated {out['generated']} by the AI Product Manager from {n} simulated child sessions run against the real "
         "app (Playwright + real tutor engine; simulated speech channel, no credits). "
         "Simulated satisfaction is **not** speech-recognition accuracy: see the separate audio section.", "",
         "## At a glance", "",
         _table([["Agents executed", n], ["Got a reading session going", f"{started} ({pct(m['session_start_rate'])})"],
                 ["Finished the text", f"{round(m['completion_rate'] * n)} ({pct(m['completion_rate'])})"],
                 ["Abandoned, could not start, or left", f"{round(m['abandon_rate'] * n)} ({pct(m['abandon_rate'])})"],
                 ["Harness errors (excluded)", len(out["harness_errors"])],
                 ["Distinct problems (root causes)", len(results)],
                 ["Unclassified symptoms", len(out["unclassified"])]], ["", ""]), "",
         "Outcomes: " + ", ".join(f"{k} {v}" for k, v in sorted(out["outcomes"].items(), key=lambda x: -x[1])), "",
         "## Top problems (by priority)", ""]
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    for r in sorted(results, key=lambda r: (order[r["priority"]], -r["score"]))[:10]:
        rc = r["rc"]
        L.append(f"- **{r['priority']} {rc['title']}** ({req_id(rc['id'])}): {r['n_agents']}/{n} children "
                 f"({pct(r['reach'])}), pre-primary reach {pct(r['pre_primary_reach'])}. "
                 + (f"“{r['quotes'][0]}”" if r["quotes"] else ""))
    L += ["", "## Grade-wise findings", "",
          _table([[g, d["n"], pct(d["session_start_rate"]), pct(d["completion_rate"]), pct(d["abandon_rate"]),
                   pct(d["coverage"]), d["interruptions_per_agent"], d["frustration_peak_mean"]]
                  for g, d in sorted(out["by_grade"].items(), key=lambda x: GRADES.index(x[0]))],
                 ["Grade", "n", "Started", "Finished", "Abandoned", "Covered", "Interruptions/agent", "Peak frustration"]), ""]
    for g in GRADES:
        aff = [r for r in results if r["grades"].get(g)]
        if aff:
            top = sorted(aff, key=lambda r: -r["grades"][g])[:3]
            L.append(f"- **{g}**: " + "; ".join(f"{r['rc']['title']} ({r['grades'][g]})" for r in top))
    L += ["", "## Language-wise findings", "",
          _table([[LANG[k], d["n"], pct(d["session_start_rate"]), pct(d["completion_rate"]), pct(d["coverage"]),
                   d["false_corrections_per_agent"], d["missed_errors_per_agent"], pct(d["wrong_language_rate"])]
                  for k, d in out["by_language"].items()],
                 ["Language", "n", "Started", "Finished", "Covered", "False corr./agent", "Missed errors/agent", "Wrong language"]), ""]
    for lang in LANG:
        aff = [r for r in results if r["languages"].get(lang)]
        if aff:
            top = sorted(aff, key=lambda r: -r["languages"][lang])[:3]
            L.append(f"- **{LANG[lang]}**: " + "; ".join(f"{r['rc']['title']} ({r['languages'][lang]})" for r in top))
    pos = Counter(p for r in reports for p in r["experience"]["positives"])
    L += ["", "## What children liked", ""] + [f"- “{p}” ({c})" for p, c in pos.most_common(6)]
    if not pos:
        L.append("- Nothing positive was recorded this cycle.")
    if out["unclassified"]:
        L += ["", "## Unclassified symptoms (kept for review)", ""]
        L += [f"- {u['agent']}: {u['code']} {u['detail'][0] if u['detail'] else ''}" for u in out["unclassified"][:20]]
    L += ["", "## Speech and audio evaluation (measured, separate from simulated satisfaction)", ""]
    a = out.get("audio_eval")
    if a:
        L.append(_table([[LANG.get(k, k), v.get("wer_clean"), v.get("false_correction_per_50"), v.get("missed_error_rate"),
                          v.get("alignment_accuracy"), v.get("latency_ms_median")] for k, v in a.get("by_language", {}).items()],
                        ["Language", "WER (clean)", "False corr./50 words", "Missed error rate", "Alignment acc.", "Latency ms"]))
        L += ["", a.get("headline", "")]
    else:
        L.append("No audio evaluation report found for this cycle (run `python -m agent_org.audio_eval`).")
    L += ["", "## Method and limits", "",
          "- Children are deterministic persona policies (seeded), not LLMs; they perceive only the screen and Buddy's voice.",
          "- Speech is simulated: reading errors come from the persona; recognition errors from a coarse per-language model "
          "(measured adult-TTS WER + an assumed child-voice penalty). Findings that depend on real child speech are marked for "
          "the audio evaluation.",
          "- Uncached Buddy lines play as timed placeholder audio (no Timbre calls); timing is realistic, sound is not.",
          f"- Evidence for every claim: `agent_org/runs/{out['cycle']}/{out['label']}/<agent>/` (report, trace, screenshots, server log)."]
    return "\n".join(L) + "\n"


def journeys(out, reports) -> str:
    n = len(reports)
    steps = [("Opened the app", lambda r: True),
             ("Reached a text", lambda r: bool(r.get("text"))),
             ("Started a session", lambda r: (r["metrics"].get("intro_s") is not None) or bool(r["metrics"].get("session_s"))),
             ("Said a first word", lambda r: r["metrics"].get("time_to_first_word_s") is not None),
             ("Covered half the text", lambda r: ((r.get("tutor_summary") or {}).get("words_read", 0) + (r.get("tutor_summary") or {}).get("words_helped", 0)) >= 0.5 * max(1, r["metrics"].get("words_total") or 1)),
             ("Finished", lambda r: r["outcome"] == "completed")]
    L = [f"# User journey analysis: cycle {out['cycle']} / {out['label']}", "", "## Funnel", ""]
    rows = []
    for name, f in steps:
        row = [name, f"{sum(1 for r in reports if f(r))}/{n}"]
        for g in GRADES:
            sub = [r for r in reports if r["persona"]["grade"] == g]
            row.append(f"{sum(1 for r in sub if f(r))}/{len(sub)}" if sub else "-")
        rows.append(row)
    L.append(_table(rows, ["Step", "All"] + GRADES))
    def med(key):
        v = [r["metrics"].get(key) for r in reports if r["metrics"].get(key) is not None]
        return round(statistics.median(v), 1) if v else "-"
    L += ["", "## Timing (median seconds)", "",
          _table([["Home → text", med("time_to_text_s")], ["Mic tap → child's first turn (Buddy intro)", med("intro_s")],
                  ["Session length", med("session_s")], ["Listen first", med("listen_first_s")]], ["", "s"]), "",
          "## Journeys by objective", ""]
    by_j = {}
    for r in reports:
        by_j.setdefault(r["persona"]["journey"], []).append(r)
    L.append(_table([[j, len(rs), ", ".join(f"{k} {v}" for k, v in Counter(r["outcome"] for r in rs).most_common())]
                     for j, rs in sorted(by_j.items())], ["Journey", "n", "Outcomes"]))
    L += ["", "## Where children dropped out", ""]
    drop = Counter()
    for r in reports:
        if r["outcome"] != "completed":
            first = next((i["code"] for i in r["experience"]["issues"] if i.get("child_severity") == "blocked"), None)
            drop[(r["outcome"], first or (r["experience"]["issues"][-1]["code"] if r["experience"]["issues"] else "-"))] += 1
    L.append(_table([[o, c, v] for (o, c), v in drop.most_common()], ["Outcome", "Main symptom", "Agents"]))
    L += ["", "## Individual journeys (abridged)", ""]
    for r in reports:
        iss = ", ".join(f"{i['code']}×{i['count']}" for i in r["experience"]["issues"][:5]) or "no problems"
        L.append(f"- **{r['agent_id']}** {r['persona']['grade']} {LANG[r['persona']['language_preference']]}, "
                 f"{r['persona']['journey']} → *{r['outcome']}*; text: {(r.get('text') or {}).get('title', '-')} "
                 f"({(r.get('text') or {}).get('grade_tag', '')}); {iss}")
    return "\n".join(L) + "\n"


def requirements(out, results) -> str:
    n = out["agents"]
    dmap = {d["rc"]: d for d in out["decisions"]}
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    L = [f"# Product requirements: cycle {out['cycle']} / {out['label']}", "",
         "Written by the AI Product Manager for the Engineering team. Status *approved* means Engineering may start; "
         "*awaiting_human_approval* needs a team decision first; *deferred* is not in this cycle. "
         "An item is resolved only when QA validates its acceptance criteria (not when code changes).", ""]
    for r in sorted(results, key=lambda r: (order[r["priority"]], -r["score"])):
        rc, d = r["rc"], dmap[r["rc"]["id"]]
        L += [f"## {req_id(rc['id'])}: {rc['title']}", "",
              f"**Priority:** {r['priority']} (score {r['score']}) · **Status:** {d['status']} ({d['why']}) · "
              f"**Owners:** {', '.join(rc['owners'])} · **Complexity:** {rc['complexity']}", "",
              "1. **Problem statement.** " + rc["title"] + f". Seen in {r['n_agents']} of {n} simulated children "
              f"({pct(r['reach'])}; pre-primary reach {pct(r['pre_primary_reach'])}), {r['instances']} occurrences; "
              f"{pct(r['abandon_rate_affected'])} of affected children abandoned or could not start.",
              "2. **Affected personas.** " + ", ".join(r["agents"]) + " · by grade: "
              + ", ".join(f"{g} {c}" for g, c in sorted(r["grades"].items(), key=lambda x: GRADES.index(x[0])))
              + " · by language: " + ", ".join(f"{LANG[k]} {v}" for k, v in r["languages"].items()),
              "3. **Supporting evidence.** Symptoms: " + ", ".join(f"{k}×{v}" for k, v in r["codes"].items()) + ". "
              + (" Children said: " + " / ".join(f"“{q}”" for q in r["quotes"]) if r["quotes"] else "")]
        for s in r["samples"][:4]:
            ev = json.dumps(s["evidence"][0], ensure_ascii=False) if s["evidence"] else ""
            L.append(f"   - {s['agent']} ({s['grade']}, {LANG[s['lang']]}): {s['detail']} {ev[:220]}"
                     + (f" (follows {s['via']})" if s.get("via") else "") + f" · `{s['artefacts']}`")
        L += ["4. **Root-cause hypothesis.** " + rc["hypothesis"],
              "5. **Expected behaviour.** " + rc["expected"],
              "6. **Technical implementation requirements.** Modules: " + ", ".join(f"`{m}`" for m in rc["modules"])]
        L += [f"   - {t}" for t in rc["tech"]]
        L.append("7. **Acceptance criteria.**")
        if rc["acceptance"]:
            for metric, op, val, scope in rc["acceptance"]:
                base = out["metrics"].get(metric)
                tgt = target_text(op, val, base)
                L.append(f"   - `{metric}` {tgt}; scope: {scope}. Baseline this cycle: {base}.")
        else:
            L.append("   - None measurable by the simulation yet; needs the method in 8.")
        L += ["   - No regressions: `pytest` green; `python -m eval.replay` tracking, catches and false corrections not worse than baseline.",
              "8. **Validation methodology.** " + rc["validation"]
              + " QA re-runs the affected personas with the same seeds on the baseline and candidate builds and compares.",
              f"9. **Priority.** {r['priority']}", ""]
    return "\n".join(L) + "\n"


def prioritisation(out, results) -> str:
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    rows = []
    for r in sorted(results, key=lambda r: (order[r["priority"]], -r["score"])):
        rc = r["rc"]
        rows.append([r["priority"], req_id(rc["id"]), rc["title"][:60], rc["severity"], f"{r['n_agents']} ({pct(r['reach'])})",
                     pct(r["pre_primary_reach"]), r["grade_weight"], len(r["languages"]), rc["learning_impact"], rc["ux_impact"],
                     pct(r["abandon_rate_affected"]), rc["complexity"], r["score"]])
    dec = Counter(d["status"] for d in out["decisions"])
    L = [f"# Prioritisation report: cycle {out['cycle']} / {out['label']}", "",
         "## Method", "",
         "score = 3·severity + 6·reach·grade_weight + 3·max(0, pre-primary reach − reach) + 1.5·learning impact + UX impact "
         "+ 2·abandonment among affected − 0.7·complexity cost (S 1, M 2, L 3).", "",
         "- **P0**: severity 4 (blocks reading or privacy risk) and reach ≥ 15 % overall or ≥ 30 % of pre-primary children.",
         "- **P1**: score ≥ 19, or any severity-4 problem regardless of how many children hit it (small groups are not dropped).",
         "- **P2**: score ≥ 14. **P3**: the rest.",
         "- Grade weights (Nursery 1.5, LKG 1.4, UKG 1.3, Class 1 1.1, others 1.0) make a problem that hits the youngest count more.",
         "- Approval: P0/P1 in order of score until engineering capacity is used; items touching content, privacy, or data "
         "collection always need human approval.", "",
         "## Scores", "",
         _table(rows, ["P", "Req", "Problem", "Sev", "Children", "Pre-primary", "Grade wt", "Langs", "Learning", "UX",
                       "Abandon (affected)", "Cplx", "Score"]), "",
         "## Decisions this cycle", "", ", ".join(f"{k}: {v}" for k, v in dec.items()), ""]
    L += [f"- {req_id(d['rc'])} **{d['status']}**: {d['why']}" + (f" (was {d['previous']})" if d.get("previous") else "")
          for d in out["decisions"]]
    return "\n".join(L) + "\n"


def backlog(state) -> str:
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    items = sorted(state["items"].values(), key=lambda i: (i.get("status") == "validated_fixed", order.get(i.get("priority"), 9)))
    L = ["# Product backlog", "", "Maintained by the AI Product Manager across cycles. Status flow: "
         "deferred / awaiting_human_approval / approved → in_progress → awaiting_qa → validated_fixed "
         "(or returned_to_engineering). A validated item that reappears becomes *regressed*.", "",
         _table([[req_id(i["id"]), i["title"][:70], i.get("priority"), i.get("status"), i.get("first_seen"),
                  " → ".join(f"{h.get('label') or h.get('event', '?')}:{h.get('agents', '-')}" for h in i.get("history", [])[-4:])]
                 for i in items], ["Req", "Problem", "P", "Status", "First seen", "Recent history (run:children)"]), "",
         "## Unresolved problems", ""]
    L += [f"- {req_id(i['id'])} {i['title']} ({i.get('status')})" for i in items
          if i.get("status") not in ("validated_fixed",)]
    L += ["", "## Cycles", ""] + [f"- {c['cycle']}/{c['label']} at {c['at']}: {c['agents']} children, "
                                  f"{c['root_causes']} root causes, {c['unclassified']} unclassified" for c in state["cycles"]]
    return "\n".join(L) + "\n"


def render_all(out, results, state, reports, personas, pm_dir: Path, publish: bool):
    docs = {"USER_RESEARCH_REPORT.md": research(out, results, reports),
            "USER_JOURNEY_ANALYSIS.md": journeys(out, reports),
            "PRODUCT_REQUIREMENTS.md": requirements(out, results),
            "PRIORITISATION_REPORT.md": prioritisation(out, results),
            "PRODUCT_BACKLOG.md": backlog(state)}
    for name, text in docs.items():
        (pm_dir / name).write_text(text, encoding="utf-8")
        if publish:
            DOCS.mkdir(parents=True, exist_ok=True)
            (DOCS / name).write_text(text, encoding="utf-8")
