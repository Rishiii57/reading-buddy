"""FastAPI app: serves the web UI, the content library, cached tutor audio and the live session socket.

Browser --PCM16 16 kHz--> /ws/session --> Prisma v2.5 streaming STT
                                       <-- transcripts --> aligner + tutor rules
Browser <-- highlight state + Timbre audio clips to play --
"""
import asyncio
import json
import logging
import os
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import websockets  # noqa: E402
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from .content import LANGUAGES, load_library  # noqa: E402
from .gnani import CACHE_DIR, TTS, StreamClock, open_stt, usage  # noqa: E402
from .phrases import PHRASES  # noqa: E402
from . import sim  # noqa: E402
from .tutor import TutorConfig, TutorEngine  # noqa: E402

log = logging.getLogger("tutor")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
DEMO_DIR = ROOT / "eval" / "testset"
SESSIONS_DIR = CACHE_DIR / "sessions"
# Privacy: nothing about a session is written to disk unless a tester opts in (consenting
# team members only). SAVE_SESSIONS keeps the transcript log; SAVE_AUDIO also keeps the audio.
SAVE_SESSIONS = os.environ.get("SAVE_SESSIONS", "0") == "1"
SAVE_AUDIO = SAVE_SESSIONS and os.environ.get("SAVE_AUDIO", "0") == "1"
PREFETCH = os.environ.get("PREFETCH", "1") == "1"
SPAN_SPEED = 0.9  # a little slower for young readers
WORD_SPEED = 0.85  # a single practice word, said slowly and clearly

app = FastAPI(title="Voice Reading Tutor")
library = load_library()
tts = TTS()


def span_text(text, a: int, b: int) -> str:
    return " ".join(w.display for w in text.words[a:b]).strip(" ,;:")


async def clip_for(part, text) -> dict:
    lang = text.language
    if part[0] == "phrase":
        words = PHRASES[lang][part[1]]
        k = await tts.get(words, lang, 1.0)
    elif part[0] == "title":
        words = text.title
        k = await tts.get(words, lang, SPAN_SPEED)
    else:
        words = span_text(text, part[1], part[2])
        k = await tts.get(words, lang, WORD_SPEED if part[2] - part[1] == 1 else SPAN_SPEED)
        return {"url": f"/tts/{k}.mp3", "text": words, "span": [part[1], part[2]]}
    return {"url": f"/tts/{k}.mp3", "text": words}


@app.get("/api/library")
def get_library():
    out = {lang: [] for lang in LANGUAGES}
    for t in library.values():
        demo = (DEMO_DIR / t.id / "demo.json").exists()  # the interactive demo child's plan
        out[t.language].append({"id": t.id, "title": t.title, "title_en": t.title_en,
                                "type": t.type, "grade": t.grade, "words": len(t.words),
                                "demo": demo})
    return {"languages": LANGUAGES, "texts": out}


@app.get("/api/text/{text_id}")
def get_text(text_id: str):
    if text_id not in library:
        raise HTTPException(404)
    return library[text_id].public()


@app.get("/api/listen/{text_id}")
async def listen(text_id: str):
    """Audio for each line, so the child can hear the text read first."""
    if text_id not in library:
        raise HTTPException(404)
    t = library[text_id]
    clips = []
    for li, (a, b) in enumerate(t.line_words):
        c = await clip_for(("span", a, b), t)
        clips.append({**c, "line": li, "from": a, "to": b})
    return {"clips": clips}


DEMO_VOICE, DEMO_SPEED = "Riyaa", 0.9  # the synthetic "child" (a Timbre voice, never a real child)


@app.get("/api/demo/{text_id}/plan")
def demo_plan(text_id: str):
    """What the interactive demo child gets wrong: one substituted word and one mid-line stop
    (from the synthetic test set), so the demo shows word practice and a stall prompt."""
    f = DEMO_DIR / text_id / "demo.json"
    if text_id not in library or not f.exists():
        raise HTTPException(404)
    plan = {"mistake": None, "stall": None}
    for t in json.loads(f.read_text())["truth"]:
        if t["type"] == "sub":
            plan["mistake"] = {"word": t["word"], "said": t["said"], "line": library[text_id].words[t["word"]].line}
        elif t["type"] == "stall":
            plan["stall"] = {"word": t["word"], "line": library[text_id].words[t["word"]].line}
    return plan


@app.get("/api/demo/{text_id}/say")
async def demo_say(text_id: str, a: int, b: int, swap: int = -1, said: str = ""):
    """16 kHz WAV of the demo child reading words a..b-1 (optionally with one word swapped)."""
    if text_id not in library:
        raise HTTPException(404)
    t = library[text_id]
    if not (0 <= a < b <= len(t.words)) or len(said) > 40:
        raise HTTPException(400)
    words = [said if i == swap and said else t.words[i].display for i in range(a, b)]
    k = await tts.get(" ".join(words), t.language, DEMO_SPEED, voice=DEMO_VOICE, container="wav", sample_rate=16000)
    f = tts.path(k, "wav")
    if not f.exists() and tts.offline:
        f = tts.offline_dir / f.name
    return FileResponse(f, media_type="audio/wav")


@app.get("/api/usage")
def get_usage():
    return usage.data


@app.get("/tts/{name}")
def tts_file(name: str):
    if "/" in name or ".." in name:
        raise HTTPException(400)
    f = CACHE_DIR / "tts" / name
    if not f.exists() and tts.offline:
        f = tts.offline_dir / name  # placeholder clip (offline test mode only)
    if not f.exists():
        raise HTTPException(404)
    return FileResponse(f, media_type="audio/mpeg", headers={"Cache-Control": "public, max-age=31536000"})


if sim.SIM_ENABLED:
    from pydantic import BaseModel

    class Utterance(BaseModel):
        token: str
        text: str
        duration_s: float

    @app.post("/api/sim/utter")
    async def sim_utter(u: Utterance):
        """Test agents only: 'say' something into the session that holds this token."""
        s = sim.lookup(u.token)
        if s is None:
            raise HTTPException(404, "no live simulated session for this token")
        return await s.utter(u.text, u.duration_s)

    @app.get("/api/sim/record/{token}")
    def sim_record(token: str):
        r = sim.get_record(token)
        if r is None:
            raise HTTPException(404)
        return r


@app.get("/healthz")
def healthz():
    return JSONResponse({"ok": True, "texts": len(library)})


class Session:
    def __init__(self, ws: WebSocket, text_id: str, mode: str):
        self.ws = ws
        # automated testing only (RB_SIM=1): the agent's token, from the rb_sim cookie
        self.sim_token = ws.cookies.get("rb_sim") if sim.SIM_ENABLED else None
        self.text = library[text_id]
        self.mode = mode
        self.id = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
        self.cfg = TutorConfig()
        self.t0 = time.monotonic()
        self.engine = TutorEngine(self.text, self.cfg, now=self.now())
        self.stt = None
        self.clock = StreamClock()
        self.closed = False
        self.say_ids: dict[str, float] = {}
        self.audio = bytearray() if SAVE_AUDIO else None
        self.stt_events: list[dict] = []
        self.prefetched: set[tuple] = set()

    def now(self) -> float:
        return time.monotonic() - self.t0

    async def send(self, msg: dict):
        if not self.closed:
            try:
                await self.ws.send_text(json.dumps(msg, ensure_ascii=False))
            except Exception:
                self.closed = True

    async def send_state(self):
        await self.send({"type": "state", **self.engine.snapshot(),
                         "speaking": self.engine.speaking, "tutor_busy": self.engine.tutor_busy})

    async def handle_actions(self, actions: list[dict]):
        if not actions:
            return
        for a in actions:
            if a["type"] == "say":
                sid = uuid.uuid4().hex[:8]
                try:
                    clips = [await clip_for(p, self.text) for p in a["parts"]]
                except Exception as exc:  # TTS failure must not kill the session
                    log.warning("tts failed: %s", exc)
                    self.engine.on_tutor_audio_end(self.now())
                    continue
                self.say_ids[sid] = self.now()
                await self.send({"type": "say", "id": sid, "kind": a["kind"], "clips": clips,
                                 "text": " ".join(c["text"] for c in clips)})
            elif a["type"] == "summary":
                await self.send({"type": "summary", "summary": a["summary"]})
            elif a["type"] == "pause":  # the child asked for a break
                await self.send({"type": "auto_pause"})
        await self.send_state()
        if PREFETCH:
            asyncio.create_task(self.prefetch())

    async def prefetch(self):
        """Synthesise what Buddy may say next (the current line, the words to practise),
        so a prompt or a practice word plays without waiting for synthesis."""
        e, t = self.engine, self.text
        if e.done:
            return
        line = t.line_range(min(e.line, len(t.line_words) - 1))
        parts = [("span", *line)] + [("span", j, j + 1) for j in e.drill]
        if e.mode == "read" and e.p < len(t.words):
            parts += [("span", e.p, e._phrase_end(e.p)), ("span", e.p, line[1])]
        for part in parts:
            if part in self.prefetched:
                continue
            self.prefetched.add(part)
            try:
                await clip_for(part, t)
            except Exception as exc:
                log.warning("prefetch failed: %s", exc)

    async def warm_up(self):
        lang = self.text.language
        await asyncio.gather(*(tts.get(s, lang, 1.0) for s in PHRASES[lang].values()),
                             clip_for(("title",), self.text), return_exceptions=True)
        await self.prefetch()

    async def connect_stt(self):
        if self.sim_token:
            self.stt = sim.SimSTT(self.sim_token, self, self.cfg.vad_silence_ms)
            return
        self.stt = await open_stt(self.text.language, self.cfg.vad_silence_ms)

    async def stt_reader(self):
        while not self.closed:
            try:
                async for raw in self.stt:
                    m = json.loads(raw)
                    kind = m.get("type")
                    now = self.now()
                    self.stt_events.append({"t": round(now, 3), **{k: m.get(k) for k in
                                            ("type", "text", "latency", "audio_duration_ms", "message")}})
                    if kind == "speech_start":
                        self.engine.on_speech_start(now)
                        await self.send({"type": "speech", "speaking": True})
                    elif kind == "transcript":
                        await self.send({"type": "heard", "text": m.get("text", "")})
                        acts = self.engine.on_transcript(m.get("text", ""), now, m.get("latency") or 0,
                                                         m.get("audio_duration_ms"))
                        await self.send({"type": "speech", "speaking": False})
                        await self.handle_actions(acts or [{"type": "progress"}])
                    elif kind == "error":
                        log.warning("stt error: %s", m.get("message"))
            except websockets.ConnectionClosed as exc:
                log.info("stt closed: %s", exc)
            if self.closed or self.engine.done:
                return
            await asyncio.sleep(0.2)  # session cap or idle timeout: reconnect
            try:
                await self.connect_stt()
            except Exception as exc:
                log.warning("stt reconnect failed: %s", exc)
                await self.send({"type": "error", "message": "Speech service disconnected."})
                return

    async def ticker(self):
        while not self.closed and not self.engine.done:
            await asyncio.sleep(0.1)
            await self.handle_actions(self.engine.tick(self.now()))

    async def on_audio(self, data: bytes):
        self.clock.frame()
        if self.audio is not None:
            self.audio.extend(data)
        if self.stt is not None:
            try:
                await self.stt.send(data)
            except websockets.ConnectionClosed:
                pass

    def on_control(self, msg: dict):
        kind = msg.get("type")
        if kind == "live":  # microphone permission granted and audio flowing
            self.engine.restart_clock(self.now())
        elif kind == "pause":
            self.engine.pause(self.now())
        elif kind == "resume":
            self.engine.resume(self.now())
        elif kind == "audio_start":
            self.engine.on_tutor_audio_start(self.now())
        elif kind == "audio_done":
            self.say_ids.pop(msg.get("id"), None)
            self.engine.on_tutor_audio_end(self.now())

    def save(self):
        if self.sim_token:  # simulated sessions: no credits used; keep the record for the test agent
            sim.store_record(self.sim_token, {
                "id": self.id, "text_id": self.text.id, "mode": self.mode,
                "summary": self.engine.summary(self.now()), "log": self.engine.log,
                "stt_events": self.stt_events, "utterances": getattr(self.stt, "utterances", []),
                "tts_offline": tts.offline_count})
            return
        usage.add(stt_stream_seconds=self.clock.seconds)
        if not SAVE_SESSIONS:
            return
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        record = {"id": self.id, "text_id": self.text.id, "mode": self.mode,
                  "summary": self.engine.summary(self.now()), "log": self.engine.log,
                  "stt_events": self.stt_events}
        (SESSIONS_DIR / f"{self.id}.json").write_text(json.dumps(record, ensure_ascii=False, indent=1))
        if self.audio:
            (SESSIONS_DIR / f"{self.id}.pcm").write_bytes(bytes(self.audio))


@app.websocket("/ws/session")
async def session_ws(ws: WebSocket):
    await ws.accept()
    try:
        start = json.loads(await ws.receive_text())
    except (WebSocketDisconnect, ValueError):
        return
    text_id = start.get("text_id")
    if start.get("type") != "start" or text_id not in library:
        await ws.send_text(json.dumps({"type": "error", "message": "Unknown text."}))
        await ws.close()
        return
    s = Session(ws, text_id, start.get("mode", "mic"))
    warm = asyncio.create_task(s.warm_up())
    try:
        await s.connect_stt()
    except Exception as exc:
        warm.cancel()
        log.exception("could not start session")
        await s.send({"type": "error", "message": f"Could not reach the speech service: {exc}"})
        await ws.close()
        return
    s.engine.restart_clock(s.now())  # the reader starts once the microphone is live
    tasks = [warm, asyncio.create_task(s.stt_reader()), asyncio.create_task(s.ticker())]
    await s.send({"type": "ready", "session": s.id})
    await s.send_state()
    try:
        while True:
            msg = await ws.receive()
            if msg["type"] == "websocket.disconnect":
                break
            if msg.get("bytes") is not None:
                await s.on_audio(msg["bytes"])
            elif msg.get("text"):
                data = json.loads(msg["text"])
                if data.get("type") == "stop":
                    if not s.engine.done:
                        await s.send({"type": "summary", "summary": s.engine.summary(s.now())})
                    break
                s.on_control(data)
                if data.get("type") == "live":  # microphone is on: greet and demonstrate the opening line
                    await s.handle_actions(s.engine.start(s.now()))
                elif data.get("type") in ("audio_done", "pause", "resume"):
                    await s.send_state()
    except WebSocketDisconnect:
        pass
    finally:
        s.closed = True
        for t in tasks:
            t.cancel()
        if s.stt is not None:
            await s.stt.close()
        s.save()
        try:
            await ws.close()
        except Exception:
            pass


app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
