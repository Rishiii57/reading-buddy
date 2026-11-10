"""Simulated speech-to-text for automated testing (the AI child-user agents). OFF by default.

Enabled only when the server starts with RB_SIM=1. Then, instead of opening a Gnani Prisma
stream, a session whose WebSocket handshake carries the cookie `rb_sim=<token>` gets a
SimSTT. A test agent "speaks" by POSTing to /api/sim/utter with the same token:

    {"token": "...", "text": "i have a kite", "duration_s": 1.6}

SimSTT then behaves like Prisma does for the app: a `speech_start` event at once, and a
`transcript` event after the utterance plus the 300 ms end-of-speech silence and a typical
server latency. Words spoken while the browser mic is muted (Buddy talking, or paused) are
lost, exactly as the real frontend sends zeros then. No audio is sent anywhere and no
credits are used. The tutor engine, aligner, frontend and Timbre cache all run unchanged.

The speech itself (what the child says, and what the speech model would write for it) is
decided by the agent, not here. This module only reproduces Prisma's event timing.
"""
import asyncio
import json
import os
import time

SIM_ENABLED = os.environ.get("RB_SIM", "0") == "1"
LATENCY_MS = 120          # median server latency measured on Prisma (eval/RESULTS.md: 117 ms)
MAX_SPEECH_S = 8.0        # matches x-max-speech-s sent to Prisma

_registry: dict[str, "SimSTT"] = {}
_records: dict[str, dict] = {}  # token -> last finished session record (engine log, summary)


class SimSTT:
    """Duck-types the websockets client used by main.Session: async-iterable of JSON strings,
    send(bytes), close()."""

    def __init__(self, token: str, session, vad_silence_ms: int = 300):
        self.token = token
        self.session = session
        self.vad_s = vad_silence_ms / 1000.0
        self.q: asyncio.Queue = asyncio.Queue()
        self.closed = False
        self.frames = 0
        self.utterances: list[dict] = []
        _registry[token] = self
        self.q.put_nowait(json.dumps({"type": "connected", "message": "simulated STT ready"}))

    # --- websockets-like interface ---------------------------------------------------
    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.closed:
            raise StopAsyncIteration
        item = await self.q.get()
        if item is None:
            raise StopAsyncIteration
        return item

    async def send(self, data: bytes):
        self.frames += 1  # audio from the browser's (fake) mic is ignored

    async def close(self):
        self.closed = True
        self.q.put_nowait(None)
        if _registry.get(self.token) is self:
            del _registry[self.token]

    # --- speech ----------------------------------------------------------------------
    def _muted(self) -> bool:
        e = self.session.engine
        return bool(e.tutor_busy or e.paused)

    async def utter(self, text: str, duration_s: float) -> dict:
        """Play one utterance in real time; return what reached the speech model."""
        words = text.split()
        duration_s = max(0.25, min(float(duration_s), 30.0))
        t0 = time.monotonic()
        heard, muted_words, started = [], 0, False
        chunk_start = 0.0
        for i, w in enumerate(words):
            # word i is spoken at its share of the utterance time
            at = duration_s * i / max(1, len(words))
            await asyncio.sleep(max(0.0, t0 + at - time.monotonic()))
            if self.closed:
                break
            if self._muted():
                muted_words += 1
                continue
            if not started:
                started = True
                chunk_start = at
                self._emit({"type": "speech_start"})
            heard.append(w)
            if at - chunk_start >= MAX_SPEECH_S:  # Prisma cuts very long speech into segments
                await self._finish(heard, at - chunk_start)
                heard, started = [], False
        await asyncio.sleep(max(0.0, t0 + duration_s - time.monotonic()))
        if heard and not self.closed:
            await self._finish(heard, duration_s - chunk_start)
        rec = {"text": text, "heard": " ".join(heard), "muted_words": muted_words,
               "duration_s": duration_s}
        self.utterances.append(rec)
        return rec

    async def _finish(self, heard: list[str], dur: float):
        await asyncio.sleep(self.vad_s + LATENCY_MS / 1000.0)
        self._emit({"type": "transcript", "text": " ".join(heard), "latency": LATENCY_MS,
                    "audio_duration_ms": round(dur * 1000)})

    def _emit(self, msg: dict):
        if not self.closed:
            self.q.put_nowait(json.dumps(msg))


def lookup(token: str) -> "SimSTT | None":
    return _registry.get(token)


def store_record(token: str, record: dict) -> None:
    _records[token] = record


def get_record(token: str) -> dict | None:
    return _records.get(token)
