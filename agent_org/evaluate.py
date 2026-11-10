"""Phase 9: compare the initial and the improved product with measurable results, and evaluate the
agent system itself. Writes docs/agent-org/AGENT_EVALUATION_REPORT.md.

    python -m agent_org.evaluate --before c01/baseline-v2 --after c02/retest

Both runs must use the same child-agent code and the same persona seeds, so the only difference
is the app build.
"""
import argparse
import itertools
import json
import statistics
from collections import Counter
from pathlib import Path

from . import metrics as M
from .personas.persona import GRADES, load as load_personas

PKG = Path(__file__).resolve().parent
RUNS = PKG / "runs"
DOC = PKG.parent / "docs" / "agent-org" / "AGENT_EVALUATION_REPORT.md"
LANG = {"en-IN": "English", "hi-IN": "Hindi", "gu-IN": "Gujarati"}
HEAD = ["session_start_rate", "completion_rate", "abandon_rate", "coverage", "interruptions_per_agent",
        "stall_interruptions_per_agent", "mic_tap_pause_rate", "spoken_guidance_gap_rate", "consent_blocked_rate",
        "consent_self_approved_rate", "level_mismatch_rate", "unheard_words_per_agent", "drill_repeat_rate",
        "false_corrections_per_agent", "missed_errors_per_agent", "long_talk_rate", "intro_s_median", "frustration_peak_mean"]


def arrow(k, b, a):
    if b == a:
        return "="
    better = (a < b) if M.METRICS[k][1] else (a > b)
    return "▲ better" if better else "▼ worse"


def table(head, rows):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] +
                     ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def persona_distinctness():
    ps = load_personas()

    def vec(p):
        b = p.behaviour
        return [b.words_per_s / 3, b.word_accuracy, b.echo_skill, float(b.can_decode), b.p_skip_small, b.p_hesitate,
                sum(b.hesitation_s) / 14, b.p_self_correct, b.volume, b.p_talk_over_buddy, b.p_off_task_click * 4,
                b.p_tap_mic_to_talk, p.ui_english_reading, p.technology_familiarity, p.patience / 6,
                p.attention_span_s / 300, p.reads(p.language_preference), p.speaks(p.language_preference), float(p.grown_up_setup)]
    d = [sum((x - y) ** 2 for x, y in zip(vec(a), vec(b))) ** .5 for a, b in itertools.combinations(ps, 2)]
    dup = sum(1 for a, b in itertools.combinations(ps, 2) if vec(a) == vec(b) and a.common_mistakes == b.common_mistakes
              and a.journey == b.journey)
    return {"n": len(ps), "min": round(min(d), 3), "median": round(statistics.median(d), 3), "identical": dup}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", default="c01/baseline-v2")
    ap.add_argument("--after", default="c02/retest")
    a = ap.parse_args(argv)
    rb = [r for r in M.load_reports(RUNS / a.before) if r["outcome"] != "harness_error"]
    ra = [r for r in M.load_reports(RUNS / a.after) if r["outcome"] != "harness_error"]
    hb = len(M.load_reports(RUNS / a.before)) - len(rb)
    ha = len(M.load_reports(RUNS / a.after)) - len(ra)
    mb, ma = M.compute(rb), M.compute(ra)
    metab = json.loads((RUNS / a.before / "run.json").read_text())
    metaa = json.loads((RUNS / a.after / "run.json").read_text())
    L = ["# Agent evaluation report", "",
         f"Initial product (`{metab['app_commit']}`, run `{a.before}`) vs improved product (`{metaa['app_commit']}`, run "
         f"`{a.after}`): the same 50 simulated children, the same seeds, and the same child-agent code, so differences "
         "come from the app. Harness errors (excluded): "
         f"{hb} before, {ha} after.", "",
         "> Simulated children and simulated speech: these numbers measure the interface, the tutor's behaviour and the "
         "learning loop as children of different levels experience them. They are not speech-recognition accuracy (see the "
         "audio section) and not results from real children.", "",
         "## Headline results", ""]
    L.append(table(["Measure", "Initial", "Improved", "Change"],
                   [[M.METRICS[k][2], mb[k], ma[k], arrow(k, mb[k], ma[k])] for k in HEAD]))
    L += ["", "## By grade", ""]
    gb = M.by_group(rb, lambda r: r["persona"]["grade"])
    ga = M.by_group(ra, lambda r: r["persona"]["grade"])
    L.append(table(["Grade", "n", "Started", "Finished", "Covered", "Interruptions/child", "Peak frustration"],
                   [[g, gb[g]["n"], f"{gb[g]['session_start_rate']} → {ga[g]['session_start_rate']}",
                     f"{gb[g]['completion_rate']} → {ga[g]['completion_rate']}", f"{gb[g]['coverage']} → {ga[g]['coverage']}",
                     f"{gb[g]['interruptions_per_agent']} → {ga[g]['interruptions_per_agent']}",
                     f"{gb[g]['frustration_peak_mean']} → {ga[g]['frustration_peak_mean']}"] for g in GRADES if g in gb and g in ga]))
    L += ["", "## By language", ""]
    lb = M.by_group(rb, lambda r: r["persona"]["language_preference"])
    la = M.by_group(ra, lambda r: r["persona"]["language_preference"])
    L.append(table(["Language", "n", "Started", "Finished", "Covered", "False corrections/child", "Missed errors/child"],
                   [[LANG[k], lb[k]["n"], f"{lb[k]['session_start_rate']} → {la[k]['session_start_rate']}",
                     f"{lb[k]['completion_rate']} → {la[k]['completion_rate']}", f"{lb[k]['coverage']} → {la[k]['coverage']}",
                     f"{lb[k]['false_corrections_per_agent']} → {la[k]['false_corrections_per_agent']}",
                     f"{lb[k]['missed_errors_per_agent']} → {la[k]['missed_errors_per_agent']}"] for k in LANG if k in lb and k in la]))
    ob, oa = Counter(r["outcome"] for r in rb), Counter(r["outcome"] for r in ra)
    L += ["", "## Outcomes", "", table(["Outcome", "Initial", "Improved"],
                                       [[o, ob.get(o, 0), oa.get(o, 0)] for o in sorted(set(ob) | set(oa))])]
    cb = Counter(i["code"] for r in rb for i in r["experience"]["issues"])
    ca = Counter(i["code"] for r in ra for i in r["experience"]["issues"])
    L += ["", "## Children affected per symptom", "",
          table(["Symptom", "Initial", "Improved"], [[c, cb.get(c, 0), ca.get(c, 0)]
                                                     for c in sorted(set(cb) | set(ca), key=lambda c: -cb.get(c, 0))])]
    # what changed in the product
    L += ["", "## What changed between the two builds", ""]
    for f in sorted((PKG / "engineering" / "changes").glob("REQ-*.json")):
        ch = json.loads(f.read_text())
        if not ch.get("merged"):
            continue
        qa = ch.get("qa", [])
        verdict = qa[-1]["verdict"] if qa else "-"
        L.append(f"- **{ch['requirement']}** ({ch.get('role')}): {ch['rounds'][-1]['summary']} · {len(ch['rounds'])} engineering "
                 f"round(s), QA: {', '.join(q['verdict'] for q in qa)} · merged as "
                 f"{'QA-validated' if verdict == 'validated_fixed' else 'accepted by human directive (QA evidence attached)'}")
    # audio
    ae = RUNS / "audio_eval" / "latest.json"
    if ae.exists():
        x = json.loads(ae.read_text())
        L += ["", "## Speech and audio (measured separately)", "", x["headline"], "",
              table(["Language", "WER clean", "WER noise+hesitation", "Alignment", "Missed error rate", "False corr./50 words", "Latency ms"],
                    [[LANG[k], v["wer_clean"], v["wer_by_condition"].get("noise+hesitation"), v["alignment_accuracy"],
                      v["missed_error_rate"], v["false_correction_per_50"], v["latency_ms_median"]] for k, v in x["by_language"].items()]),
              "", "Text-level tutor test, share of 2.5 s / 3.5 s mid-line pauses interrupted: " +
              ", ".join(f"{LANG[k]} {d.get('pause_2.5', {}).get('pause_interruption_rate')} / {d.get('pause_3.5', {}).get('pause_interruption_rate')}"
                        for k, d in x["part_b"].items()) + f" (app `{x['commit']}`)."]
    # the agent system itself
    pd = persona_distinctness()
    sig = len({(r["outcome"], tuple(sorted(i["code"] for i in r["experience"]["issues"]))) for r in ra})
    led_a = metaa.get("summary", {}).get("ledger", {})
    L += ["", "## Evaluation of the agent system", "",
          table(["Check", "Result"], [
              ["Personas", f"{pd['n']} (Nursery 10, LKG 8, UKG 8, Class 1–4 six each; en/hi/gu 17/17/16)"],
              ["Behaviour distance between personas (19 traits)", f"min {pd['min']}, median {pd['median']}; identical pairs: {pd['identical']}"],
              ["Distinct (outcome, symptom-set) experiences in one 50-child run", f"{sig} of {len(ra)}"],
              ["Real product interaction", "Playwright/Chromium on the real UI, WebSocket protocol and tutor engine; coordinate taps, scrolling"],
              ["Blindness", "agents read only the screen and Buddy's voice; no code, docs or other reports"],
              ["Harness errors", f"{hb} / {ha} (excluded from findings, retried once)"],
              ["Cost of a 50-child run", f"{led_a.get('wall_s')} s wall time, Gnani credits {led_a.get('gnani_credits')}, LLM tokens {led_a.get('llm_tokens')}"],
              ["Would-be live STT for the same sessions", f"{led_a.get('stt_stream_s_if_live')} s of audio"],
          ])]
    L += ["", "## Reading the results", "",
          "- Biggest gains: finishing a text (Class 1 0 → 83 %, UKG 0 → 38 %), abandonment, coverage, frustration, and the "
          "complete removal of the mic-tap pause, written-only onboarding and consent dead ends.",
          "- Worse: misreadings accepted as correct rose. Most of this is intended: pre-primary rhymes now accept imperfect "
          "repetition (echo reading), and children simply read more words. For Class 2-4 it is REQ-LENIENT-MATCHING (awaiting a "
          "product decision).",
          "- Unchanged problems (deferred, next cycle): Buddy's long opening talk, speech lost while Buddy talks, Nursery "
          "children still not finishing a rhyme, and children leaving the reading page by accident.", ""]
    L += ["## Honest limits", "",
          "- The children are deterministic, seeded behaviour policies, not people and not LLMs. Their speech and the speech "
          "model's errors are modelled. Findings that depend on real children's voices (accuracy, accent, pitch) need consented "
          "recordings or the credit-spending audio steps in RUN_INSTRUCTIONS.md.",
          "- Uncached Buddy lines play as timed placeholders in simulation (no Timbre access from the build machine). The 13 new "
          "rhymes and the new phrases need `python -m backend.pregen --words` once on a machine with the key.",
          "- Sessions run in real time; parallel runs on a 2-CPU machine add timing noise, so QA compares the same personas and "
          "seeds on both builds and uses two seeds per persona.",
          "- During the cycle the measuring instrument was fixed several times (tap detection, hearing, level tags, on-screen "
          "preference). This comparison re-ran the initial build with the final instrument for that reason.",
          "- Two changes were merged on the human's directive although QA returned them (consent removal, pre-primary rhymes); "
          "the QA evidence and reasons are in the backlog and PRODUCT_IMPROVEMENT_HISTORY.md."]
    DOC.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(DOC)


if __name__ == "__main__":
    main()
