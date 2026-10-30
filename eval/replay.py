"""Replay recorded Prisma events through the tutor engine and score it against ground truth.

No API calls: this reads eval/runs/stt/*.json (made by eval/run_stt.py) and runs the
same TutorEngine the app uses, on a simulated clock.

    python -m eval.replay                       # score with default settings, write eval/RESULTS.md
    python -m eval.replay --set stall_mid_s=2.2 align.match_thr=0.55 --no-write
    python -m eval.replay --show en-kite__sub   # print the event trace of one reading
"""
import argparse
import json
import statistics
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

from rapidfuzz.distance import Levenshtein

from backend.content import load_library
from backend.normalize import tokenize
from backend.tutor import TutorConfig, TutorEngine

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "eval" / "runs" / "stt"
DT = 0.05


def make_cfg(overrides: list[str]) -> TutorConfig:
    cfg = TutorConfig()
    for o in overrides:
        k, v = o.split("=")
        if k.startswith("align."):
            cfg.align = replace(cfg.align, **{k[6:]: type(getattr(cfg.align, k[6:]))(v)})
        else:
            cfg = replace(cfg, **{k: type(getattr(cfg, k))(v)})
    return cfg


def say_duration(action: dict) -> float:
    n = 0
    for part in action["parts"]:
        n += (part[2] - part[1]) if part[0] == "span" else 3
    return 0.6 + 0.4 * n


def replay(run: dict, text, cfg: TutorConfig):
    meta, events = run["meta"], sorted(run["events"], key=lambda e: e["t"])
    eng = TutorEngine(text, cfg, now=0.0)
    eng.state = "CHILD_READING"  # the recorded readers start straight away (no greeting)
    checkpoints = {round(s["end"] + 1.5, 2): max(s["words"]) + 1 for s in meta["segments"] if s["words"]}
    observed = {}
    busy_until = None
    t, ei, end = 0.0, 0, meta["duration"] + 4.0
    while t <= end:
        acts = []
        while ei < len(events) and events[ei]["t"] <= t:
            e = events[ei]
            ei += 1
            if e["type"] == "speech_start":
                acts += eng.on_speech_start(t)
            elif e["type"] == "transcript":
                acts += eng.on_transcript(e.get("text", ""), t, e.get("latency") or 0, e.get("audio_duration_ms"))
        acts += eng.tick(t)
        for a in acts:
            if a["type"] == "say":
                busy_until = t + say_duration(a)
        if busy_until is not None and t >= busy_until:
            eng.on_tutor_audio_end(t)
            busy_until = None
        for cp, want in checkpoints.items():
            if cp not in observed and t >= cp:
                observed[cp] = (eng.p, want)
        t = round(t + DT, 3)
    return eng, observed


def score(cfg: TutorConfig, show: str | None = None) -> dict:
    lib = load_library()
    by_lang = defaultdict(lambda: defaultdict(list))
    tracking, false_corr, false_prompts, words_ok = [], 0, 0, 0
    hards: dict[str, dict] = {}
    caught = {"sub": [], "skip": []}
    stall_lat, stall_hit = [], []
    stt_lat, arrival, wer = [], [], defaultdict(list)
    details = []
    for f in sorted(RUNS.glob("*.json")):
        run = json.loads(f.read_text())
        meta = run["meta"]
        if meta["variant"] == "demo":
            continue
        text = lib[meta["text_id"]]
        lang, var = meta["language"], meta["variant"]
        eng, observed = replay(run, text, cfg)
        if show and f.stem == show:
            print(json.dumps(eng.log, ensure_ascii=False, indent=1))
            print("checkpoints (pointer, want):", observed)
        log = eng.log
        # A scripted reader cannot do word practice, so the replay diverges after Buddy's first
        # correction: score each reading on its first correction only.
        first = next((e for e in log if e["event"] == "correction"), None)
        corr = [{"event": "correction", "t": first["t"], "word": w} for w in first["words"]] if first else []
        prompts = [e for e in log if e["event"] == "prompt" and (not first or e["t"] < first["t"])]
        truth = meta["truth"]
        err_words = {t["word"] for t in truth if t["type"] in ("sub", "skip")}
        stray = [c for c in corr if not any(abs(c["word"] - w) <= 1 for w in err_words)]  # falsely flagged words
        stray_notes = []
        false_corr += len(stray)
        words_ok += len(text.words) - len(err_words)
        trans = [e for e in run["events"] if e["type"] == "transcript"]
        stt_lat += [e["latency"] for e in trans if e.get("latency") is not None]
        rec = {"reading": f.stem, "lang": lang, "variant": var, "corrections": len(corr),
               "stray_corrections": len(stray), "stray_notes": len(stray_notes),
               "prompts": len(prompts), "finished": eng.done}
        if var.startswith("hard"):  # stress tests, reported separately
            hard = hards.setdefault(var, {"tracking": [], "false_corr": 0, "prompts": 0, "words": 0})
            ok = sum(1 for p, want in observed.values() if p == want)
            frac = ok / max(1, len(observed))
            hard["tracking"].append(frac >= 0.9 and eng.done and not first)
            hard["false_corr"] += len(stray)
            hard["false_notes"] = hard.get("false_notes", 0) + len(stray_notes)
            hard["prompts"] += len(prompts)
            hard["words"] += len(text.words)
            false_corr -= len(stray)
            words_ok -= len(text.words)
            rec.update(track_frac=round(frac, 2), tracking_pass=frac >= 0.9 and eng.done and not first)
            details.append(rec)
            continue
        if var.startswith("clean"):
            ok = sum(1 for p, want in observed.values() if p == want)
            frac = ok / max(1, len(observed))
            passed = frac >= 0.9 and eng.done and not first
            tracking.append(passed)
            by_lang[lang]["tracking"].append(passed)
            false_prompts += len(prompts)
            rec.update(track_frac=round(frac, 2), tracking_pass=passed)
            # Prisma word error rate against the text (synthetic voices)
            ref = [w.norm for w in text.words]
            hyp = tokenize(" ".join(e.get("text", "") for e in trans))
            wer[lang].append(Levenshtein.distance(ref, hyp) / len(ref))
            # how long after a line ends its transcript arrives
            for seg, tr in zip(meta["segments"], trans):
                arrival.append(tr["t"] - seg["end"])
        for t in truth:
            if t["type"] in ("sub", "skip"):
                hit = [c for c in corr if abs(c["word"] - t["word"]) <= 1]
                ok = bool(hit)
                caught[t["type"]].append(ok)
                by_lang[lang]["errors"].append(ok)
                rec.update(error=t["type"], caught=ok,
                           latency=round(hit[0]["t"] - t["segment_end"], 2) if hit else None)
            elif t["type"] == "stall":
                line = text.words[t["word"]].line
                hit = [p for p in prompts if p["line"] == line and t["start"] <= p["t"] <= t["end"]]
                stall_hit.append(bool(hit))
                by_lang[lang]["stall"].append(bool(hit))
                if hit:
                    stall_lat.append(hit[0]["t"] - t["start"])
                rec.update(stall_prompted=bool(hit),
                           stall_latency=round(hit[0]["t"] - t["start"], 2) if hit else None)
        details.append(rec)
    errs = caught["sub"] + caught["skip"]
    err_lat = [d["latency"] for d in details if d.get("latency") is not None]
    res = {
        "readings": len(details),
        "tracking_pass": f"{sum(tracking)}/{len(tracking)}",
        "errors_caught": f"{sum(errs)}/{len(errs)}",
        "subs_caught": f"{sum(caught['sub'])}/{len(caught['sub'])}",
        "skips_caught": f"{sum(caught['skip'])}/{len(caught['skip'])}",
        "error_response_s_median": round(statistics.median(err_lat), 2) if err_lat else None,
        "stalls_prompted": f"{sum(stall_hit)}/{len(stall_hit)}",
        "stall_prompt_s_median": round(statistics.median(stall_lat), 2) if stall_lat else None,
        "stall_prompt_s_max": round(max(stall_lat), 2) if stall_lat else None,
        "false_corrections": false_corr,
        "correct_words": words_ok,
        "false_corrections_per_50_words": round(50 * false_corr / max(1, words_ok), 3),
        "prompts_in_clean_readings": false_prompts,
        "prisma_latency_ms_median": statistics.median(stt_lat) if stt_lat else None,
        "transcript_after_line_end_s_median": round(statistics.median(arrival), 2) if arrival else None,
        "prisma_wer_clean": {k: round(statistics.mean(v), 3) for k, v in wer.items()},
        "stress_sets": {name: {"tracking_pass": f"{sum(h['tracking'])}/{len(h['tracking'])}",
                               "false_corrections": h["false_corr"], "words": h["words"],
                               "false_silent_notes": h.get("false_notes", 0),
                               "false_corrections_per_50_words": round(50 * h["false_corr"] / max(1, h["words"]), 2),
                               "prompts_during_hesitations": h["prompts"]} for name, h in sorted(hards.items())},
        "by_language": {lang: {k: f"{sum(v)}/{len(v)}" for k, v in d.items()} for lang, d in by_lang.items()},
    }
    return {"summary": res, "details": details}


def write_report(out: dict, cfg: TutorConfig):
    s, rows = out["summary"], out["details"]
    lines = [
        "# Test results (synthetic test set)",
        "",
        "Generated by `python -m eval.replay` from Prisma v2.5 streaming transcripts of the synthetic "
        "readings in `eval/testset` (Timbre voices Riyaa and Devansh; no human or child audio). "
        "The tutor is strict and line-by-line: a scripted reader cannot do word practice, so each "
        "reading is scored up to Buddy's first correction, and a false correction is a correctly read word "
        "that Buddy flagged for practice.",
        "",
        "| Objective (PID) | Target | Result |",
        "|---|---|---|",
        f"| Track the reader's place | 9 of 10 readings | {s['tracking_pass']} clean readings tracked (≥90% of line checkpoints, finished) |",
        f"| Prompt when the reader stalls | within 2.5 s, none at line ends | {s['stalls_prompted']} stalls prompted; median {s['stall_prompt_s_median']} s, max {s['stall_prompt_s_max']} s after the reader stopped; {s['prompts_in_clean_readings']} prompts in clean readings |",
        f"| Catch a wrong or skipped word (starts word practice) | 7 of 10 | {s['errors_caught']} caught (substitutions {s['subs_caught']}, skips {s['skips_caught']}); median {s['error_response_s_median']} s after the line ended |",
        f"| Few false corrections (PID: < 1 per 50 words; now strict matching) | | {s['false_corrections']} correctly read words flagged, over {s['correct_words']} = {s['false_corrections_per_50_words']} per 50 |",
        f"| Three languages | full loop in gu, en, hi | see per-language table |",
        "",
        "## By language",
        "",
        "| Language | Tracking | Errors caught | Stalls prompted | Prisma WER (clean) |",
        "|---|---|---|---|---|",
    ]
    for lang, d in s["by_language"].items():
        lines.append(f"| {lang} | {d.get('tracking')} | {d.get('errors')} | {d.get('stall')} | {s['prisma_wer_clean'].get(lang)} |")
    lines += [
        "",
        f"Prisma transcription latency (server-reported, median): {s['prisma_latency_ms_median']} ms. "
        f"A line's transcript arrives a median {s['transcript_after_line_end_s_median']} s after the reader stops "
        f"(includes the {cfg.vad_silence_ms} ms end-of-speech silence).",
        "",
        "## Stress tests (noise and mid-line hesitations)",
        "",
        "Built from the cached clean readings with `eval/make_hardset.py`: ~10 dB SNR background noise, and every line cut at its "
        "quietest point with a 1.0-1.8 s pause inserted. The cut sometimes lands inside a word, which is harsher than a real "
        "child's pause. `hard` (voice Devansh) was used for one round of robustness fixes; `hard2` (voice Riyaa, new noise and "
        "pause points) was not used for tuning. Tracking here is pessimistic: after any correction the scripted reader does not "
        "re-read, as a child would, so the pointer stays behind.",
        "",
        "| Set | Tracking pass | Spoken false corrections | Per 50 words | Silent false notes | Prompts during hesitations |",
        "|---|---|---|---|---|---|",
    ]
    for name, h in s["stress_sets"].items():
        lines.append(f"| {name} | {h['tracking_pass']} | {h['false_corrections']} / {h['words']} words | "
                     f"{h['false_corrections_per_50_words']} | {h['false_silent_notes']} | {h['prompts_during_hesitations']} |")
    lines += [
        "",
        "## Every reading",
        "",
        "| Reading | Result |",
        "|---|---|",
    ]
    for r in rows:
        bits = []
        if "track_frac" in r and not r["variant"].startswith("hard"):
            bits.append(f"tracking {r['track_frac']:.0%}" + ("" if r["tracking_pass"] else " ✗"))
        if "error" in r:
            bits.append(f"{r['error']} {'caught' if r['caught'] else 'MISSED'}"
                        + (f" in {r['latency']} s" if r["latency"] is not None else ""))
        if "stall_prompted" in r:
            bits.append(f"stall {'prompted in ' + str(r['stall_latency']) + ' s' if r['stall_prompted'] else 'MISSED'}")
        if r["stray_corrections"] and not r["variant"].startswith("hard"):
            bits.append(f"{r['stray_corrections']} false correction(s)")
        if r["variant"].startswith("hard"):
            bits.append(f"tracking {r['track_frac']:.0%}; {r['stray_corrections']} false correction(s), "
                        f"{r['stray_notes']} silent note(s), {r['prompts']} prompt(s)")
        elif r["variant"].startswith("clean") and r["prompts"]:
            bits.append(f"{r['prompts']} unneeded prompt(s)")
        lines.append(f"| {r['reading']} | {'; '.join(bits)} |")
    (ROOT / "eval" / "RESULTS.md").write_text("\n".join(lines) + "\n")
    (ROOT / "eval" / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs="*", default=[])
    ap.add_argument("--show")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    cfg = make_cfg(args.set)
    out = score(cfg, args.show)
    print(json.dumps(out["summary"], ensure_ascii=False, indent=1))
    for r in out["details"]:
        flag = (r.get("caught") is False or r.get("stall_prompted") is False or r["stray_corrections"]
                or r.get("tracking_pass") is False or (r["variant"].startswith("clean") and r["prompts"]))
        if flag:
            print("  !", r)
    if not args.no_write:
        write_report(out, cfg)


if __name__ == "__main__":
    main()
