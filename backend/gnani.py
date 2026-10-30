"""Gnani API clients: Timbre text-to-speech (cached) and Prisma streaming speech-to-text."""
import asyncio
import hashlib
import json
import os
import time
from pathlib import Path

import httpx
import websockets

API_BASE = "https://api.vachana.ai"
STT_STREAM_URL = "wss://api.vachana.ai/stt/v3/stream"
CACHE_DIR = Path(os.environ.get("CACHE_DIR", Path(__file__).resolve().parent.parent / "cache"))
TTS_DIR = CACHE_DIR / "tts"
USAGE_FILE = CACHE_DIR / "usage.json"

TTS_MODEL = os.environ.get("TTS_MODEL", "timbre-v3.0")
TTS_VOICE = os.environ.get("TTS_VOICE", "Lakshmi")
STT_MODEL = os.environ.get("STT_MODEL", "prisma-v2.5")


def api_key() -> str:
    key = os.environ.get("GNANI_API_KEY", "")
    if not key:
        raise RuntimeError("GNANI_API_KEY is not set (see .env.example)")
    return key


class Usage:
    """Local ledger of API use, so credit spend can be checked against the dashboard."""

    def __init__(self):
        self.data = {"tts_calls": 0, "tts_chars": 0, "stt_stream_seconds": 0.0, "stt_sessions": 0}
        if USAGE_FILE.exists():
            self.data.update(json.loads(USAGE_FILE.read_text()))

    def add(self, **kw):
        for k, v in kw.items():
            self.data[k] = round(self.data.get(k, 0) + v, 2)
        USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        USAGE_FILE.write_text(json.dumps(self.data, indent=1))


usage = Usage()


class TTS:
    """Timbre REST synthesis with a permanent on-disk cache: each phrase costs one call, ever."""

    def __init__(self):
        TTS_DIR.mkdir(parents=True, exist_ok=True)
        self._client = httpx.AsyncClient(timeout=30)
        self._inflight: dict[str, asyncio.Future] = {}
        self._slots = asyncio.Semaphore(int(os.environ.get("TTS_CONCURRENCY", "2")))  # API rate limit

    @staticmethod
    def key(text: str, lang: str, speed: float, voice: str = TTS_VOICE, model: str = TTS_MODEL,
            container: str = "mp3", sample_rate: int = 24000) -> str:
        raw = f"{model}|{voice}|{lang}|{speed}|{container}|{sample_rate}|{text.strip()}"
        return hashlib.sha1(raw.encode()).hexdigest()[:20]

    def path(self, key: str, container: str = "mp3") -> Path:
        return TTS_DIR / f"{key}.{container}"

    async def get(self, text: str, lang: str, speed: float = 1.0, voice: str = TTS_VOICE,
                  model: str = TTS_MODEL, container: str = "mp3", sample_rate: int = 24000) -> str:
        """Return the cache key for this utterance, synthesising it on first use."""
        k = self.key(text, lang, speed, voice, model, container, sample_rate)
        if self.path(k, container).exists():
            return k
        if k in self._inflight:
            await self._inflight[k]
            return k
        fut = asyncio.get_running_loop().create_future()
        self._inflight[k] = fut
        try:
            audio_config = {"sample_rate": sample_rate, "num_channels": 1, "sample_width": 2}
            if container == "mp3":
                audio_config.update(container="mp3", bitrate="64k")
            else:
                audio_config.update(container=container, encoding="linear_pcm")
            body = {"text": text, "voice": voice, "model": model, "language": lang,
                    "speed": speed, "audio_config": audio_config}
            for attempt in range(7):
                async with self._slots:
                    r = await self._client.post(f"{API_BASE}/api/v1/tts/inference", json=body,
                                                headers={"X-API-Key-ID": api_key()})
                if r.status_code == 429 and attempt < 6:
                    wait = r.headers.get("retry-after")
                    await asyncio.sleep(float(wait) if wait and wait.replace(".", "").isdigit()
                                        else min(8.0, 0.6 * 2 ** attempt))
                    continue
                r.raise_for_status()
                break
            tmp = self.path(k, container).with_suffix(".part")
            tmp.write_bytes(r.content)
            tmp.rename(self.path(k, container))
            usage.add(tts_calls=1, tts_chars=len(text))
            fut.set_result(k)
            return k
        except Exception as exc:
            fut.set_exception(exc)
            fut.exception()  # mark retrieved
            raise
        finally:
            self._inflight.pop(k, None)


def stt_headers(lang: str, vad_silence_ms: int = 300) -> dict:
    return {
        "x-api-key-id": api_key(),
        "language_code": lang,
        "model": STT_MODEL,
        "x-sample-rate": "16000",
        "x-vad-threshold": os.environ.get("STT_VAD_THRESHOLD", "0.5"),
        "x-min-silence-ms": str(vad_silence_ms),
        "x-max-speech-s": "8",
        "x-idle-timeout-sec": "300",
        "format": "verbatim",
    }


async def open_stt(lang: str, vad_silence_ms: int = 300):
    """Open a Prisma streaming session. Caller sends 1024-byte PCM16 frames at 16 kHz."""
    ws = await websockets.connect(STT_STREAM_URL, additional_headers=stt_headers(lang, vad_silence_ms),
                                  max_size=2 ** 22, ping_interval=20)
    usage.add(stt_sessions=1)
    return ws


class StreamClock:
    """Tracks how much audio was streamed, for the usage ledger."""

    def __init__(self):
        self.frames = 0
        self.t0 = time.monotonic()

    def frame(self):
        self.frames += 1

    @property
    def seconds(self) -> float:
        return self.frames * 512 / 16000
