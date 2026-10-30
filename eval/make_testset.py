"""Build the synthetic test set: Timbre voices "reading" each text, with known errors.

For every text we write 16 kHz WAV readings plus a JSON ground truth:
  clean_a, clean_b  - correct readings by two voices (one with a long line-end pause)
  sub               - one word replaced by a different word
  skip              - one word left out
  stall             - the reader stops mid-line for 5 s, then carries on
  demo              - a stall and a wrong word in one reading (used by the app's Demo reader)

Only synthetic voices are used (challenge data rule). Each line is one TTS call and is
cached, so re-running costs nothing.

    python -m eval.make_testset
"""
import asyncio
import json
import random
import struct
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

from backend.content import load_library  # noqa: E402
from backend.gnani import TTS  # noqa: E402
from backend.normalize import similarity  # noqa: E402

OUT = ROOT / "eval" / "testset"
SR = 16000
VOICES = {"a": ("Riyaa", 0.9), "b": ("Devansh", 1.0)}
tts = TTS()


def pcm_of(path: Path) -> bytes:
    raw = path.read_bytes()
    i = raw.find(b"data")
    return raw[i + 8:] if i >= 0 else raw[44:]


def silence(sec: float) -> bytes:
    return bytes(int(sec * SR) * 2)


def write_wav(path: Path, pcm: bytes):
    hdr = b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt " + struct.pack(
        "<IHHIIHH", 16, 1, 1, SR, SR * 2, 2, 16) + b"data" + struct.pack("<I", len(pcm))
    path.write_bytes(hdr + pcm)


async def say(text: str, lang: str, voice_key: str) -> bytes:
    voice, speed = VOICES[voice_key]
    k = await tts.get(text, lang, speed, voice=voice, container="wav", sample_rate=SR)
    return pcm_of(tts.path(k, "wav"))


def pick_target(text, rng, exclude_lines=()):
    """A content word in the middle of a middle line (not the first word of a line)."""
    cands = [w for w in text.words
             if not w.short and not w.line_start and w.line not in exclude_lines and w.line > 0
             and not (w.idx > 0 and text.words[w.idx - 1].norm == w.norm)
             and w.idx < len(text.words) - 1]
    if not cands:
        return pick_target(text, rng)
    return rng.choice(cands)


def distractor(text, target, library, rng):
    pool = [w for t in library.values() if t.language == text.language and t.id != text.id
            for w in t.words if not w.short and len(w.loose) >= 2]
    pool = [w for w in pool if similarity(w.norm, target.norm) < 0.35]
    pool.sort(key=lambda w: abs(len(w.loose) - len(target.loose)))
    return rng.choice(pool[:15]).display.strip(",.!?;:।")


def line_text(text, li, replace=None, drop=None):
    a, b = text.line_range(li)
    out = []
    for w in text.words[a:b]:
        if drop is not None and w.idx == drop:
            continue
        out.append(replace[1] if replace and w.idx == replace[0] else w.display)
    return " ".join(out)


async def build(text, library, rng):
    lang, d = text.language, OUT / text.id
    d.mkdir(parents=True, exist_ok=True)
    nlines = len(text.line_words)
    sub_t = pick_target(text, rng)
    skip_t = pick_target(text, rng, exclude_lines={sub_t.line})
    stall_line = rng.choice([li for li in range(nlines) if text.line_range(li)[1] - text.line_range(li)[0] >= 4])
    a, b = text.line_range(stall_line)
    stall_at = a + (b - a) // 2  # reader stops before this word
    sub_word = distractor(text, sub_t, library, rng)
    long_pause_line = rng.randrange(0, nlines - 1)

    async def reading(variant, voice, mods):
        pcm, segs, truth = bytearray(silence(1.0)), [], []
        for li in range(nlines):
            la, lb = text.line_range(li)
            m = mods.get(li)
            pieces = [(line_text(text, li), list(range(la, lb)))]
            if m and m[0] == "sub":
                pieces = [(line_text(text, li, replace=(m[1], m[2])), list(range(la, lb)))]
                truth.append({"type": "sub", "word": m[1], "said": m[2]})
            elif m and m[0] == "skip":
                pieces = [(line_text(text, li, drop=m[1]), [i for i in range(la, lb) if i != m[1]])]
                truth.append({"type": "skip", "word": m[1]})
            elif m and m[0] == "stall":
                k = m[1]
                pieces = [(" ".join(w.display for w in text.words[la:k]), list(range(la, k))),
                          ("__STALL__", []),
                          (" ".join(w.display for w in text.words[k:lb]), list(range(k, lb)))]
            for ptext, idxs in pieces:
                if ptext == "__STALL__":
                    t0 = len(pcm) / 2 / SR
                    pcm += silence(5.0)
                    truth.append({"type": "stall", "word": m[1], "start": round(t0, 3), "end": round(t0 + 5.0, 3)})
                    continue
                audio = await say(ptext, lang, voice)
                t0 = len(pcm) / 2 / SR
                pcm += audio
                segs.append({"start": round(t0, 3), "end": round(len(pcm) / 2 / SR, 3), "words": idxs,
                             "line": li})
            last = li == nlines - 1
            if last:
                gap = 2.0
            elif text.words[text.line_range(li)[1] - 1].stanza_end:
                gap = 1.6
            elif variant == "clean_a" and li == long_pause_line:
                gap = 3.0  # a long, normal pause at a line end: must not trigger a prompt
            else:
                gap = 0.8 if voice == "a" else 0.6
            pcm += silence(gap)
        for t in truth:  # when the error happened in the audio
            if t["type"] in ("sub", "skip"):
                line = text.words[t["word"]].line
                t["segment_end"] = [s for s in segs if s["line"] == line][-1]["end"]
        write_wav(d / f"{variant}.wav", bytes(pcm))
        meta = {"text_id": text.id, "language": lang, "variant": variant, "voice": VOICES[voice][0],
                "duration": round(len(pcm) / 2 / SR, 2), "segments": segs, "truth": truth}
        (d / f"{variant}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
        return meta

    demo_sub_line = next((li for li in range(nlines) if li != stall_line and li > 0), 0)
    demo_target = pick_target(text, rng, exclude_lines={li for li in range(nlines) if li != demo_sub_line} or ())
    await reading("clean_a", "a", {})
    await reading("clean_b", "b", {})
    await reading("sub", "a", {sub_t.line: ("sub", sub_t.idx, sub_word)})
    await reading("skip", "b", {skip_t.line: ("skip", skip_t.idx)})
    await reading("stall", "a", {stall_line: ("stall", stall_at)})
    await reading("demo", "a", {stall_line: ("stall", stall_at),
                                demo_sub_line: ("sub", demo_target.idx, distractor(text, demo_target, library, rng))})
    print(f"{text.id}: sub {sub_t.display}->{sub_word}, skip {skip_t.display}, stall before {text.words[stall_at].display}")


async def main():
    library = load_library()
    rng = random.Random(7)
    for text in library.values():
        await build(text, library, rng)


if __name__ == "__main__":
    asyncio.run(main())
