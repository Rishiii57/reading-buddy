"""Run a batch of child agents against a running Reading Buddy (one testing cycle's user study).

    python -m agent_org.orchestrator --cycle c01 --agents 5 --parallel 2
    python -m agent_org.orchestrator --cycle c01 --ids N01,L01 --parallel 1
    python -m agent_org.orchestrator --cycle c02 --agents 50 --parallel 4 --app-root ../rb-candidate

Defaults are cheap and safe: the app is started in simulation mode (RB_SIM=1: simulated
speech-to-text, RB_TTS_OFFLINE=1: placeholder audio for uncached lines), so a run uses no
Gnani credits and no LLM tokens. Agents run in independent browser contexts (separate cookies,
storage and session token) with bounded parallelism, are retried on harness errors, and
everything is written under agent_org/runs/<cycle>/.

Status:  agent_org/runs/<cycle>/status.json   (live, per agent)
Ledger:  agent_org/runs/<cycle>/ledger.json   (wall time, sessions, credits, tokens)
"""
import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import httpx

from .child_agent.driver import ChildAgent
from .personas.persona import load, select

ROOT = Path(__file__).resolve().parent.parent
RUNS = Path(__file__).resolve().parent / "runs"
CHROMIUM_ARGS = ["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream",
                 "--autoplay-policy=no-user-gesture-required", "--mute-audio"]


class AppServer:
    """Starts the app from a checkout (repo root or a git worktree) in simulation mode."""

    def __init__(self, app_root: Path, port: int, log_file: Path):
        self.app_root, self.port, self.log_file = app_root, port, log_file
        self.proc = None

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def __enter__(self):
        env = {**os.environ, "RB_SIM": "1", "RB_TTS_OFFLINE": "1", "PREFETCH": "1"}
        env.pop("GNANI_API_KEY", None)  # simulation runs must not be able to spend credits
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self._log = open(self.log_file, "w")
        self.proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--port", str(self.port),
                                      "--log-level", "warning"], cwd=self.app_root, env=env,
                                     stdout=self._log, stderr=subprocess.STDOUT)
        for _ in range(100):
            try:
                if httpx.get(self.url + "/healthz", timeout=1).status_code == 200:
                    return self
            except Exception:
                pass
            time.sleep(0.2)
        self.__exit__(None, None, None)
        raise RuntimeError(f"app did not start from {self.app_root}; see {self.log_file}")

    def __exit__(self, *a):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self._log.close()


class Status:
    def __init__(self, path: Path, ids: list[str]):
        self.path = path
        self.data = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "agents": {i: {"state": "queued"} for i in ids}}
        self.save()

    def set(self, aid: str, **kw):
        self.data["agents"][aid].update(kw)
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.data, indent=1))


async def run_agent(persona, base: str, out: Path, run_id: str, browser_factory, status: Status, retries: int,
                    seed: int | None, screenshots: bool) -> dict:
    last = None
    for attempt in range(retries + 1):
        status.set(persona.id, state="running", attempt=attempt + 1, since=time.strftime("%H:%M:%S"))
        d = out / persona.id
        if d.exists():
            shutil.rmtree(d)
        browser = await browser_factory()
        try:
            agent = ChildAgent(persona, base, d, run_id, seed=seed, screenshots=screenshots)
            last = await agent.run(browser)
        except Exception as exc:  # the agent itself crashed
            last = {"agent_id": persona.id, "outcome": "harness_error", "harness_error": repr(exc)[:300]}
        finally:
            await browser.close()
        if last.get("outcome") != "harness_error":
            break
        status.set(persona.id, state="retrying", error=last.get("harness_error"))
    status.set(persona.id, state="done", outcome=last.get("outcome"), issues=len(last.get("experience", {}).get("issues", [])))
    return last


async def run_batch(personas, base: str, out: Path, run_id: str, parallel: int, retries: int,
                    seed: int | None, screenshots: bool) -> list[dict]:
    from playwright.async_api import async_playwright
    status = Status(out / "status.json", [p.id for p in personas])
    sem = asyncio.Semaphore(parallel)
    async with async_playwright() as pw:
        async def factory():
            return await pw.chromium.launch(args=CHROMIUM_ARGS)

        async def one(p):
            async with sem:
                return await run_agent(p, base, out, run_id, factory, status, retries, seed, screenshots)
        return await asyncio.gather(*(one(p) for p in personas))


def summarise(reports: list[dict], personas, wall_s: float, mode: str) -> dict:
    outcomes = {}
    for r in reports:
        outcomes[r.get("outcome")] = outcomes.get(r.get("outcome"), 0) + 1
    completed = sum(1 for r in reports if r.get("outcome") == "completed")
    abandoned = sum(1 for r in reports if str(r.get("outcome", "")).startswith(("abandoned", "could_not", "left")))
    child_talk = sum((r.get("metrics") or {}).get("child_talk_s", 0) for r in reports)
    session_s = sum((r.get("metrics") or {}).get("session_s", 0) or 0 for r in reports)
    return {"agents": len(reports), "completed": completed, "abandoned_or_failed": abandoned,
            "harness_errors": outcomes.get("harness_error", 0), "outcomes": outcomes,
            "ledger": {"mode": mode, "wall_s": round(wall_s, 1), "gnani_credits": 0 if mode == "sim" else None,
                       "stt_stream_s_if_live": round(session_s, 1),
                       "note": "In sim mode no Prisma/Timbre calls are made. stt_stream_s_if_live is how many seconds "
                               "of audio the same sessions would stream to Prisma if run live (sessions stream for "
                               "their whole length, including Buddy's talking time).",
                       "child_speech_s": round(child_talk, 1), "llm_tokens": 0,
                       "llm_note": "Child agents, PM, QA scoring are deterministic code; no LLM calls."}}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", required=True, help="cycle id, e.g. c01")
    ap.add_argument("--label", default="baseline", help="run label inside the cycle (baseline, retest, qa-before, ...)")
    ap.add_argument("--agents", type=int, help="how many personas (spread across grades and languages)")
    ap.add_argument("--ids", help="comma-separated persona ids")
    ap.add_argument("--grades", help="comma-separated grades")
    ap.add_argument("--parallel", type=int, default=2)
    ap.add_argument("--retries", type=int, default=1)
    ap.add_argument("--seed", type=int, help="override every persona's seed")
    ap.add_argument("--seed-offset", type=int, default=0, help="add to each persona's own seed (repeat runs)")
    ap.add_argument("--port", type=int, default=8790)
    ap.add_argument("--app-root", default=str(ROOT), help="checkout to test (repo root or a git worktree)")
    ap.add_argument("--base-url", help="use an already-running app instead of starting one")
    ap.add_argument("--no-screens", action="store_true")
    a = ap.parse_args(argv)
    if a.parallel > 6:
        sys.exit("refusing --parallel > 6: each agent runs a real browser and session in real time")
    personas = select(load(), ids=a.ids.split(",") if a.ids else None, n=a.agents,
                      grades=a.grades.split(",") if a.grades else None)
    if not personas:
        sys.exit("no personas selected")
    out = RUNS / a.cycle / a.label
    out.mkdir(parents=True, exist_ok=True)
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=a.app_root, capture_output=True, text=True).stdout.strip()
    meta = {"cycle": a.cycle, "label": a.label, "app_root": a.app_root, "app_commit": commit,
            "personas": [p.id for p in personas], "parallel": a.parallel, "seed": a.seed, "seed_offset": a.seed_offset,
            "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    (out / "run.json").write_text(json.dumps(meta, indent=1))
    print(f"[{a.cycle}/{a.label}] {len(personas)} agents, parallel {a.parallel}, app {commit} -> {out}", flush=True)
    t0 = time.monotonic()
    run_id = f"{a.cycle}-{a.label}"
    seed = a.seed
    if a.seed_offset:
        for p in personas:
            p.seed += a.seed_offset
    if a.base_url:
        reports = asyncio.run(run_batch(personas, a.base_url, out, run_id, a.parallel, a.retries, seed, not a.no_screens))
    else:
        with AppServer(Path(a.app_root), a.port, out / "server.log") as srv:
            reports = asyncio.run(run_batch(personas, srv.url, out, run_id, a.parallel, a.retries, seed, not a.no_screens))
    summary = summarise(reports, personas, time.monotonic() - t0, "sim")
    meta.update(finished=time.strftime("%Y-%m-%dT%H:%M:%S"), summary=summary)
    (out / "run.json").write_text(json.dumps(meta, indent=1))
    (out / "ledger.json").write_text(json.dumps(summary["ledger"], indent=1))
    print(json.dumps(summary, indent=1))
    return out


if __name__ == "__main__":
    main()
