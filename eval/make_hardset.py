"""Held-out "hard" readings, built from the cached line audio (no new TTS calls).

Each line of the voice-B clean reading gets:
  - a hesitation: the line is cut at its quietest point near the middle and 1.0-1.8 s of
    silence inserted (a child pausing mid-line, which must NOT trigger a prompt), and
  - background noise at about 10 dB SNR (pink-ish noise plus a low hum).

    python -m eval.make_hardset                                   # "hard"  (voice B, tuned on)
    python -m eval.make_hardset --source clean_a --name hard2 --seed 23   # held-out
"""
import argparse
import json
import random
from pathlib import Path

import numpy as np

from eval.make_testset import SR, write_wav

ROOT = Path(__file__).resolve().parent.parent
TESTSET = ROOT / "eval" / "testset"


def quiet_split(x: np.ndarray) -> int:
    """Sample index of the lowest-energy 60 ms window in the middle 30-70% of the clip."""
    win = int(0.06 * SR)
    lo, hi = int(len(x) * 0.3), int(len(x) * 0.7)
    best, at = None, (lo + hi) // 2
    for s in range(lo, hi - win, win // 3):
        e = float(np.mean(x[s:s + win] ** 2))
        if best is None or e < best:
            best, at = e, s + win // 2
    return at


def noise_like(n: int, rng: np.random.Generator) -> np.ndarray:
    white = rng.standard_normal(n)
    pink = np.convolve(white, np.ones(8) / 8, mode="same")
    hum = 0.3 * np.sin(2 * np.pi * 100 * np.arange(n) / SR)
    return pink + hum


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="clean_b")
    ap.add_argument("--name", default="hard")
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()
    rng_py = random.Random(args.seed)
    rng = np.random.default_rng(args.seed)
    for d in sorted(TESTSET.iterdir()):
        meta = json.loads((d / f"{args.source}.json").read_text())
        raw = (d / f"{args.source}.wav").read_bytes()[44:]
        x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768
        out, segs = [x[: int(meta["segments"][0]["start"] * SR)]], []
        prev_end = meta["segments"][0]["start"]
        for seg in meta["segments"]:
            a, b = int(seg["start"] * SR), int(seg["end"] * SR)
            gap = x[int(prev_end * SR):a]
            out.append(gap)
            clip = x[a:b]
            cut = quiet_split(clip)
            pause = rng_py.uniform(1.0, 1.8)
            t0 = sum(len(o) for o in out) / SR
            out += [clip[:cut], np.zeros(int(pause * SR), dtype=np.float32), clip[cut:]]
            t1 = sum(len(o) for o in out) / SR
            segs.append({"start": round(t0, 3), "end": round(t1, 3), "words": seg["words"],
                         "line": seg["line"], "hesitation_s": round(pause, 2)})
            prev_end = seg["end"]
        out.append(x[int(prev_end * SR):])
        y = np.concatenate(out)
        speech_rms = float(np.sqrt(np.mean(y[np.abs(y) > 0.02] ** 2)))
        nz = noise_like(len(y), rng)
        nz *= speech_rms / (10 ** (10 / 20)) / float(np.sqrt(np.mean(nz ** 2)))  # ~10 dB SNR
        y = np.clip(y + nz, -1, 1)
        write_wav(d / f"{args.name}.wav", (y * 32767).astype("<i2").tobytes())
        (d / f"{args.name}.json").write_text(json.dumps({**meta, "variant": args.name, "segments": segs,
                                                 "duration": round(len(y) / SR, 2), "truth": [],
                                                 "noise_snr_db": 10}, ensure_ascii=False, indent=1))
        print(d.name, f"{len(y) / SR:.1f}s")


if __name__ == "__main__":
    main()
