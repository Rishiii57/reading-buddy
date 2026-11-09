"""Build audio test variants the recorded set does not cover, offline (ffmpeg, no API calls).

    python -m eval.make_testset                    # first: rebuild clean WAVs from the TTS cache (offline)
    python -m agent_org.audio_eval.augment         # writes eval/testset/<text>/aug_<variant>.wav + .json

Variants made from each text's clean_a reading (synthetic voice Riyaa):
  aug_fast       1.25x speaking rate (tempo, pitch kept)
  aug_slow       0.8x speaking rate
  aug_whisper    -20 dB, band-limited 400-3500 Hz, light hiss: a quiet, breathy reader
  aug_childlike  pitch raised ~3 semitones at the same tempo: a CRUDE proxy for a younger voice,
                 not a substitute for real children's speech
  aug_classroom  pink noise mixed at ~5 dB SNR: a noisy classroom

Streaming them through Prisma costs credits, so it is a separate, human-approved step:

    python -m eval.run_stt --variants aug_fast,aug_slow,aug_whisper,aug_childlike,aug_classroom

The script prints the total audio length so the cost can be estimated first. After recording,
`python -m agent_org.audio_eval.run` includes them in Part A automatically (condition = variant).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TESTSET = ROOT / "eval" / "testset"
VARIANTS = {
    "aug_fast": ("atempo=1.25", 1 / 1.25),
    "aug_slow": ("atempo=0.8", 1 / 0.8),
    "aug_whisper": ("volume=-20dB,highpass=f=400,lowpass=f=3500", 1.0),
    "aug_childlike": ("asetrate=16000*1.19,aresample=16000,atempo=0.8403", 1.0),
    "aug_classroom": (None, 1.0),
}


def ffmpeg(args):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr)


def duration(wav: Path) -> float:
    return (wav.stat().st_size - 44) / 32000


def main():
    total = 0.0
    made = 0
    for d in sorted(p for p in TESTSET.iterdir() if p.is_dir()):
        src = d / "clean_a.wav"
        if not src.exists():
            sys.exit(f"{src} missing: run `python -m eval.make_testset` first (offline, from the TTS cache)")
        truth = json.loads((d / "clean_a.json").read_text())
        for name, (filt, tscale) in VARIANTS.items():
            out = d / f"{name}.wav"
            if name == "aug_classroom":
                ffmpeg(["-i", str(src), "-f", "lavfi", "-i", "anoisesrc=color=pink:amplitude=0.06:sample_rate=16000",
                        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:weights=1 1[a]", "-map", "[a]",
                        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(out)])
            else:
                if name == "aug_whisper":
                    filt += ",aeval=val(0)+0.002*(random(0)-0.5):c=same"
                ffmpeg(["-i", str(src), "-af", filt, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(out)])
            t = dict(truth, variant=name, duration=round(truth["duration"] * tscale, 3),
                     segments=[dict(s, start=round(s["start"] * tscale, 3), end=round(s["end"] * tscale, 3)) for s in truth["segments"]],
                     note=f"derived from clean_a by ffmpeg ({name}); synthetic voice")
            (d / f"{name}.json").write_text(json.dumps(t, ensure_ascii=False, indent=1))
            total += duration(out)
            made += 1
    print(f"built {made} variant recordings, {total:.0f} s of audio in total.")
    print("Streaming them to Prisma (credits!) is a human-approved step: "
          "python -m eval.run_stt --variants " + ",".join(VARIANTS))


if __name__ == "__main__":
    main()
