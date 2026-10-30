"""Stream every test reading through Prisma (same settings as the app) and record the events.

Audio is sent at real-time pace in 1024-byte frames, exactly like the browser does, and
each server event is stamped with the audio time at which it arrived. The recordings are
replayed offline by eval/replay.py, so tuning the tutor costs no further credits.

    python -m eval.run_stt [--only en-kite] [--variants clean_a,sub] [--force]
"""
import argparse
import asyncio
import json
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

import websockets  # noqa: E402

from backend.gnani import STT_STREAM_URL, stt_headers, usage  # noqa: E402
from backend.tutor import TutorConfig  # noqa: E402

TESTSET = ROOT / "eval" / "testset"
RUNS = ROOT / "eval" / "runs" / "stt"
FRAME = 1024


async def stream(wav: Path, lang: str) -> dict:
    raw = wav.read_bytes()
    pcm = raw[44:] + bytes(16000)  # +0.5 s tail
    events = []
    silence_ms = TutorConfig().vad_silence_ms
    async with websockets.connect(STT_STREAM_URL, additional_headers=stt_headers(lang, silence_ms),
                                  max_size=2 ** 22) as ws:
        t0 = time.monotonic()
        done = asyncio.Event()

        async def send():
            n = len(pcm) // FRAME
            for i in range(n):
                target = t0 + i * 0.032
                delay = target - time.monotonic()
                if delay > 0:
                    await asyncio.sleep(delay)
                await ws.send(pcm[i * FRAME:(i + 1) * FRAME])
            await asyncio.sleep(2.5)
            done.set()
            await ws.close()

        async def recv():
            try:
                async for msg in ws:
                    m = json.loads(msg)
                    events.append({"t": round(time.monotonic() - t0, 3),
                                   **{k: m.get(k) for k in ("type", "text", "latency", "audio_duration_ms", "message")
                                      if m.get(k) is not None}})
            except websockets.ConnectionClosed:
                pass

        await asyncio.gather(send(), recv())
    usage.add(stt_stream_seconds=len(pcm) / 32000, stt_sessions=1)
    return {"events": events}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--variants", default="clean_a,clean_b,sub,skip,stall,demo")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--parallel", type=int, default=4)
    args = ap.parse_args()
    RUNS.mkdir(parents=True, exist_ok=True)
    jobs = []
    for d in sorted(TESTSET.iterdir()):
        if args.only and d.name != args.only:
            continue
        for v in args.variants.split(","):
            meta = json.loads((d / f"{v}.json").read_text())
            out = RUNS / f"{d.name}__{v}.json"
            if out.exists() and not args.force:
                continue
            jobs.append((d / f"{v}.wav", meta, out))
    print(f"{len(jobs)} readings to stream")
    sem = asyncio.Semaphore(args.parallel)

    async def run(wav, meta, out):
        async with sem:
            for attempt in range(3):
                try:
                    res = await stream(wav, meta["language"])
                    break
                except Exception as exc:
                    print(f"  retry {wav.parent.name}/{wav.name}: {exc}")
                    await asyncio.sleep(3)
            else:
                return
            out.write_text(json.dumps({**res, "meta": meta}, ensure_ascii=False, indent=1))
            texts = [e["text"] for e in res["events"] if e["type"] == "transcript"]
            print(f"  {wav.parent.name}/{wav.stem}: {' | '.join(texts)}")

    await asyncio.gather(*(run(*j) for j in jobs))


if __name__ == "__main__":
    asyncio.run(main())
