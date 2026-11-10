"""Speech and audio evaluation, kept separate from simulated user satisfaction.

    python -m agent_org.audio_eval.run [--label c01-baseline] [--app-root .]

Part A, MEASURED (real Gnani Prisma output): the 96 recorded streaming sessions in eval/runs/stt
(synthetic Timbre voices Riyaa and Devansh reading every text clean, with a substituted word, a
skipped word, a 5 s stall, and noisy/hesitant stress versions). For each language and condition:
  * Word Error Rate against what was actually spoken (substitutions and skips included);
  * server latency and transcript arrival after the speaker stops;
  * the tutor run on those transcripts (same engine as the app): alignment/tracking accuracy,
    missed-error rate, false corrections per 50 correctly read words, prompts during hesitations.

Part B, TEXT-LEVEL (no audio): scripted transcripts for conditions the recordings do not cover:
repeated words, self-corrections, skipped small words, similar-sounding substitutions, matra
variants, and mid-line thinking pauses of 1.5-4 s. They go through the same tutor engine on a
simulated clock. This measures the tutor's decisions, NOT speech recognition.

Not covered (needs real audio and credits, or consented recordings): children's voices, regional
accents, whispering, speaking speed, real background noise beyond the stress set. See
`augment` below: it builds those audio variants offline from the cached clean readings; streaming
them through Prisma (eval/run_stt.py) costs credits and is a human-approved step.
"""
import argparse
import json
import random
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
OUT_DIR = PKG / "runs" / "audio_eval"
LANG = {"en-IN": "English", "hi-IN": "Hindi", "gu-IN": "Gujarati"}


def _wer(ref, hyp):
    from rapidfuzz.distance import Levenshtein
    return Levenshtein.distance(ref, hyp) / max(1, len(ref))


def part_a(root: Path) -> dict:
    sys.path.insert(0, str(root))
    from backend.content import load_library
    from backend.normalize import norm, tokenize
    from backend.tutor import TutorConfig
    from eval.replay import score
    lib = load_library()
    runs = sorted((root / "eval" / "runs" / "stt").glob("*.json"))
    wer = defaultdict(list)
    lat = defaultdict(list)
    arrival = defaultdict(list)
    for f in runs:
        run = json.loads(f.read_text())
        meta = run["meta"]
        if meta["variant"] == "demo":
            continue
        text = lib[meta["text_id"]]
        spoken = []
        subs = {t["word"]: t["said"] for t in meta["truth"] if t["type"] == "sub"}
        skips = {t["word"] for t in meta["truth"] if t["type"] == "skip"}
        for seg in meta["segments"]:
            for w in seg["words"]:
                if w in skips:
                    continue
                spoken.append(norm(subs[w]) if w in subs else text.words[w].norm)
        trans = [e for e in run["events"] if e["type"] == "transcript"]
        hyp = tokenize(" ".join(e.get("text", "") for e in trans))
        v = meta["variant"]
        cond = "noise+hesitation" if v.startswith("hard") else v if v.startswith("aug_") else v.split("_")[0]
        wer[(meta["language"], cond)].append(_wer(spoken, hyp))
        lat[meta["language"]] += [e["latency"] for e in trans if e.get("latency") is not None]
        for seg, tr in zip(meta["segments"], trans):
            arrival[meta["language"]].append(tr["t"] - seg["end"])
    rep = score(TutorConfig())
    det = rep["details"]
    by_lang = {}
    for lang in LANG:
        d = [x for x in det if x["lang"] == lang]
        clean = [x for x in d if x["variant"].startswith("clean")]
        errs = [x for x in d if x.get("error")]
        stalls = [x for x in d if "stall_prompted" in x]
        hard = [x for x in d if x["variant"].startswith("hard")]
        n_words_clean = sum(len(lib[x["reading"].split("__")[0]].words) for x in clean)
        by_lang[lang] = {
            "wer_clean": round(statistics.mean(wer[(lang, "clean")]), 3),
            "wer_by_condition": {c: round(statistics.mean(v), 3) for (l2, c), v in sorted(wer.items()) if l2 == lang},
            "latency_ms_median": statistics.median(lat[lang]),
            "transcript_after_speech_s_median": round(statistics.median(arrival[lang]), 2),
            "alignment_accuracy": round(statistics.mean(x["track_frac"] for x in clean), 3),
            "alignment_accuracy_noisy": round(statistics.mean(x["track_frac"] for x in hard), 3),
            "missed_error_rate": round(1 - sum(x["caught"] for x in errs) / max(1, len(errs)), 3),
            "false_correction_per_50": round(50 * sum(x["stray_corrections"] for x in clean) / max(1, n_words_clean), 3),
            "false_correction_per_50_noisy": round(50 * sum(x["stray_corrections"] for x in hard) /
                                                   max(1, sum(len(lib[x["reading"].split("__")[0]].words) for x in hard)), 3),
            "stall_detection": f"{sum(x['stall_prompted'] for x in stalls)}/{len(stalls)}",
            "prompts_during_hesitations_noisy": sum(x["prompts"] for x in hard),
            "readings": len(d),
        }
    return {"by_language": by_lang, "replay_summary": rep["summary"], "recordings": len(runs)}


# ---------------------------------------------------------------- Part B
CONDITIONS = ["clean", "repeat_word", "self_correct", "skip_small", "substitute", "matra_variant",
              "pause_1.5", "pause_2.5", "pause_3.5", "slow_word_by_word"]


def _line_script(text, cond, rng):
    """Transcript events for reading line 0 under a condition, plus ground truth."""
    from agent_org.child_agent.speech_model import is_small, mispronounce
    a, b = text.line_range(0)
    words = [w.display.strip(",.!?;:।\"'") for w in text.words[a:b]]
    errors, pauses = set(), []
    toks = list(words)
    segs = []
    if cond == "repeat_word":
        k = rng.randrange(len(toks))
        toks.insert(k + 1, toks[k])
    elif cond == "self_correct":
        k = rng.randrange(1, len(toks))
        wrong = mispronounce(toks[k], text.language, ["guesses_from_first_letter", "letter_confusion"], rng)
        toks.insert(k, wrong)
    elif cond == "skip_small":
        smalls = [i for i, w in enumerate(words) if is_small(w)]
        if smalls:
            k = rng.choice(smalls)
            toks.pop(k)
            errors.add(a + k)
    elif cond == "substitute":
        cands = [i for i, w in enumerate(words) if not is_small(w)]
        k = rng.choice(cands)
        toks[k] = mispronounce(words[k], text.language, ["guesses_from_first_letter", "letter_confusion", "drops_endings"], rng)
        errors.add(a + k)
    elif cond == "matra_variant" and text.language != "en-IN":
        cands = [i for i, w in enumerate(words) if not is_small(w)]
        k = rng.choice(cands)
        toks[k] = mispronounce(words[k], text.language, ["matra_errors"], rng)
        errors.add(a + k)
    if cond.startswith("pause_") or cond == "slow_word_by_word":
        if cond == "slow_word_by_word":
            cut = list(range(1, len(toks)))
            gap = 2.2
        else:
            cut = [rng.randrange(1, len(toks))]
            gap = float(cond.split("_")[1])
        prev = 0
        for c in cut + [len(toks)]:
            segs.append(toks[prev:c])
            prev = c
        pauses = [gap] * (len(segs) - 1)
    else:
        segs = [toks]
    return segs, pauses, errors


def part_b(seed: int = 7) -> dict:
    from backend.content import load_library
    from backend.tutor import TutorEngine
    lib = load_library()
    rng = random.Random(seed)
    res = defaultdict(lambda: {"lines": 0, "correct_words": 0, "false_corr": 0, "errors": 0, "missed": 0,
                               "pauses": 0, "interrupted": 0})
    for text in lib.values():
        for cond in CONDITIONS:
            if cond == "matra_variant" and text.language == "en-IN":
                continue
            for rep in range(3):
                segs, pauses, errors = _line_script(text, cond, rng)
                e = TutorEngine(text, now=0.0)
                e.state = "CHILD_READING"
                t, events = 1.0, []
                pause_windows = []
                for i, seg in enumerate(segs):
                    dur = 0.45 * len(seg) + 0.2
                    events.append((t, "ss", ""))
                    events.append((t + dur + 0.42, "tr", " ".join(seg)))
                    t += dur
                    if i < len(pauses):
                        pause_windows.append((t + 0.42, t + pauses[i]))
                        t += pauses[i]
                acts, corrections, prompts = [], set(), []
                tt, ei, busy = 0.0, 0, None
                while tt < t + 8.0:
                    while ei < len(events) and events[ei][0] <= tt:
                        _, kind, txt = events[ei]
                        ei += 1
                        acts = e.on_speech_start(tt) if kind == "ss" else e.on_transcript(txt, tt, 120)
                        _collect(acts, tt, corrections, prompts)
                    acts = e.tick(tt)
                    _collect(acts, tt, corrections, prompts)
                    if e.tutor_busy and busy is None:
                        busy = tt
                    if busy is not None and tt - busy >= 1.5:
                        e.on_tutor_audio_end(tt)
                        busy = None
                    if e.line > 0:
                        break
                    tt = round(tt + 0.05, 2)
                corrections = {w for ev in e.log if ev["event"] == "correction" for w in ev["words"]}
                a, b = text.line_range(0)
                r = res[(text.language, cond)]
                r["lines"] += 1
                r["correct_words"] += (b - a) - len(errors)
                r["false_corr"] += len([w for w in corrections if w not in errors])
                r["errors"] += len(errors)
                r["missed"] += len([w for w in errors if w not in corrections])
                r["pauses"] += len(pause_windows)
                r["interrupted"] += sum(1 for (p0, p1) in pause_windows if any(p0 <= pt < p1 for pt in prompts))
    out = {}
    for (lang, cond), r in sorted(res.items()):
        out.setdefault(lang, {})[cond] = {
            "lines": r["lines"],
            "false_corr_per_50": round(50 * r["false_corr"] / max(1, r["correct_words"]), 2),
            "missed_error_rate": round(r["missed"] / r["errors"], 2) if r["errors"] else None,
            "pause_interruption_rate": round(r["interrupted"] / r["pauses"], 2) if r["pauses"] else None,
        }
    return out


def _collect(acts, tt, corrections, prompts):
    for a in acts or []:
        if a.get("type") != "say":
            continue
        if a["kind"].startswith(("stall", "fix")):
            prompts.append(tt)


def headline(a: dict, b: dict) -> str:
    worst = max(a["by_language"].items(), key=lambda kv: kv[1]["wer_clean"])
    p25 = {l: d.get("pause_2.5", {}).get("pause_interruption_rate") for l, d in b.items()}
    return (f"Measured on synthetic adult voices: clean WER is highest for {LANG[worst[0]]} ({worst[1]['wer_clean']}); "
            f"noise and hesitation cut tracking to {min(v['alignment_accuracy_noisy'] for v in a['by_language'].values())}–"
            f"{max(v['alignment_accuracy_noisy'] for v in a['by_language'].values())} of checkpoints. Text-level: a 2.5 s "
            f"mid-line thinking pause is interrupted in {', '.join(f'{LANG[l]} {v}' for l, v in p25.items())} of cases. "
            "Child-voice accuracy is unmeasured.")


def render(o: dict) -> str:
    a, b = o["part_a"], o["part_b"]
    L = [f"# Speech and audio evaluation: {o['label']}", "", f"Generated {o['generated']} from app commit `{o['commit']}`.", "",
         "> Measured speech-recognition numbers (Part A) and tutor-decision numbers on scripted transcripts (Part B) are "
         "reported separately from the simulated children's satisfaction. Neither includes real children's voices.", "",
         f"**Headline:** {o['headline']}", "",
         "## Part A: Prisma on recorded synthetic speech (measured)", "",
         "| Language | WER clean | WER sub | WER skip | WER stall | WER noise+hesitation | Latency ms | Transcript after speech s | "
         "Alignment acc. | Alignment acc. (noisy) | Missed errors | False corr./50 | False corr./50 (noisy) | Stalls detected |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for lang, d in a["by_language"].items():
        w = d["wer_by_condition"]
        L.append(f"| {LANG[lang]} | {d['wer_clean']} | {w.get('sub')} | {w.get('skip')} | {w.get('stall')} | {w.get('noise+hesitation')} | "
                 f"{d['latency_ms_median']} | {d['transcript_after_speech_s_median']} | {d['alignment_accuracy']} | "
                 f"{d['alignment_accuracy_noisy']} | {d['missed_error_rate']} | {d['false_correction_per_50']} | "
                 f"{d['false_correction_per_50_noisy']} | {d['stall_detection']} |")
    L += ["", f"{a['recordings']} recordings (12 texts × 8 variants, 2 synthetic voices). WER is against the words actually "
          "spoken (a substituted word counts as what was said).", "",
          "## Part B: tutor decisions on scripted transcripts (text level, no audio)", "",
          "Line 1 of every text, 3 random variants per condition. `false corr./50`: corrections of correctly read words per "
          "50 such words. `missed`: injected reading errors never practised. `pause interrupted`: share of mid-line pauses "
          "during which Buddy spoke (stall prompt or correction).", ""]
    for lang, conds in b.items():
        L += [f"### {LANG[lang]}", "", "| Condition | Lines | False corr./50 | Missed error rate | Pause interrupted |", "|---|---|---|---|---|"]
        L += [f"| {c} | {v['lines']} | {v['false_corr_per_50']} | {v['missed_error_rate'] if v['missed_error_rate'] is not None else '-'} | "
              f"{v['pause_interruption_rate'] if v['pause_interruption_rate'] is not None else '-'} |" for c, v in conds.items()]
        L.append("")
    L += ["## Not yet measured", "",
          "- Children's voices (pitch, articulation): needs consented, safeguarded recordings (human approval).",
          "- Whispering, fast/slow speech and accents on real audio: `python -m agent_org.audio_eval.augment` builds these "
          "variants offline from cached readings; streaming them through Prisma costs credits (`eval/run_stt.py`).",
          ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="latest")
    ap.add_argument("--app-root", default=str(PKG.parent))
    a = ap.parse_args(argv)
    root = Path(a.app_root).resolve()
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip()
    pa = part_a(root)
    pb = part_b()
    o = {"label": a.label, "generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "commit": commit, "part_a": pa, "part_b": pb}
    o["headline"] = headline(pa, pb)
    o["by_language"] = pa["by_language"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{a.label}.json").write_text(json.dumps(o, indent=1, ensure_ascii=False))
    (OUT_DIR / "latest.json").write_text(json.dumps(o, indent=1, ensure_ascii=False))
    (OUT_DIR / f"{a.label}.md").write_text(render(o), encoding="utf-8")
    print(render(o))


if __name__ == "__main__":
    main()
