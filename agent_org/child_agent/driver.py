"""One simulated child using the real Reading Buddy app in a real browser (Playwright/Chromium).

Blind by construction: the agent never reads the repo, the docs or other agents' reports. It
perceives only what a child would:
  * the visible screen: active view, visible buttons and their labels, the speech bubble,
    which word is highlighted, whether Buddy is talking (the mic dock animation);
  * Buddy's voice: the lines Buddy speaks (taken from the audio messages the page receives;
    the agent never looks at the tutor's internal state).
Labels are only "readable" to the extent the persona can read English (the UI language) or
the script on a card; otherwise the child taps by size and colour, as young children do.

The child speaks through the simulated speech channel (backend/sim.py, zero credits). All
taps, speech, Buddy reactions and frustration events are recorded as evidence.
"""
import asyncio
import json
import random
import re
import time
from pathlib import Path

import httpx

from .affect import Affect
from .speech_model import clean, read_attempt, stt_channel

LANG_NAME = {"en-IN": "English", "hi-IN": "Hindi", "gu-IN": "Gujarati"}
TIRED = {"en-IN": "I am tired", "hi-IN": "मैं थक गया", "gu-IN": "હું થાકી ગયો"}
LANG_LABEL = {"en-IN": ["english"], "hi-IN": ["हिन्दी", "hindi"], "gu-IN": ["ગુજરાતી", "gujarati"]}
CORRECTION_KINDS = {"fix_word", "fix_next", "fix_again"}

OBSERVE_JS = r"""() => {
  document.querySelectorAll('[data-rb-agent]').forEach((e) => e.removeAttribute('data-rb-agent'));
  const vis = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 4 && r.height > 4 && s.visibility !== 'hidden' && s.display !== 'none' && !el.closest('[hidden]'); };
  const dlg = document.querySelector('dialog[open]');
  const view = document.querySelector('.view.is-active');
  const root = dlg || document;
  const els = [...root.querySelectorAll('button, a[href], [role=tab], input[type=checkbox]')]
    .filter((e) => vis(e) && !e.disabled && (dlg || e.closest('.view.is-active') || e.closest('.topnav')));
  const clickables = els.map((e, i) => { e.dataset.rbAgent = 'a' + i; const r = e.getBoundingClientRect();
    return { aid: 'a' + i, text: (e.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 80),
             aria: e.getAttribute('aria-label') || '', area: Math.round(r.width * r.height),
             cls: String(e.className || ''), id: e.id || '', tag: e.tagName.toLowerCase(),
             lang: e.dataset.lang || '', grade: e.dataset.grade || '', story: e.dataset.id || '',
             inView: r.bottom > 0 && r.top < innerHeight }; });
  const t = (id) => { const e = document.getElementById(id); return e && vis(e) ? e.textContent.trim() : ''; };
  const cur = document.querySelector('.w.is-current'); const tgt = document.querySelector('.w.is-target');
  return { view: view ? view.id : null, hash: location.hash, dialog: dlg ? dlg.id : null,
    dock: document.getElementById('micDock')?.dataset.state || null,
    bubbleLabel: t('bubbleLabel'), bubbleText: t('bubbleText'), toast: t('toast'),
    current: cur ? +cur.id.slice(1) : null, target: tgt ? +tgt.id.slice(1) : null,
    listenLabel: document.getElementById('listenBtn')?.innerText.trim() || '',
    clickables };
}"""

STATE_JS = r"""() => ({ view: document.querySelector('.view.is-active')?.id || null, hash: location.hash,
  dialog: document.querySelector('dialog[open]')?.id || null, dock: document.getElementById('micDock')?.dataset.state || null })"""

# The child's ears: record every sound the page starts playing (time and length). Perception only:
# it does not change what the app does.
EARS_JS = r"""(() => { try { const S = AudioBufferSourceNode.prototype.start; window.__rbHeard = [];
  AudioBufferSourceNode.prototype.start = function (...a) {
    try { window.__rbHeard.push({ t: performance.now(), dur: this.buffer ? this.buffer.duration : 0 }); } catch (e) {}
    return S.apply(this, a); }; } catch (e) {} })();"""

WORDS_JS = r"""() => [...document.querySelectorAll('#passageInner .w')].map((e) => ({
  i: +e.id.slice(1), t: e.textContent, line: +e.closest('.line').dataset.line }))"""


class ChildAgent:
    def __init__(self, persona, base_url: str, out_dir: Path, run_id: str, seed: int | None = None,
                 time_scale: float = 1.0, screenshots: bool = True):
        self.p = persona
        self.base = base_url.rstrip("/")
        self.out = out_dir
        self.run_id = run_id
        self.seed = persona.seed if seed is None else seed
        self.rng = random.Random(self.seed)
        self.token = re.sub(r"[^A-Za-z0-9_-]", "_", f"{run_id}-{persona.id}-{self.seed}")
        self.affect = Affect(persona.patience)
        self.t0 = time.monotonic()
        self.trace: list[dict] = []
        self.ws_log: list[dict] = []
        self.issues: dict[str, dict] = {}
        self.heard_words: dict[str, float] = {}     # word -> last time Buddy said it
        self.buddy_said: list[dict] = []
        self.attempts: dict[int, list] = {}         # word idx -> attempts (ground truth)
        self.drill_counts: dict[int, int] = {}
        self.corrections: list[dict] = []
        self.utterances: list[dict] = []
        self.understood_kinds: set = set()
        self.state_msgs = 0
        self.last_state: dict | None = None
        self.summary: dict | None = None
        self.outcome = "incomplete"
        self.metrics: dict = {"clicks": 0, "dead_clicks": 0, "nav_clicks": 0, "praise_heard": 0,
                              "interruptions": 0, "unheard_words": 0, "buddy_talk_s": 0.0,
                              "child_talk_s": 0.0, "tired_said": False}
        self.text_meta: dict = {}
        self.words: list[dict] = []
        self.screens_dir = out_dir / "screens"
        self.screenshots = screenshots
        self.shots: list[str] = []
        self.talking_since: float | None = None
        self.session_started_at: float | None = None
        self.first_word_at: float | None = None
        self.intro_done_at: float | None = None
        self.pause_planned = False

    # ----- bookkeeping -------------------------------------------------------------
    def now(self) -> float:
        return round(time.monotonic() - self.t0, 2)

    def log(self, kind: str, **data):
        self.trace.append({"t": self.now(), "kind": kind, **data})

    def issue(self, code: str, detail: str, evidence: dict | None = None, level: str = "observed"):
        """Record a problem the child ran into (first occurrence keeps the screenshot)."""
        rec = self.issues.setdefault(code, {"code": code, "count": 0, "evidence_level": level,
                                            "first_t": self.now(), "details": [], "evidence": []})
        rec["count"] += 1
        if len(rec["details"]) < 6:
            rec["details"].append(detail)
        if evidence and len(rec["evidence"]) < 6:
            rec["evidence"].append({"t": self.now(), **evidence})
        self.log("issue", code=code, detail=detail)
        return rec["count"] == 1

    async def shot(self, page, name: str):
        if not self.screenshots or len(self.shots) >= 12:
            return
        self.screens_dir.mkdir(parents=True, exist_ok=True)
        f = self.screens_dir / f"{len(self.shots):02d}-{name}.png"
        try:
            await page.screenshot(path=str(f))
            self.shots.append(str(f.relative_to(self.out)))
        except Exception:
            pass

    # ----- perception ----------------------------------------------------------------
    def on_frame(self, payload):
        if not isinstance(payload, str):
            return
        try:
            m = json.loads(payload)
        except ValueError:
            return
        t = self.now()
        kind = m.get("type")
        if kind == "state":
            self.state_msgs += 1
            self.last_state = m
            return
        entry = {"t": t, "type": kind}
        if kind == "say":
            entry.update(kind=m.get("kind"), text=m.get("text"),
                         spans=[c.get("span") for c in m.get("clips", []) if c.get("span")])
            self.buddy_said.append(entry)
            for w in (m.get("text") or "").split():
                self.heard_words[clean(w).lower()] = t
            if m.get("kind") == "praise" or m.get("kind") in ("fix_next", "finish"):
                self.metrics["praise_heard"] += 1
                self.affect.add("praise", t)
            if m.get("kind") in CORRECTION_KINDS:
                spans = [s for s in entry["spans"] if s and s[1] - s[0] == 1]
                if spans:
                    self.corrections.append({"t": t, "kind": m["kind"], "word": spans[0][0]})
        elif kind == "heard":
            entry["text"] = m.get("text")
        elif kind == "summary":
            self.summary = m.get("summary")
            entry["summary"] = self.summary
        elif kind in ("error", "auto_pause", "ready"):
            entry["message"] = m.get("message")
        self.ws_log.append(entry)

    async def observe(self, page) -> dict:
        try:
            return await page.evaluate(OBSERVE_JS)
        except Exception as exc:  # navigation in progress
            return {"view": None, "clickables": [], "error": str(exc)}

    def can_read_label(self, c: dict) -> bool:
        """Is this button label readable for this child?"""
        txt = (c["text"] + " " + c["aria"]).strip()
        if not txt:
            return False
        if c["lang"]:  # a language card in its own script
            return self.rng.random() < max(self.p.reads(c["lang"]), self.p.ui_english_reading * 0.8)
        return self.rng.random() < self.p.ui_english_reading

    def choose(self, cands: list[dict], want=None, avoid=None) -> dict | None:
        """want: predicate on a readable button. Non-readers tap by size and colour."""
        cands = [c for c in cands if not (avoid and avoid(c))]
        if not cands:
            return None
        if want:
            readable = [c for c in cands if want(c) and self.can_read_label(c)]
            if readable:
                return readable[0]
        def weight(c):
            w = max(c["area"], 1) ** 0.8
            if any(k in c["cls"] for k in ("btn--sun", "btn--xl", "mic", "lang-card", "story")):
                w *= 2.5
            if c["tag"] == "a" and "navpill" in c["cls"]:
                w *= 0.5
            if c.get("inView"):  # small children tap what they can see before they think of scrolling
                w *= 4
            return w
        ws = [weight(c) for c in cands]
        return self.rng.choices(cands, weights=ws, k=1)[0]

    async def state(self, page) -> dict:
        try:
            return await page.evaluate(STATE_JS)
        except Exception:
            return {}

    async def tap(self, page, c: dict, why: str) -> dict:
        before = await self.state(page)  # must not re-tag elements: c["aid"] refers to the last observation
        self.metrics["clicks"] += 1
        self.log("tap", target=c["text"][:40] or c["aria"][:40] or c["id"] or c["cls"][:30], why=why,
                 view=before.get("view"))
        # a child taps a spot on the screen: whatever is on top there gets the tap, animated or not
        tapped = False
        try:
            # the child scrolls to it (plain scroll: no waiting for animations to settle)
            box = await page.evaluate("""(aid) => { const e = document.querySelector(`[data-rb-agent="${aid}"]`);
                if (!e) return null; e.scrollIntoView({block: 'center', behavior: 'instant'});
                const r = e.getBoundingClientRect(); return {x: r.left, y: r.top, width: r.width, height: r.height}; }""",
                                      c["aid"])
            await asyncio.sleep(0.15)
            if box is None:
                raise RuntimeError("element gone before the tap")
            if box:
                x = box["x"] + box["width"] * self.rng.uniform(0.35, 0.65)
                y = box["y"] + box["height"] * self.rng.uniform(0.35, 0.65)
                await page.mouse.click(x, y)
                tapped = True
        except Exception as exc:
            self.log("tap_failed", error=str(exc)[:120])  # harness problem, not a product finding
            self.metrics["tap_failures"] = self.metrics.get("tap_failures", 0) + 1
            if self.metrics["tap_failures"] >= 3:
                raise RuntimeError(f"harness could not tap reliably: {exc}")
        await asyncio.sleep(0.6)
        after = await self.state(page)
        changed = (after.get("view"), after.get("hash"), after.get("dialog"), after.get("dock")) != \
                  (before.get("view"), before.get("hash"), before.get("dialog"), before.get("dock"))
        if tapped and not changed and c["tag"] != "input" and "chip" not in c["cls"]:
            self.metrics["dead_clicks"] += 1
            self.affect.add("dead_click", self.now(), target=c["text"][:40])
        return after

    # ----- the journey ------------------------------------------------------------------
    async def run(self, browser) -> dict:
        self.out.mkdir(parents=True, exist_ok=True)
        ctx = await browser.new_context(permissions=["microphone"], viewport={"width": 1280, "height": 860},
                                        locale="en-IN")
        await ctx.add_cookies([{"name": "rb_sim", "value": self.token, "url": self.base}])
        await ctx.add_init_script(EARS_JS)
        if self.p.grown_up_setup:  # a grown-up already said yes on this device
            await ctx.add_init_script("try{localStorage.setItem('rb.consent','1')}catch(e){}")
        page = await ctx.new_page()
        page.on("websocket", lambda ws: ws.on("framereceived", self.on_frame))
        page.on("pageerror", lambda e: self.log("page_error", error=str(e)[:200]))
        error = None
        try:
            await page.goto(self.base + "/", wait_until="domcontentloaded")
            await asyncio.sleep(1.0)
            await self.shot(page, "home")
            self.log("open_app", brief=self.p.public_brief())
            reached = await self.navigate_to_text(page)
            if reached:
                await self.reading_phase(page)
        except Exception as exc:  # harness failure: recorded, never hidden as a finding
            error = f"{type(exc).__name__}: {exc}"[:400]
            self.outcome = "harness_error"
            self.log("harness_error", error=error)
        finally:
            try:
                await self.shot(page, "end")
            except Exception:
                pass
            await ctx.close()
        record = await self.fetch_server_record()
        return self.build_report(record, error)

    async def navigate_to_text(self, page) -> bool:
        b = self.p.behaviour
        lang = self.p.language_preference
        explored = 0
        t_start = self.now()
        for _ in range(b.max_nav_clicks):
            o = await self.observe(page)
            v = o.get("view")
            if v == "view-reader":
                break
            cands = o["clickables"]
            if self.rng.random() < b.p_off_task_click and v != "view-library":
                c = self.choose(cands)
                if c:
                    self.metrics["nav_clicks"] += 1
                    await self.tap(page, c, "curious tap")
                    continue
            if v == "view-home":
                c = self.choose(cands, want=lambda c: (c["lang"] == lang) or re.search(r"start reading", c["text"], re.I))
            elif v == "view-languages":
                c = self.choose(cands, want=lambda c: c["lang"] == lang, avoid=lambda c: "btn--back" in c["cls"])
            elif v == "view-library":
                c = await self.pick_in_library(page, o, explored)
                explored += 1
            elif v in ("view-about", "view-summary"):
                c = self.choose(cands, want=lambda c: re.search(r"back|home|library", c["text"], re.I))
            else:
                c = self.choose(cands)
            if c is None:
                break
            self.metrics["nav_clicks"] += 1
            after = await self.tap(page, c, f"looking for something to read ({v})")
            if v != "view-reader" and after.get("view") == v and v != "view-library":
                self.affect.add("wrong_screen", self.now(), view=v)
            if self.affect.gave_up:
                break
        o = await self.observe(page)
        self.metrics["time_to_text_s"] = round(self.now() - t_start, 1)
        if o.get("view") != "view-reader":
            self.outcome = "abandoned_navigation"
            self.issue("NAV_TEXT_NOT_FOUND", f"Could not find a poem to read after {self.metrics['nav_clicks']} taps "
                       f"(last screen {o.get('view')}).", {"view": o.get("view"), "taps": self.metrics["nav_clicks"]})
            return False
        await asyncio.sleep(0.8)
        self.words = await page.evaluate(WORDS_JS)
        title = await page.evaluate("document.getElementById('textTitle').textContent")
        tags = await page.evaluate("[...document.querySelectorAll('#rbTags .tag')].map(e=>e.textContent)")
        self.text_meta = {"hash": o.get("hash"), "title": title, "tags": tags, "words": len(self.words),
                          "lines": len({w["line"] for w in self.words})}
        self.log("opened_text", **self.text_meta)
        await self.shot(page, "reader")
        text_lang = next((k for k, v in {"en-IN": "English", "hi-IN": "Hindi", "gu-IN": "Gujarati"}.items() if v in tags), None)
        self.text_meta["language"] = text_lang
        if text_lang and text_lang != lang:
            self.issue("WRONG_LANGUAGE_TEXT", f"Wanted {lang} but ended up on a {text_lang} text.",
                       {"wanted": lang, "got": text_lang, "title": title})
        grade_tag = next((t for t in tags if t.startswith("Grade") or t in ("Nursery", "LKG", "UKG")), "")
        self.text_meta["grade_tag"] = grade_tag
        if self.p.pre_primary and grade_tag not in ("Nursery", "LKG", "UKG"):
            self.issue("NO_TEXT_FOR_MY_LEVEL", f"{self.p.grade} child landed on a '{grade_tag}' text, made for "
                       "children who already read.", {"title": title, "grade_tag": grade_tag})
        return True

    async def pick_in_library(self, page, o, explored: int):
        lang = self.p.language_preference
        cands = o["clickables"]
        tabs = [c for c in cands if c["tag"] == "button" and c["lang"]]
        sel = await page.evaluate("document.querySelector('#libLangs [aria-selected=\"true\"]')?.dataset.lang")
        if sel != lang and tabs and explored < 3:
            mine = [c for c in tabs if c["lang"] == lang]
            if mine and self.can_read_label(mine[0]):
                return mine[0]
        if self.p.journey == "explore_and_read" and explored < 2 and self.p.ui_english_reading > 0.5:
            g = re.sub(r"\D", "", self.p.grade)
            chip = [c for c in cands if c["grade"] == g]
            if chip:
                return chip[0]
        stories = [c for c in cands if c["story"]]
        if not stories:
            return self.choose(cands)
        if self.p.ui_english_reading > 0.5 and not self.p.pre_primary:
            g = int(re.sub(r"\D", "", self.p.grade) or 1)
            fit = [c for c in stories if re.search(rf"grade {g}\b|grade \d-{g}\b|grade {g}-", c["aria"], re.I)]
            if "likes_poems" in self.p.learning_preferences or self.p.journey == "read_whole_poem":
                fit = [c for c in fit if "poem" in c["aria"]] or fit
            if fit:
                return self.rng.choice(fit)
        if "likes_poems" in self.p.learning_preferences:
            poems = [c for c in stories if "poem" in c["aria"]]
            if poems and self.rng.random() < 0.6:
                return self.rng.choice(poems)
        return self.choose(stories)

    # ----- reading ------------------------------------------------------------------------
    async def reading_phase(self, page):
        b, lang = self.p.behaviour, self.text_meta.get("language") or self.p.language_preference
        # what does a child who cannot read the screen learn here? listen for a few seconds first
        await asyncio.sleep(4.0)
        o = await self.observe(page)
        heard = await page.evaluate("(window.__rbHeard || []).filter(h => h.dur > 0.3).length")
        bubble = f"{o.get('bubbleLabel')} {o.get('bubbleText')}"
        script = "gu-IN" if re.search(r"[\u0A80-\u0AFF]", bubble) else "hi-IN" if re.search(r"[\u0900-\u097F]", bubble) else "en-IN"
        can_read_bubble = (self.p.ui_english_reading if script == "en-IN" else self.p.reads(script)) >= 0.3
        self.metrics["reader_page_audio_clips"] = heard
        if not heard and not can_read_bubble:
            self.issue("NO_SPOKEN_GUIDANCE_BEFORE_START", "On the reading page nothing was said out loud, and the "
                       f"written instructions ({LANG_NAME[script]}) are not something this child can read.",
                       {"bubble": bubble, "audio_clips_heard": heard})
            self.affect.add("not_understood", self.now(), what="reader page instructions")
        if self.p.journey == "listen_then_read" or "listen_first" in self.p.learning_preferences \
                or "needs_audio_for_everything" in self.p.learning_preferences:
            await self.listen_first(page, o)
        if not await self.start_session(page):
            return
        lines = sorted({w["line"] for w in self.words})
        tired_done = False
        replay_looked = False
        drill_said_at = -1.0
        line_tapped: set = set()
        while True:
            el = self.now() - (self.session_started_at or self.now())
            o = await self.observe(page)
            v, dock = o.get("view"), o.get("dock")
            if v == "view-summary" or self.summary is not None and v != "view-reader":
                self.outcome = "completed" if (self.summary or {}).get("finished") else "ended_early"
                await asyncio.sleep(1.0)
                await self.shot(page, "summary")
                if self.p.journey == "restart_session":
                    await self.restart_from_summary(page)
                break
            if v != "view-reader":
                self.outcome = "left_session"
                self.issue("LEFT_READING_BY_ACCIDENT", f"The child ended up on {v} in the middle of reading.", {"view": v})
                break
            if dock in ("idle", "error") and self.session_started_at and el > 5:
                if self.summary is not None:
                    self.outcome = "completed" if self.summary.get("finished") else "ended_early"
                else:
                    self.outcome = "session_stopped"
                    self.issue("SESSION_STOPPED_UNEXPECTEDLY", f"The reading stopped (mic state '{dock}') without the child ending it.",
                               {"dock": dock, "bubble": o.get("bubbleText")})
                break
            # attention and patience
            if el > self.p.attention_span_s or self.affect.gave_up:
                why = "attention" if el > self.p.attention_span_s else "frustration"
                await self.abandon(page, o, why)
                break
            if b.says_tired_after_s and el > b.says_tired_after_s and not tired_done and dock in ("listening", "hearing"):
                tired_done = True
                await self.say_tired(page, lang)
                continue
            # Buddy talking
            if dock == "talking":
                if self.talking_since is None:
                    self.talking_since = self.now()
                elif self.now() - self.talking_since > 12 and not self.issues.get("LONG_TUTOR_TALK"):
                    self.issue("LONG_TUTOR_TALK", "Buddy talked for over 12 s in one go before the child could read.",
                               {"talk_s": round(self.now() - self.talking_since, 1)})
                    self.affect.add("long_wait", self.now())
                await self.check_understanding(lang)
                if self.rng.random() < b.p_talk_over_buddy * 0.08 and o.get("current") is not None:
                    await self.speak_turn(page, o, lang, over_buddy=True)
                await asyncio.sleep(0.25)
                continue
            if self.talking_since is not None:
                self.metrics["buddy_talk_s"] += self.now() - self.talking_since
                self.talking_since = None
                if self.intro_done_at is None:
                    self.intro_done_at = self.now()
                    self.metrics["intro_s"] = round(self.intro_done_at - self.session_started_at, 1)
            await self.check_understanding(lang)
            if dock == "paused":
                await self.handle_pause(page, o)
                continue
            if dock == "connecting":
                await asyncio.sleep(0.3)
                continue
            if self.rng.random() < b.p_off_task_click * 0.3:
                await self.off_task(page, o)
                continue
            if (self.p.journey == "replay_line" or "wants_replay" in self.p.learning_preferences) and not replay_looked \
                    and any(s.get("kind") in ("intro", "repeat_line", "stall_rest") for s in self.buddy_said):
                replay_looked = True
                await self.look_for_replay(o)
            # the child's turn
            line_now = self.line_of(o.get("target") if o.get("target") is not None else o.get("current"))
            if (line_now not in line_tapped and self.rng.random() < b.p_tap_mic_to_talk):
                line_tapped.add(line_now)
                mic = next((c for c in o["clickables"] if c["id"] == "micBtn"), None)
                if mic:
                    self.log("tap_mic_to_talk")
                    await self.tap(page, mic, "tapping the microphone to talk")
                    continue
            if o.get("target") is not None:
                if self.now() - drill_said_at < 2.5:
                    await asyncio.sleep(0.25)
                    continue
                await self.drill_turn(page, o, lang)
                drill_said_at = self.now()
            elif o.get("current") is not None:
                await self.speak_turn(page, o, lang)
            else:
                await asyncio.sleep(0.3)
            if not lines:
                break
        self.metrics["session_s"] = round(self.now() - (self.session_started_at or self.now()), 1)

    def line_of(self, idx):
        if idx is None:
            return None
        return next((w["line"] for w in self.words if w["i"] == idx), None)

    async def listen_first(self, page, o):
        btn = next((c for c in o["clickables"] if c["id"] == "listenBtn"), None)
        if not btn:
            return
        if not (self.can_read_label(btn) or self.rng.random() < 0.35):
            if "needs_audio_for_everything" in self.p.learning_preferences:
                self.issue("LISTEN_FIRST_NOT_FOUND", "Wanted to hear the poem first but could not tell which button does that.",
                           {"label": btn["text"]})
            return
        await self.tap(page, btn, "wants to hear it first")
        t = self.now()
        while self.now() - t < 90:
            o2 = await self.observe(page)
            if "Listen first" in o2.get("listenLabel", "") and self.now() - t > 2:
                break
            await asyncio.sleep(0.4)
        heard_s = round(self.now() - t, 1)
        for w in self.words:
            self.heard_words[clean(w["t"]).lower()] = self.now()
        self.metrics["listen_first_s"] = heard_s
        self.log("listened_first", seconds=heard_s)
        if heard_s >= 90:
            self.issue("LISTEN_FIRST_STUCK", "Listen first did not finish within 90 s.", {"seconds": heard_s})

    async def start_session(self, page) -> bool:
        for attempt in range(3):
            o = await self.observe(page)
            mic = next((c for c in o["clickables"] if c["id"] == "micBtn"), None)
            want = lambda c: c["id"] == "micBtn" or re.search(r"start reading|tap to start", c["text"], re.I)
            c = mic if (mic and (self.can_read_label(mic) or self.rng.random() < 0.6)) else self.choose(o["clickables"], want=want)
            if c is None:
                break
            o2 = await self.tap(page, c, "trying to start reading")
            if o2.get("dialog") == "consentDlg":
                if not await self.handle_consent(page):
                    continue
            await asyncio.sleep(1.5)
            o3 = await self.observe(page)
            # a session is running only if the End button is live ("Listen first" also animates the mic dock)
            running = any(c["id"] == "endBtn" for c in o3["clickables"])
            if running and o3.get("dock") in ("connecting", "listening", "talking", "hearing"):
                self.session_started_at = self.now()
                self.log("session_started", tries=attempt + 1)
                return True
            if o3.get("view") != "view-reader":
                self.issue("LEFT_READING_BY_ACCIDENT", "Tapped something that left the reading page before starting.",
                           {"view": o3.get("view")})
                self.outcome = "left_before_start"
                return False
            if "Stop listening" in o3.get("listenLabel", ""):  # started 'Listen first' by mistake: it plays to the end
                self.log("listen_first_by_mistake")
                t = self.now()
                while self.now() - t < 90 and "Stop listening" in (await self.observe(page)).get("listenLabel", ""):
                    await asyncio.sleep(0.5)
                for w in self.words:
                    self.heard_words[clean(w["t"]).lower()] = self.now()
        self.outcome = "could_not_start"
        self.issue("COULD_NOT_START_SESSION", "Never managed to start a reading session.", {"tries": 3})
        return False

    async def handle_consent(self, page) -> bool:
        await self.shot(page, "consent")
        o = await self.observe(page)
        box = next((c for c in o["clickables"] if c["tag"] == "input"), None)
        yes = lambda: next((c for c in o["clickables"] if c["id"] == "consentYes"), None)
        if self.p.ui_english_reading >= 0.6 and box:
            # an older child reads the grown-up box and ticks it themself
            await self.tap(page, box, "ticking the box")
            o = await self.observe(page)
            y = yes()
            if y:
                await self.tap(page, y, "allowing the microphone")
            self.issue("CONSENT_SELF_APPROVED", "The parent-consent box was ticked by the child; nothing stops a child "
                       "from confirming they are the parent.", {"grade": self.p.grade}, level="observed")
            return True
        # cannot read it: taps something
        c = self.choose(o["clickables"])
        if c:
            await self.tap(page, c, "does not understand the grown-up box")
        self.issue("CONSENT_BLOCKS_CHILD", "A written grown-ups-only box appeared; the child could not read it and "
                   "could not start.", {"grade": self.p.grade, "tapped": c["text"] if c else None})
        self.affect.add("not_understood", self.now(), what="consent dialog")
        o = await self.observe(page)
        if o.get("dialog"):
            await page.keyboard.press("Escape")
        return False

    async def check_understanding(self, lang):
        for s in self.buddy_said:
            k = s.get("kind")
            if k in self.understood_kinds:
                continue
            self.understood_kinds.add(k)
            if self.p.speaks(lang) < 0.5:
                self.issue("BUDDY_LANGUAGE_NOT_UNDERSTOOD", f"Buddy spoke in {lang}, which this child understands "
                           f"poorly ({self.p.speaks(lang):.1f}).", {"kind": k, "said": (s.get("text") or "")[:80]})
                self.affect.add("not_understood", self.now(), say_kind=k)

    async def speak(self, text: str, duration: float) -> dict:
        async with httpx.AsyncClient(base_url=self.base, timeout=duration + 20) as c:
            r = await c.post("/api/sim/utter", json={"token": self.token, "text": text, "duration_s": duration})
            return r.json() if r.status_code == 200 else {"error": r.status_code, "heard": ""}

    async def speak_turn(self, page, o, lang, over_buddy=False):
        p0 = o["current"]
        line = self.line_of(p0)
        words = [(w["i"], w["t"]) for w in self.words if w["line"] == line and w["i"] >= p0]
        if not words:
            await asyncio.sleep(0.3)
            return
        recent = {w for w, t in self.heard_words.items() if self.now() - t < 25}
        attempts, segments, reached = read_attempt(words, lang, self.p, self.rng, recent)
        if reached == 0:
            # cannot read the next word and has not just heard it: silent, waiting for help
            stuck_from = self.now()
            while self.now() - stuck_from < 10:
                await asyncio.sleep(0.3)
                o2 = await self.observe(page)
                if o2.get("dock") == "talking" or o2.get("current") != p0:
                    break
            else:
                self.issue("STUCK_WITHOUT_HELP", "Could not read the next word and waited 10 s with no help.",
                           {"word": words[0][1]})
                self.affect.add("stuck", self.now())
            self.log("stuck", word=words[0][1], waited=round(self.now() - stuck_from, 1))
            return
        for k, seg in enumerate(segments):
            heard, notes = stt_channel(seg.text, lang, self.p, self.rng)
            if self.first_word_at is None:
                self.first_word_at = self.now()
                self.metrics["time_to_first_word_s"] = round(self.first_word_at - (self.session_started_at or 0), 1)
            res = await self.speak(heard, seg.duration_s)
            self.metrics["child_talk_s"] += seg.duration_s
            rec = {"t": self.now(), "said": seg.text, "stt": heard, "stt_notes": notes, "words": seg.words,
                   "muted_words": res.get("muted_words", 0), "over_buddy": over_buddy}
            self.utterances.append(rec)
            for a in attempts:
                if a.idx in seg.words:
                    self.attempts.setdefault(a.idx, []).append({"t": self.now(), "target": a.target, "said": a.said,
                                                                "correct": a.correct, "kind": a.kind, "stt": heard})
            if res.get("muted_words"):
                self.metrics["unheard_words"] += res["muted_words"]
                self.issue("SPEECH_IGNORED_WHILE_BUDDY_TALKS", f"{res['muted_words']} word(s) the child said were not heard "
                           "because Buddy was talking or the session was paused.",
                           {"said": seg.text, "heard": res.get("heard")})
                self.affect.add("unheard_speech", self.now())
            if any(a.correct for a in attempts if a.idx in seg.words):
                self.affect.add("progress", self.now())
            if seg.pause_after_s > 0:
                # thinking pause: does Buddy jump in before the child is ready to go on?
                # (only a real interruption if Buddy was quiet when the pause began)
                if over_buddy or (await self.state(page)).get("dock") == "talking":
                    return
                t_p = self.now()
                interrupted = False
                while self.now() - t_p < seg.pause_after_s:
                    await asyncio.sleep(0.15)
                    o2 = await self.observe(page)
                    if o2.get("dock") == "talking":
                        interrupted = True
                        break
                if interrupted:
                    paused_for = round(self.now() - t_p, 1)
                    self.metrics["interruptions"] += 1
                    said_kind = next((s["kind"] for s in reversed(self.buddy_said) if s["t"] >= t_p - 0.3), None)
                    self.issue("INTERRUPTED_WHILE_THINKING", f"Buddy started talking {paused_for} s into a planned "
                               f"{seg.pause_after_s} s thinking pause.",
                               {"paused_s": paused_for, "planned_s": seg.pause_after_s, "line": line, "buddy_kind": said_kind,
                                "next_words": " ".join(w for _, w in words[len(sum([s.words for s in segments[:k+1]], [])):][:3])})
                    self.affect.add("interrupted_pause", self.now(), paused_s=paused_for)
                    return
        await asyncio.sleep(0.8)
        self.check_corrections()

    async def drill_turn(self, page, o, lang):
        j = o["target"]
        self.drill_counts[j] = self.drill_counts.get(j, 0) + 1
        n = self.drill_counts[j]
        word = next((w["t"] for w in self.words if w["i"] == j), "")
        if n >= 3:
            if self.issue("SAME_WORD_ASKED_AGAIN_AND_AGAIN", f"Asked to say '{clean(word)}' {n} times.",
                          {"word": clean(word), "times": n}):
                pass
            self.affect.add("drill_repeat", self.now(), word=clean(word))
        recent = {w for w, t in self.heard_words.items() if self.now() - t < 25}
        attempts, segments, _ = read_attempt([(j, word)], lang, self.p, self.rng, recent, allow_hesitation=False)
        if not segments:
            await asyncio.sleep(1.0)
            return
        heard, notes = stt_channel(segments[0].text, lang, self.p, self.rng)
        res = await self.speak(heard, segments[0].duration_s)
        self.utterances.append({"t": self.now(), "said": segments[0].text, "stt": heard, "stt_notes": notes,
                                "words": [j], "drill": True, "muted_words": res.get("muted_words", 0)})
        for a in attempts:
            self.attempts.setdefault(j, []).append({"t": self.now(), "target": a.target, "said": a.said,
                                                    "correct": a.correct, "kind": a.kind, "stt": heard, "drill": True})
        await asyncio.sleep(0.6)
        self.check_corrections()

    def check_corrections(self):
        """Compare Buddy's corrections with what the child really said (ground truth)."""
        for c in self.corrections:
            if c.get("checked"):
                continue
            c["checked"] = True
            if c["kind"] != "fix_word":
                continue
            j = c["word"]
            tries = [a for a in self.attempts.get(j, []) if a["t"] <= c["t"] + 0.5 and not a.get("drill")]
            if not tries:
                self.issue("CORRECTED_A_WORD_NOT_YET_READ", "Buddy asked to practise a word the child had not said "
                           "(it was skipped, lost while muted, or not reached).",
                           {"word": self.word_text(j)}, level="inferred")
                continue
            last = tries[-1]
            if last["correct"]:
                misheard = clean(last["target"]).lower() not in (last["stt"] or "").lower()
                code = "FALSE_CORRECTION_STT" if misheard else "FALSE_CORRECTION"
                self.issue(code, f"Read '{last['target']}' correctly but Buddy asked to practise it"
                           + (" (the speech model wrote it differently)" if misheard else "") + ".",
                           {"word": last["target"], "child_said": last["said"], "speech_model_wrote": last["stt"]})
                self.affect.add("false_correction", self.now(), word=last["target"])

    def word_text(self, j):
        return next((clean(w["t"]) for w in self.words if w["i"] == j), str(j))

    async def handle_pause(self, page, o):
        """The session is paused. If the child did not ask for that, it is confusing."""
        t = self.now()
        recent_tap = any(e["kind"] == "tap_mic_to_talk" and t - e["t"] < 3 for e in self.trace)
        tired = self.metrics["tired_said"]
        if recent_tap:
            self.issue("MIC_TAP_PAUSED_SESSION", "Tapped the big microphone to talk; the session paused instead.",
                       {"bubble": o.get("bubbleText")})
            self.affect.add("unexpected_pause", t)
        waited = 0.0
        while True:
            await asyncio.sleep(0.5)
            waited += 0.5
            o2 = await self.observe(page)
            if o2.get("dock") != "paused":
                return
            # how fast a child figures out to tap again
            if self.rng.random() < 0.08 + 0.25 * self.p.technology_familiarity or (tired and waited > 6):
                mic = next((c for c in o2["clickables"] if c["id"] == "micBtn"), None)
                if mic:
                    await self.tap(page, mic, "trying to carry on")
                    self.log("resumed", after_s=waited)
                    if waited > 8 and not tired:
                        self.issue("HARD_TO_RESUME", f"Took {waited:.0f} s to work out how to carry on after a pause.",
                                   {"waited_s": waited})
                    return
            if waited > 20:
                self.affect.add("stuck", self.now(), what="paused")
                await self.abandon(page, o2, "stuck_paused")
                return

    async def look_for_replay(self, o):
        """The child wants to hear the line again. Is there a control for that during reading?"""
        want = re.compile(r"again|replay|repeat|hear|listen", re.I)
        hit = [c for c in o["clickables"] if want.search(c["text"] + " " + c["aria"]) and c["id"] != "micBtn"]
        self.log("looked_for_replay", found=[c["text"][:30] for c in hit])
        if not hit:
            self.issue("NO_REPLAY_CONTROL", "Wanted Buddy to read the line again, but there is no button for that "
                       "while reading ('Listen first' is switched off during a session).", {"visible": [c["text"][:20] for c in o["clickables"]][:8]})

    async def restart_from_summary(self, page):
        """Read the same text again from the summary screen."""
        o = await self.observe(page)
        again = next((c for c in o["clickables"] if c["id"] == "againBtn"), None)
        if not again:
            self.issue("RESTART_NOT_FOUND", "Wanted to read it again but found no way from the end screen.", {})
            return
        await self.tap(page, again, "wants to read it again")
        await asyncio.sleep(1.2)
        o = await self.observe(page)
        if o.get("view") != "view-reader":
            self.issue("RESTART_FAILED", f"'Read this again' led to {o.get('view')}.", {"view": o.get("view")})
            return
        mic = next((c for c in o["clickables"] if c["id"] == "micBtn"), None)
        if mic:
            await self.tap(page, mic, "starting again")
            t = self.now()
            while self.now() - t < 25:
                o = await self.observe(page)
                if o.get("dock") in ("listening", "hearing"):
                    self.log("restart_ok", after_s=round(self.now() - t, 1))
                    self.metrics["restart_ok"] = True
                    return
                await asyncio.sleep(0.4)
            self.issue("RESTART_FAILED", "After 'Read this again' the new session did not get to the child's turn in 25 s.",
                       {"dock": o.get("dock")})

    async def say_tired(self, page, lang):
        self.metrics["tired_said"] = True
        res = await self.speak(TIRED.get(lang, "I am tired"), 1.2)
        self.log("said_tired", heard=res.get("heard"))
        t = self.now()
        paused = False
        while self.now() - t < 6:
            await asyncio.sleep(0.3)
            o = await self.observe(page)
            if o.get("dock") == "paused":
                paused = True
                break
        self.metrics["break_honoured"] = paused
        if not paused:
            self.issue("BREAK_REQUEST_IGNORED", "Said they were tired; Buddy did not offer a break.",
                       {"said": TIRED.get(lang), "heard": res.get("heard")})

    async def off_task(self, page, o):
        c = self.choose([c for c in o["clickables"] if c["id"] != "micBtn"])
        if not c:
            return
        self.log("off_task_tap", target=c["text"][:40])
        after = await self.tap(page, c, "curious tap during reading")
        if after.get("view") != "view-reader":
            self.issue("LEFT_READING_BY_ACCIDENT", f"A curious tap on '{c['text'][:30]}' left the reading page.",
                       {"tapped": c["text"][:40], "view": after.get("view")})
            self.affect.add("wrong_screen", self.now())

    async def abandon(self, page, o, why):
        self.outcome = f"abandoned_{why}"
        self.log("abandon", why=why, frustration=round(self.affect.frustration, 2))
        await self.shot(page, "abandon")
        end = next((c for c in o["clickables"] if c["id"] == "endBtn"), None)
        if end and self.rng.random() < 0.5 + 0.5 * self.p.technology_familiarity:
            await self.tap(page, end, "stopping")
            await asyncio.sleep(1.5)

    async def fetch_server_record(self) -> dict | None:
        await asyncio.sleep(1.0)
        try:
            async with httpx.AsyncClient(base_url=self.base, timeout=10) as c:
                r = await c.get(f"/api/sim/record/{self.token}")
                return r.json() if r.status_code == 200 else None
        except Exception:
            return None

    # ----- report ---------------------------------------------------------------------------
    def build_report(self, record, error) -> dict:
        from .report import build
        return build(self, record, error)
