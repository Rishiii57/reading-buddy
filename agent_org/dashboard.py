"""A one-file HTML dashboard of the whole process (python -m agent_org.dashboard).

Reads only files the system already writes (run.json/status.json/ledger.json, PM analyses and
backlog, QA validations, change records, audio evaluation) and writes agent_org/runs/dashboard.html.
Open it in a browser; it has no external dependencies.
"""
import html
import json
from pathlib import Path

PKG = Path(__file__).resolve().parent
RUNS = PKG / "runs"
OUT = RUNS / "dashboard.html"
KEY = ["session_start_rate", "completion_rate", "abandon_rate", "coverage", "interruptions_per_agent",
       "mic_tap_pause_rate", "unheard_words_per_agent", "false_corrections_per_agent", "frustration_peak_mean", "intro_s_median"]
LOWER = {"abandon_rate", "interruptions_per_agent", "mic_tap_pause_rate", "unheard_words_per_agent",
         "false_corrections_per_agent", "frustration_peak_mean", "intro_s_median"}


def e(x):
    return html.escape(str(x))


def table(head, rows, cls=""):
    return (f'<table class="{cls}"><thead><tr>' + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table>")


def build() -> Path:
    state = json.loads((PKG / "pm" / "state" / "backlog.json").read_text()) if (PKG / "pm" / "state" / "backlog.json").exists() else {"items": {}, "cycles": []}
    studies = []
    for c in state["cycles"]:
        d = RUNS / c["cycle"] / c["label"]
        a = d / "pm" / "analysis.json"
        if a.exists():
            studies.append((c, json.loads(a.read_text()), json.loads((d / "run.json").read_text()) if (d / "run.json").exists() else {}))
    parts = ['<header><h1>Reading Buddy · AI product organisation</h1><p class="sub">Simulated children on the real app → '
             'Product Manager → Engineering → independent QA → re-test. Generated from files in <code>agent_org/runs</code>.</p></header>']
    # cards: latest study
    if studies:
        c, a, run = studies[-1]
        m = a["metrics"]
        prev = studies[-2][1]["metrics"] if len(studies) > 1 else None
        cards = []
        for k in ["session_start_rate", "completion_rate", "abandon_rate", "interruptions_per_agent", "frustration_peak_mean"]:
            delta = ""
            if prev is not None:
                d = round(m[k] - prev[k], 3)
                good = (d < 0) if k in LOWER else (d > 0)
                delta = f'<span class="{"good" if good else "bad" if d else ""}">{d:+}</span>'
            cards.append(f'<div class="card"><div class="k">{e(k.replace("_", " "))}</div><div class="v">{e(m[k])}</div>{delta}</div>')
        parts.append(f'<h2>Latest study: {e(c["cycle"])} / {e(c["label"])}</h2><p>{a["agents"]} children · app '
                     f'<code>{e(run.get("app_commit", "?"))}</code> · {e(a["generated"])}</p><div class="cards">{"".join(cards)}</div>')
    # like-for-like comparison: original build re-measured with the final agents vs the improved build
    fair = [(RUNS / "c01" / "baseline-v2", "original app (re-measured)"), (RUNS / "c02" / "retest", "improved app")]
    if all((d / "run.json").exists() for d, _ in fair):
        from . import metrics as M
        ms = [M.compute([r for r in M.load_reports(d) if r["outcome"] != "harness_error"]) for d, _ in fair]
        commits = [json.loads((d / "run.json").read_text()).get("app_commit", "") for d, _ in fair]
        rows = []
        for k in KEY + ["level_mismatch_rate", "spoken_guidance_gap_rate", "missed_errors_per_agent"]:
            d = round(ms[1][k] - ms[0][k], 3)
            good = (d < 0) if (k in LOWER or k in ("level_mismatch_rate", "spoken_guidance_gap_rate", "missed_errors_per_agent")) else (d > 0)
            rows.append([e(k.replace("_", " ")), e(ms[0][k]), e(ms[1][k]),
                         f'<span class="{"good" if good else "bad" if d else ""}">{d:+}</span>'])
        parts.append(f"<h2>Before → after (same 50 children, same seeds, same agents)</h2><p>Original <code>{e(commits[0])}</code> "
                     f"vs improved <code>{e(commits[1])}</code>. Full write-up: <code>docs/agent-org/AGENT_EVALUATION_REPORT.md</code>.</p>"
                     + table(["Measure", "Original", "Improved", "Change"], rows))
    # studies table
    rows = []
    for c, a, run in studies:
        led = (run.get("summary") or {}).get("ledger", {})
        rows.append([e(f'{c["cycle"]}/{c["label"]}'), e(run.get("app_commit", "")), a["agents"]]
                    + [e(a["metrics"][k]) for k in KEY]
                    + [e(led.get("wall_s", "")), e(led.get("gnani_credits", "")), e(led.get("llm_tokens", ""))])
    parts.append("<h2>User studies</h2>" + table(["Run", "App", "Children"] + [k.replace("_", " ") for k in KEY]
                                                 + ["Wall s", "Gnani credits", "LLM tokens"], rows))
    # backlog
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    items = sorted(state["items"].values(), key=lambda i: order.get(i.get("priority"), 9))
    rows = [[f'<span class="p {e(i.get("priority"))}">{e(i.get("priority"))}</span>', e("REQ-" + i["id"][3:]), e(i["title"]),
             f'<span class="st {e(i.get("status"))}">{e(i.get("status"))}</span>',
             e(" → ".join(f'{h.get("label", h.get("event", ""))}:{h.get("agents", "")}' for h in i.get("history", [])[-5:]))] for i in items]
    parts.append("<h2>Backlog</h2>" + table(["P", "Requirement", "Problem", "Status", "History"], rows))
    # engineering + QA
    rows = []
    for f in sorted((PKG / "engineering" / "changes").glob("REQ-*.json")):
        ch = json.loads(f.read_text())
        last = ch["rounds"][-1] if ch.get("rounds") else {}
        qa = ch.get("qa", [])
        rows.append([e(ch["requirement"]), e(ch.get("role", "")), e(len(ch.get("rounds", []))),
                     e(", ".join(last.get("files", []))), e("✅" if last.get("tests", {}).get("passed") else "❌"),
                     e(qa[-1]["verdict"] if qa else "awaiting QA"), e(qa[-1]["report"] if qa else ""),
                     e("merged " + ch["merged"]["commit"][:8] if ch.get("merged") else "")])
    parts.append("<h2>Engineering and QA</h2>" + table(["Requirement", "Role", "Rounds", "Files", "Unit tests", "QA verdict",
                                                         "Validation report", "Merge"], rows))
    # QA details
    for f in sorted(RUNS.glob("*/qa/*/r*/VALIDATION.json")):
        v = json.loads(f.read_text())
        rows = [[e(c["metric"]), e(c["target"]), e(c["before"]), e(c["after"]), "✅" if c["pass"] else "❌"] for c in v["criteria"]]
        rows += [[e("guard: " + g["metric"]), e(g["rule"]), e(g["before"]), e(g["after"]), "✅" if g["pass"] else "❌"] for g in v["guards"]]
        rows += [[e("replay: " + r["check"]), "", e(r["before"]), e(r["after"]), "✅" if r["pass"] else "❌"] for r in v["replay"]]
        parts.append(f'<details><summary>QA {e(v["requirement"])} round {v["round"]}: <b>{e(v["verdict"])}</b></summary>'
                     + table(["Check", "Target", "Before", "After", "Pass"], rows) + "</details>")
    # audio
    ae = RUNS / "audio_eval" / "latest.json"
    if ae.exists():
        a = json.loads(ae.read_text())
        rows = [[e(k), e(v["wer_clean"]), e(v["wer_by_condition"].get("noise+hesitation")), e(v["alignment_accuracy"]),
                 e(v["alignment_accuracy_noisy"]), e(v["missed_error_rate"]), e(v["false_correction_per_50"]), e(v["latency_ms_median"])]
                for k, v in a["by_language"].items()]
        p25 = {k: d.get("pause_2.5", {}).get("pause_interruption_rate") for k, d in a["part_b"].items()}
        parts.append(f'<h2>Speech and audio evaluation ({e(a["label"])})</h2><p>{e(a["headline"])}</p>'
                     + table(["Language", "WER clean", "WER noise+hes.", "Alignment", "Alignment noisy", "Missed errors",
                              "False corr./50", "Latency ms"], rows)
                     + f"<p>Text-level: 2.5 s mid-line pause interrupted: {e(p25)}</p>")
    css = """
:root{--bg:#f7f7f4;--fg:#1d1d1b;--mut:#6b6b66;--card:#fff;--line:#e3e2dc;--good:#1f7a4d;--bad:#b3261e;--acc:#3a5bd9}
@media (prefers-color-scheme: dark){:root{--bg:#141413;--fg:#ecebe6;--mut:#a3a29c;--card:#1e1e1c;--line:#33322e;--good:#5fc48f;--bad:#f2867d;--acc:#8ea5ff}}
body{background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:24px 16px;max-width:1200px;margin:auto}
h1{font-size:22px;margin:0}.sub{color:var(--mut);margin:4px 0 16px}h2{font-size:16px;margin:28px 0 8px}
table{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--line);display:block;overflow-x:auto}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;font-variant-numeric:tabular-nums}
th{font-weight:600;color:var(--mut);font-size:12px}code{font-size:12px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px}.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px}
.card .k{color:var(--mut);font-size:12px}.card .v{font-size:22px;font-weight:600}.good{color:var(--good)}.bad{color:var(--bad)}
.p{font-weight:700}.P0{color:var(--bad)}.st{font-size:12px;padding:1px 6px;border-radius:10px;border:1px solid var(--line)}
.validated_fixed{color:var(--good)}.returned_to_engineering,.regressed{color:var(--bad)}details{margin:8px 0}summary{cursor:pointer}"""
    OUT.write_text(f"<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
                   f"<title>Reading Buddy agent dashboard</title><style>{css}</style><body>{''.join(parts)}</body></html>", encoding="utf-8")
    return OUT


if __name__ == "__main__":
    print(build())
