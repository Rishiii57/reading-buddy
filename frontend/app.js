// Reading Buddy - browser client.
// Captures the microphone, resamples to 16 kHz PCM16 in 1024-byte frames and streams it to the
// backend (which proxies to Gnani Prisma). Renders live highlighting, plays Buddy's Timbre clips
// (muting the mic meanwhile), and shows the parent summary from real session data.
"use strict";

const $ = (id) => document.getElementById(id);
const FRAME_SAMPLES = 512; // 1024 bytes of PCM16 at 16 kHz = 32 ms
const STORE = { lang: "rb.lang" };
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const LANGS = {
  "gu-IN": { name: "ગુજરાતી", en: "Gujarati", desc: "Lovely poems and stories in Gujarati", tag: "gu", html: "gu" },
  "en-IN": { name: "English", en: "English", desc: "Fun poems and passages in English", tag: "en", html: "en" },
  "hi-IN": { name: "हिन्दी", en: "Hindi", desc: "सुंदर कविताएँ और कहानियाँ हिंदी में", tag: "hi", html: "hi" },
};
// which illustration goes with which text (presentation only; unknown texts get a book)
const ART_FOR = {
  "en-kite": "kite", "gu-patang": "kite", "en-rain": "rain", "hi-baarish": "rain", "gu-varsad": "rain",
  "en-mango": "mango", "en-ant": "ant", "hi-gudiya": "doll", "hi-chidiya": "nest", "gu-chakli": "nest",
  "hi-bagicha": "garden", "gu-shala": "school",
};
// what Buddy shows on the reading page, in the language of the text (REQ-SPOKEN-ONBOARDING)
const UI = {
  "en-IN": { hi: "Hi! I'm Buddy.", start: "Press the big microphone and read the first line out loud.",
    listening: "I'm listening…", readWord: "Read the highlighted word out loud. Take your time!",
    turn: "Your turn!", wholeLine: "Read the whole line out loud.", sayWord: "Your turn! Say this word:" },
  "hi-IN": { hi: "नमस्ते! मैं बडी हूँ।", start: "बड़ा माइक दबाओ और पहली पंक्ति ज़ोर से पढ़ो।",
    listening: "मैं सुन रहा हूँ…", readWord: "चमकता शब्द ज़ोर से पढ़ो। आराम से!",
    turn: "अब तुम्हारी बारी!", wholeLine: "पूरी पंक्ति ज़ोर से पढ़ो।", sayWord: "अब तुम्हारी बारी! यह शब्द बोलो:" },
  "gu-IN": { hi: "નમસ્તે! હું બડી છું.", start: "મોટું માઇક દબાવ અને પહેલી પંક્તિ મોટેથી વાંચ.",
    listening: "હું સાંભળું છું…", readWord: "ચમકતો શબ્દ મોટેથી વાંચ. આરામથી!",
    turn: "હવે તારો વારો!", wholeLine: "આખી પંક્તિ મોટેથી વાંચ.", sayWord: "હવે તારો વારો! આ શબ્દ બોલ:" },
};
function ui(key) { const L = (app.text && UI[app.text.language]) || UI["en-IN"]; return L[key]; }
function uiLang() { return app.text ? LANGS[app.text.language].html : null; }
const COLORS = ["#FFC93C", "#FF7A59", "#FF6FA8", "#2FC48F", "#7B5CFF", "#4FB8FF"];

const app = {
  library: null, libError: null, texts: new Map(),
  lang: storeGet(STORE.lang) || "gu-IN", grade: "all", // grade filter is per visit, so nobody lands on an empty shelf
  text: null, ws: null, ctx: null, analyser: null,
  running: false, ready: false, paused: false, mode: null,
  tutorSpeaking: false, sayQueue: [], buffers: new Map(),
  mic: null, demo: null, listening: false,
  last: null, summary: null, leaving: false,
  level: 0, levelSmooth: 0, bubbleTimer: null,
};

function storeGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function storeSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage blocked */ } }
function esc(s) { return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
function gradeRange(g) { const [a, b] = String(g).split("-").map(Number); return [a, b || a]; }
function minutes(words) { return Math.max(1, Math.round(words / 40)); }
function artFor(id) { return (Art.scenes[ART_FOR[id]] || Art.scenes.book)(); }
function toast(msg) {
  const t = $("toast");
  t.textContent = msg;
  t.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { t.hidden = true; }, 3800);
}

// =====================================================================================
// Scene + static art
// =====================================================================================
function buildScene() {
  const tree = (c1, c2) => `<svg class="tree" viewBox="0 0 150 200" aria-hidden="true"><rect x="66" y="110" width="18" height="90" rx="6" fill="#B07A4F"/>
    <circle cx="75" cy="78" r="56" fill="${c1}"/><circle cx="40" cy="104" r="34" fill="${c2}"/><circle cx="112" cy="100" r="36" fill="${c2}"/><circle cx="76" cy="40" r="34" fill="${c2}" opacity=".6"/></svg>`;
  const clouds = [[6, 0, 1.1], [18, -25, 0.8], [11, -48, 1.3], [26, -12, 0.7]]
    .map(([top, delay, s]) => `<svg class="cloud" viewBox="0 0 80 40" style="top:${top}vh;animation-delay:${delay}s;width:${180 * s}px"><path fill="#fff" d="M12 34 C0 34 0 16 14 16 C16 4 34 0 40 12 C46 2 66 6 64 22 C76 22 76 34 66 34 Z"/></svg>`).join("");
  const twinkles = [[12, 30], [84, 22], [70, 48], [6, 60], [92, 64]]
    .map(([l, t], i) => `<svg class="twinkle" viewBox="0 0 24 24" style="left:${l}vw;top:${t}vh;animation-delay:${i * 0.6}s"><path d="${Art.starPath(12, 12, 10, 0.45)}" fill="${COLORS[i]}" opacity=".8"/></svg>`).join("");
  $("scene").innerHTML = `${clouds}${twinkles}
    <div style="position:absolute;left:-40px;bottom:0">${tree("#5BC46F", "#4AB35F")}</div>
    <div style="position:absolute;right:-30px;bottom:0;transform:scaleX(-1)">${tree("#6FD07F", "#55BF68")}</div>
    <svg class="hills" viewBox="0 0 1440 260" preserveAspectRatio="none" aria-hidden="true">
      <path d="M0 120 C240 40 480 150 760 90 C1040 30 1240 120 1440 70 L1440 260 L0 260 Z" fill="#A6E38B"/>
      <path d="M0 180 C300 120 620 210 940 150 C1180 110 1320 170 1440 150 L1440 260 L0 260 Z" fill="#7FD06A"/></svg>`;
  $("heroArt").innerHTML = Art.hero();
  $("buddy").innerHTML = Art.owl();
  $("sumOwl").innerHTML = `<div data-state="happy">${Art.owl()}</div>`;
  $("sumKid").innerHTML = Art.kid({ hair: "boy", shirt: "#3D8BFF", pose: "cheer" });
  const bars = (n) => Array.from({ length: n }, () => "<i></i>").join("");
  document.querySelectorAll(".wave").forEach((w) => { w.innerHTML = bars(7); });
}

// =====================================================================================
// Library data
// =====================================================================================
async function loadLibrary() {
  if (app.library) return app.library;
  try {
    const res = await fetch("/api/library");
    if (!res.ok) throw new Error(res.statusText);
    app.library = await res.json();
    app.libError = null;
    if (!app.library.texts[app.lang]) app.lang = "gu-IN";
  } catch (e) {
    app.libError = e;
  }
  return app.library;
}

function langCard(code) {
  const L = LANGS[code];
  const n = app.library ? app.library.texts[code].length : 0;
  return `<a class="lang-card${code === app.lang ? " is-selected" : ""}" data-lang="${code}" href="#/library/${code}" data-cursor="card" aria-label="${L.en}: ${n} poems and stories">
    <span class="sel-badge"><svg class="icon"><use href="#i-check"/></svg> Picked</span>
    <span class="lang-art">${Art.langArt[code]()}</span>
    <span class="lang-text"><span class="lang-name" lang="${L.html}">${L.name}</span>
    <span class="lang-desc" ${code === "hi-IN" ? 'lang="hi"' : ""}>${L.desc}</span>
    <span class="lang-meta">${n ? `${n} poems & stories` : "&nbsp;"}</span></span>
    <span class="lang-go"><svg class="icon"><use href="#i-next"/></svg></span></a>`;
}

function renderLangGrid(id) {
  $(id).innerHTML = Object.keys(LANGS).map(langCard).join("");
}

function errorBlock(retry) {
  return `<div class="empty">${Art.owl()}<h2>Oh no, I can't find the books!</h2>
    <p>The reading server didn't answer. Check the connection and try again.</p>
    <button class="btn btn--sun" id="${retry}"><svg class="icon"><use href="#i-refresh"/></svg> Try again</button></div>`;
}

function renderLibrary() {
  const grid = $("storyGrid");
  $("libLangs").innerHTML = Object.entries(LANGS).map(([code, L]) =>
    `<button role="tab" data-lang="${code}" aria-selected="${code === app.lang}" lang="${L.html}">${L.name}</button>`).join("");
  if (!app.library) {
    $("gradeChips").innerHTML = "";
    grid.innerHTML = app.libError ? errorBlock("libRetry") : Array.from({ length: 4 }, () => `<div class="skeleton"><i></i><i></i><i></i></div>`).join("");
    const r = $("libRetry");
    if (r) r.onclick = async () => { app.libError = null; renderLibrary(); await loadLibrary(); renderLibrary(); };
    return;
  }
  const texts = app.library.texts[app.lang];
  const count = (g) => texts.filter((t) => { const [a, b] = gradeRange(t.grade); return a <= g && g <= b; }).length;
  $("gradeChips").innerHTML = [["all", "All", texts.length], ...[1, 2, 3, 4, 5].map((g) => [String(g), `Grade ${g}`, count(g)])]
    .map(([v, label, n]) => `<button class="chip" data-grade="${v}" aria-pressed="${app.grade === v}">${label}<small>${n}</small></button>`).join("");
  const sel = $("gradeChips").querySelector('[aria-pressed="true"]');
  if (sel) $("gradeChips").scrollLeft = sel.offsetLeft - $("gradeChips").clientWidth / 2 + sel.offsetWidth / 2;
  const shown = app.grade === "all" ? texts : texts.filter((t) => { const [a, b] = gradeRange(t.grade); return a <= +app.grade && +app.grade <= b; });
  const L = LANGS[app.lang];
  grid.innerHTML = shown.length ? shown.map((t, i) => `
    <button class="story" data-id="${t.id}" data-cursor="card" style="animation-delay:${i * 0.06}s" aria-label="${esc(t.title_en)}, ${t.type === "poem" ? "poem" : "story"}, grade ${t.grade}">
      <span class="story-art">${artFor(t.id)}</span>
      <span class="story-title" lang="${L.html}">${esc(t.title)}</span>
      ${t.title_en !== t.title ? `<span class="story-sub">${esc(t.title_en)}</span>` : ""}
      <span class="tags"><span class="tag tag--${L.tag}">${L.en}</span><span class="tag tag--grade">Grade ${t.grade}</span><span class="tag tag--type">${t.type === "poem" ? "Poem" : "Story"}</span></span>
      <span class="story-foot"><svg class="icon"><use href="#i-clock"/></svg> ${minutes(t.words)} min read · ${t.words} words</span>
      <span class="story-go" aria-hidden="true"><svg class="icon"><use href="#i-next"/></svg></span>
    </button>`).join("")
    : `<div class="empty">${Art.owl()}<h2>No stories for Grade ${app.grade} yet</h2><p>Try another grade, or pick “All”.</p>
       <button class="btn btn--sun" data-grade="all">Show all</button></div>`;
}

$("libLangs").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-lang]");
  if (b) location.hash = `#/library/${b.dataset.lang}`;
});
$("libLangs").addEventListener("keydown", (e) => {
  if (!["ArrowLeft", "ArrowRight"].includes(e.key)) return;
  const codes = Object.keys(LANGS);
  const i = (codes.indexOf(app.lang) + (e.key === "ArrowRight" ? 1 : codes.length - 1)) % codes.length;
  location.hash = `#/library/${codes[i]}`;
  requestAnimationFrame(() => document.querySelector(`#libLangs [data-lang="${codes[i]}"]`)?.focus());
});
$("view-library").addEventListener("click", (e) => {
  const g = e.target.closest("[data-grade]");
  if (g) {
    app.grade = g.dataset.grade;
    renderLibrary();
    return;
  }
  const s = e.target.closest(".story");
  if (s) location.hash = `#/read/${s.dataset.id}`;
});
document.addEventListener("click", (e) => {
  const c = e.target.closest(".lang-card");
  if (c) { app.lang = c.dataset.lang; storeSet(STORE.lang, app.lang); }
});

// =====================================================================================
// Router
// =====================================================================================
const VIEWS = ["home", "languages", "library", "reader", "summary", "about"];

function showView(name) {
  VIEWS.forEach((v) => $(`view-${v}`).classList.toggle("is-active", v === name));
  const nav = name === "languages" || name === "reader" || name === "summary" ? "library" : name;
  document.querySelectorAll("[data-nav]").forEach((a) => a.classList.toggle("is-active", a.dataset.nav === nav && a.closest(".navpill")));
  window.scrollTo({ top: 0, behavior: "instant" });
  $("main").focus({ preventScroll: true });
}

async function route() {
  const parts = location.hash.replace(/^#\/?/, "").split("/");
  const [page, arg] = parts;
  if (page !== "read" && app.running) { app.leaving = true; stopSession(); }
  if (page !== "read") { stopListen(); stopHint(); }
  switch (page) {
    case "languages":
      showView("languages");
      await withLibrary(() => renderLangGrid("pageLangs"));
      break;
    case "library":
      if (arg && LANGS[arg]) { app.lang = arg; storeSet(STORE.lang, arg); }
      showView("library");
      await withLibrary(renderLibrary);
      break;
    case "read":
      showView("reader");
      await openText(arg);
      break;
    case "done":
      if (!app.summary) { location.replace("#/library"); return; }
      showView("summary");
      renderSummary();
      break;
    case "about":
      showView("about");
      break;
    default:
      showView("home");
      await withLibrary(() => renderLangGrid("homeLangs"));
  }
}

// render once if the library is loaded; otherwise render a loading state, load, render again
async function withLibrary(render) {
  if (!app.library) {
    render();
    await loadLibrary();
  }
  render();
}
window.addEventListener("hashchange", route);

// =====================================================================================
// Reader
// =====================================================================================
async function openText(id) {
  app.leaving = false;
  resetReaderUI();
  $("textTitle").textContent = "…";
  $("passageInner").querySelectorAll(".line, .gap, .empty").forEach((n) => n.remove());
  try {
    if (!app.texts.has(id)) {
      const res = await fetch(`/api/text/${encodeURIComponent(id)}`);
      if (!res.ok) throw new Error("not found");
      app.texts.set(id, await res.json());
    }
  } catch (e) {
    app.text = null;
    $("textTitle").textContent = "Story not found";
    $("passageInner").insertAdjacentHTML("beforeend", `<div class="empty">${Art.owl()}<h2>I can't find that story.</h2><p>Let's pick another one.</p>
      <a class="btn btn--sun" href="#/library">Go to the library</a></div>`);
    $("micBtn").disabled = true;
    return;
  }
  app.text = app.texts.get(id);
  app.lang = app.text.language;
  storeSet(STORE.lang, app.lang);
  await loadLibrary();
  const meta = app.library?.texts[app.lang]?.find((t) => t.id === id);
  const L = LANGS[app.lang];
  $("textTitle").textContent = app.text.title;
  $("textTitle").lang = L.html;
  $("rbThumb").innerHTML = artFor(id);
  $("bookArt").innerHTML = artFor(id);
  $("rbTags").innerHTML = `<span class="tag tag--${L.tag}">${L.en}</span><span class="tag tag--grade">Grade ${app.text.grade}</span>`;
  $("readerBack").href = `#/library/${app.lang}`;
  $("demoBtn").hidden = !meta?.demo;
  $("micBtn").disabled = false;
  renderPassage();
  resetReaderUI();
  speakHint(id);
}

// Buddy says out loud what to do, once per opened text, for children who can't read the screen yet
async function speakHint(id) {
  stopHint();
  const token = (app.hintToken = {});
  try {
    const res = await fetch(`/api/phrase/${app.text.language}/reader_hint`);
    if (!res.ok) return;
    const { url, text } = await res.json();
    await ensureAudio();
    const buf = await getBuffer(url);
    if (app.hintToken !== token || app.running || app.listening || app.text?.id !== id) return;
    setBuddy("talking");
    bubble(ui("hi"), text, "help", uiLang());
    const s = app.ctx.createBufferSource();
    s.buffer = buf;
    s.connect(app.analyser);
    app.hintSource = s;
    s.onended = () => { if (app.hintSource === s) { app.hintSource = null; if (!app.running && !app.listening) setBuddy("idle"); } };
    s.start();
  } catch (e) { /* audio blocked or unavailable: the written hint stays */ }
}
function stopHint() {
  app.hintToken = null;
  if (app.hintSource) { try { app.hintSource.stop(); } catch (e) { /* already stopped */ } app.hintSource = null; }
}

function renderPassage() {
  const inner = $("passageInner");
  inner.querySelectorAll(".line, .gap").forEach((n) => n.remove());
  const L = LANGS[app.text.language];
  let lineEl = null, lastLine = -1, lastStanza = 0;
  const frag = document.createDocumentFragment();
  for (const w of app.text.words) {
    if (w.line !== lastLine) {
      if (w.stanza !== lastStanza) {
        const gap = document.createElement("span");
        gap.className = "gap";
        frag.appendChild(gap);
        lastStanza = w.stanza;
      }
      lineEl = document.createElement("span");
      lineEl.className = "line";
      lineEl.dataset.line = w.line;
      lineEl.lang = L.html;
      frag.appendChild(lineEl);
      lastLine = w.line;
    }
    const s = document.createElement("span");
    s.className = "w";
    s.id = `w${w.i}`;
    s.textContent = w.t;
    lineEl.appendChild(s);
    lineEl.appendChild(document.createTextNode(" "));
  }
  inner.appendChild(frag);
  app.last = { pointer: 0, status: app.text.words.map(() => "todo"), done: false };
  paintState(app.last, true);
}

function paintState(st, initial) {
  const prev = app.last && !initial ? app.last.status : null;
  app.last = st;
  const step = $("stepTag");
  step.hidden = !(app.running && st.state);
  if (st.state) step.textContent = STEP_NAMES[st.state] || st.state;
  st.status.forEach((s, i) => {
    const el = $(`w${i}`);
    if (!el) return;
    el.classList.toggle("is-read", s === "read");
    el.classList.toggle("is-helped", s === "helped");
    el.classList.toggle("is-practise", s === "practise");
    el.classList.toggle("is-skipped", s === "skipped");
    el.classList.toggle("is-current", i === st.pointer && !st.done);
    el.classList.toggle("is-target", st.mode === "drill" && i === st.target);
    if (prev && prev[i] === "todo" && s !== "todo" && !reduceMotion.matches) {
      el.animate([{ transform: "none" }, { transform: "translateY(-7px) scale(1.12)" }, { transform: "none" }],
        { duration: 450, delay: (i % 8) * 35, easing: "cubic-bezier(.34,1.56,.64,1)" });
    }
  });
  positionMarker();
  // progress
  const n = st.status.length;
  const done = st.status.filter((s) => s !== "todo").length; // includes lines left for next time
  const pct = n ? Math.round((100 * done) / n) : 0;
  $("progFill").style.width = `${pct}%`;
  $("progStar").style.left = `${pct}%`;
  $("progBar").setAttribute("aria-valuenow", pct);
  const lines = app.text.words.length ? app.text.words[app.text.words.length - 1].line + 1 : 1;
  const cur = app.text.words[Math.min(st.pointer, n - 1)];
  $("progLine").textContent = st.done ? `All ${lines} lines read` : `Line ${cur ? cur.line + 1 : 1} of ${lines}`;
  $("progWords").textContent = `${done} / ${n} words`;
  const el = $(`w${st.pointer}`);
  if (el && app.running) {
    const r = el.getBoundingClientRect();
    if (r.top < 90 || r.bottom > innerHeight - 170) el.scrollIntoView({ block: "center", behavior: reduceMotion.matches ? "auto" : "smooth" });
  }
}

function positionMarker() {
  const m = $("marker");
  const st = app.last;
  const el = st && !st.done ? $(`w${st.pointer}`) : null;
  if (!el) { m.classList.remove("is-on"); return; }
  const p = $("passageInner").getBoundingClientRect();
  const r = el.getBoundingClientRect();
  const fs = parseFloat(getComputedStyle($("passage")).fontSize);
  const h = fs * 1.32;
  m.style.width = `${r.width + 8}px`;
  m.style.height = `${h}px`;
  m.style.transform = `translate(${r.left - p.left - 4}px, ${r.top - p.top + (r.height - h) / 2}px)`;
  m.classList.add("is-on");
  m.classList.toggle("is-waiting", !app.running);
  m.classList.toggle("is-drill", st.mode === "drill");
  // the line the child is reading (or practising) gets a soft band
  document.querySelectorAll(".line.is-active").forEach((l) => l.classList.remove("is-active"));
  if (app.running && st.line != null) document.querySelector(`.line[data-line="${st.line}"]`)?.classList.add("is-active");
}
new ResizeObserver(() => positionMarker()).observe($("passageInner"));

function setBuddy(state) {
  $("buddy").dataset.state = state;
}
function setDock(state, label) {
  $("micDock").dataset.state = state;
  if (label) $("micLabel").textContent = label;
  const sr = { idle: "Start reading", connecting: "Connecting", listening: "Pause", hearing: "Pause", talking: "Buddy is talking", paused: "Resume", error: "Try again" }[state];
  $("micSr").textContent = sr || "";
}
function bubble(label, text, tone = "", lang = null, hold = 0) {
  const b = $("bubble");
  $("bubbleLabel").textContent = label;
  const t = $("bubbleText");
  t.textContent = text;
  if (lang) t.lang = lang; else t.removeAttribute("lang");
  b.dataset.tone = tone;
  b.classList.remove("is-pop");
  void b.offsetWidth;
  b.classList.add("is-pop");
  clearTimeout(app.bubbleTimer);
  if (hold) app.bubbleTimer = setTimeout(() => { if (app.running && !app.tutorSpeaking && !app.paused) listeningBubble(); }, hold);
}
function listeningBubble() {
  bubble(ui("listening"), ui("readWord"), "", uiLang());
}

function resetReaderUI() {
  setDock("idle", "Tap to start reading");
  setBuddy("idle");
  bubble(ui("hi"), ui("start"), "", uiLang());
  $("helpChip").hidden = true;
  $("heardList").innerHTML = "";
  $("heardEmpty").hidden = false;
  $("pauseBtn").disabled = true;
  $("endBtn").disabled = true;
  setPauseButton(false);
  $("listenBtn").disabled = false;
  $("demoBtn").disabled = false;
}

// =====================================================================================
// Audio
// =====================================================================================
const WORKLET = `
class Capture extends AudioWorkletProcessor {
  process(inputs) {
    const ch = inputs[0] && inputs[0][0];
    if (ch) this.port.postMessage(ch.slice(0));
    return true;
  }
}
registerProcessor("capture", Capture);`;

async function ensureAudio() {
  if (!app.ctx) {
    app.ctx = new (window.AudioContext || window.webkitAudioContext)();
    const url = URL.createObjectURL(new Blob([WORKLET], { type: "application/javascript" }));
    await app.ctx.audioWorklet.addModule(url);
    app.analyser = app.ctx.createAnalyser();
    app.analyser.fftSize = 512;
    app.analyser.connect(app.ctx.destination);
  }
  if (app.ctx.state === "suspended") await app.ctx.resume();
  return app.ctx;
}

// Streaming linear resampler: any input rate -> 16 kHz Int16 frames of 512 samples.
class Resampler {
  constructor(inRate, onFrame) {
    this.step = inRate / 16000;
    this.pos = 0;
    this.prev = 0;
    this.frame = new Int16Array(FRAME_SAMPLES);
    this.n = 0;
    this.onFrame = onFrame;
  }
  push(input, mute) {
    // pos indexes the virtual stream [prev, ...input]
    while (this.pos < input.length) {
      const i = Math.floor(this.pos);
      const f = this.pos - i;
      const a = i === 0 ? this.prev : input[i - 1];
      const b = input[i];
      let v = mute ? 0 : a + (b - a) * f;
      v = Math.max(-1, Math.min(1, v));
      this.frame[this.n++] = v < 0 ? v * 0x8000 : v * 0x7fff;
      if (this.n === FRAME_SAMPLES) {
        this.onFrame(this.frame.buffer.slice(0));
        this.n = 0;
      }
      this.pos += this.step;
    }
    this.pos -= input.length;
    this.prev = input[input.length - 1];
  }
}

function sendFrame(buf) {
  if (app.ws && app.ws.readyState === 1) app.ws.send(buf);
}

async function startMic() {
  const ctx = await ensureAudio();
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, channelCount: 1 },
  });
  const src = ctx.createMediaStreamSource(stream);
  const node = new AudioWorkletNode(ctx, "capture");
  const sink = ctx.createGain();
  sink.gain.value = 0;
  src.connect(node).connect(sink).connect(ctx.destination);
  const rs = new Resampler(ctx.sampleRate, sendFrame);
  node.port.onmessage = (e) => {
    const x = e.data;
    let sum = 0;
    for (let i = 0; i < x.length; i += 4) sum += x[i] * x[i];
    const muted = app.tutorSpeaking || app.paused;
    app.level = muted ? 0 : Math.sqrt(sum / (x.length / 4));
    rs.push(x, muted); // never let Buddy's own voice reach the speech model
  };
  app.mic = { stream, src, node, sink };
}

function stopMic() {
  if (!app.mic) return;
  app.mic.stream.getTracks().forEach((t) => t.stop());
  app.mic.node.port.onmessage = null;
  app.mic.src.disconnect();
  app.mic.node.disconnect();
  app.mic = null;
  app.level = 0;
}

// Interactive demo child: a synthetic Timbre voice ("Riyaa", never a real child) that answers
// Buddy like a child would. It reads each line (with one scripted wrong word and one scripted
// mid-line stop), says a practice word when asked, re-reads the line, and falls silent whenever
// Buddy talks. Its audio streams through the same Prisma -> tutor -> Timbre pipeline as a mic.
async function fetchPcm(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("demo clip unavailable");
  const bytes = new DataView(await res.arrayBuffer());
  let off = 12;
  while (off < bytes.byteLength - 8) {
    const id = String.fromCharCode(bytes.getUint8(off), bytes.getUint8(off + 1), bytes.getUint8(off + 2), bytes.getUint8(off + 3));
    const size = bytes.getUint32(off + 4, true);
    if (id === "data") { off += 8; break; }
    off += 8 + size;
  }
  const n = Math.floor((bytes.byteLength - off) / 2);
  const pcm = new Float32Array(n);
  for (let i = 0; i < n; i++) pcm[i] = bytes.getInt16(off + i * 2, true) / 0x8000;
  return pcm;
}

function lineRange(L) {
  const ws = app.text.words.filter((w) => w.line === L);
  return ws.length ? [ws[0].i, ws[ws.length - 1].i + 1] : [0, 0];
}

async function startDemo() {
  const ctx = await ensureAudio();
  const res = await fetch(`/api/demo/${app.text.id}/plan`);
  if (!res.ok) throw new Error("demo unavailable");
  const d = { plan: await res.json(), cur: null, pos: 0, source: null, sent: 0, t0: performance.now(),
    mistakeDone: false, stallDone: false, waitPrompt: false, lastEnd: 0, lastKey: "", same: 0, busy: false };
  const stopClip = () => {
    if (d.source) { try { d.source.stop(); } catch (e) { /* already stopped */ } d.source.disconnect(); d.source = null; }
  };
  d.timer = setInterval(() => {
    const due = Math.floor((performance.now() - d.t0) / 32);
    while (d.sent < due) {
      d.sent++;
      const frame = new Int16Array(FRAME_SAMPLES);
      if (d.cur && (app.tutorSpeaking || app.paused)) { // the child stops when the teacher talks
        stopClip();
        d.cur = null;
        d.lastEnd = performance.now();
      }
      if (d.cur) {
        let sum = 0;
        for (let i = 0; i < FRAME_SAMPLES && d.cur; i++) {
          const v = d.cur[d.pos++];
          frame[i] = v < 0 ? v * 0x8000 : v * 0x7fff;
          sum += v * v;
          if (d.pos >= d.cur.length) { d.cur = null; d.lastEnd = performance.now(); }
        }
        app.level = Math.sqrt(sum / FRAME_SAMPLES);
      } else {
        app.level = 0;
      }
      sendFrame(frame.buffer);
    }
  }, 20);
  d.decider = setInterval(() => demoTurn(d, ctx), 250);
  d.stopClip = stopClip;
  app.demo = d;
}

async function demoTurn(d, ctx) {
  if (d.busy || d.cur || !app.running || !app.ready || app.paused || app.tutorSpeaking || app.sayQueue.length) return;
  const st = app.last;
  if (!st || st.done || d.waitPrompt) return;
  const now = performance.now();
  if (now - Math.max(d.lastEnd, app.lastSayEnd || 0) < 1800) return; // let Buddy respond first
  // wait until the tutor has processed what the child just said (or give up waiting after 6 s)
  if (d.lastEnd && (app.lastStateAt || 0) < d.lastEnd + 200 && now - d.lastEnd < 6000) return;
  let a, b, swap = -1, said = "";
  if (st.mode === "drill" && st.target != null) {
    [a, b] = [st.target, st.target + 1]; // say the practice word
  } else {
    const [ls, le] = lineRange(st.line);
    [a, b] = [Math.max(st.pointer, ls), le];
    if (a >= b) return;
    const { mistake, stall } = d.plan;
    if (mistake && st.line === mistake.line && !d.mistakeDone) {
      [a, swap, said] = [ls, mistake.word, mistake.said]; // the scripted slip
      d.mistakeDone = true;
    } else if (stall && st.line === stall.line && !d.stallDone && a < stall.word) {
      b = stall.word; // the scripted stop: wait for Buddy's prompt
      d.stallDone = true;
      d.waitPrompt = true;
    }
  }
  const key = `${a}-${b}-${swap}`;
  d.same = key === d.lastKey ? d.same + 1 : 0;
  d.lastKey = key;
  if (d.same >= 3) return; // the same thing three times: stop rather than loop
  d.busy = true;
  try {
    const pcm = await fetchPcm(`/api/demo/${app.text.id}/say?a=${a}&b=${b}&swap=${swap}&said=${encodeURIComponent(said)}`);
    if (!app.running || app.tutorSpeaking) return;
    const buf = ctx.createBuffer(1, pcm.length, 16000);
    buf.copyToChannel(pcm, 0);
    d.source = ctx.createBufferSource();
    d.source.buffer = buf;
    d.source.connect(ctx.destination);
    d.source.start();
    d.pos = 0;
    d.cur = pcm;
  } catch (e) {
    console.warn("demo child", e);
  } finally {
    d.busy = false;
  }
}

function stopDemo() {
  if (!app.demo) return;
  clearInterval(app.demo.timer);
  clearInterval(app.demo.decider);
  app.demo.stopClip();
  app.demo = null;
  app.level = 0;
}

async function getBuffer(url) {
  if (!app.buffers.has(url)) {
    const res = await fetch(url);
    app.buffers.set(url, await app.ctx.decodeAudioData(await res.arrayBuffer()));
  }
  return app.buffers.get(url);
}

function playBuffer(buf) {
  return new Promise((resolve) => {
    const s = app.ctx.createBufferSource();
    s.buffer = buf;
    s.connect(app.analyser);
    s.onended = resolve;
    s.start();
    app.currentSource = s;
  });
}

// waveform bars follow the real microphone level, or Buddy's voice while Buddy talks
const BAR_MULT = [0.55, 0.9, 0.7, 1.15, 0.8, 1.0, 0.6];
const tdata = new Float32Array(512);
function animateWave() {
  let lvl = app.level;
  if ((app.tutorSpeaking || app.listening) && app.analyser) {
    app.analyser.getFloatTimeDomainData(tdata);
    let s = 0;
    for (let i = 0; i < tdata.length; i += 2) s += tdata[i] * tdata[i];
    lvl = Math.sqrt(s / (tdata.length / 2));
  }
  app.levelSmooth = Math.max(lvl, app.levelSmooth * 0.86);
  if ($("view-reader").classList.contains("is-active")) {
    const t = performance.now() / 1000;
    document.querySelectorAll(".wave").forEach((w, side) => {
      w.querySelectorAll("i").forEach((bar, i) => {
        const k = side === 0 ? BAR_MULT[6 - i] : BAR_MULT[i];
        const wobble = 0.85 + 0.15 * Math.sin(t * 9 + i * 1.7 + side);
        const h = Math.min(1, 0.12 + app.levelSmooth * 7 * k * wobble);
        bar.style.setProperty("--h", h.toFixed(3));
      });
    });
  }
  requestAnimationFrame(animateWave);
}

function glow(span, on, cls = "is-spoken") {
  if (!span) return;
  for (let i = span[0]; i < span[1]; i++) {
    const el = $(`w${i}`);
    if (el) el.classList.toggle(cls, on);
  }
}

const SAY_UI = {
  intro: { label: "Hello! Let's read together", tone: "help", buddy: "talking" },
  stall_phrase: { label: "Listen…", tone: "help", chip: "Buddy is helping", buddy: "talking" },
  stall_rest: { label: "Listen, then you try!", tone: "help", chip: "Buddy is helping", buddy: "talking" },
  take_time: { label: "Take your time", tone: "", buddy: "talking" },
  uncertain: { label: "Can you read it again?", tone: "", buddy: "talking" },
  uncertain_word: { label: "Can you say it again?", tone: "", chip: "Word practice", buddy: "talking" },
  fix_word: { label: "Let's practise this word together", tone: "rewind", chip: "Word practice", buddy: "talking" },
  fix_next: { label: "Yes! Very nice! Next word:", tone: "praise", chip: "Word practice", buddy: "talking" },
  fix_again: { label: "Listen again", tone: "rewind", chip: "Word practice", buddy: "talking" },
  repeat_line: { label: "Now the whole line", tone: "help", chip: "Read the whole line", buddy: "talking" },
  praise: { label: "Yay!", tone: "praise", buddy: "happy", party: "small" },
  skip_line: { label: "That's okay!", tone: "rewind", chip: "Moving on", buddy: "talking" },
  break: { label: "Let's take a little break", tone: "", buddy: "sleepy" },
  finish: { label: "You did it!", tone: "praise", buddy: "happy", party: "big" },
};
// the teaching steps, in words a parent understands
const STEP_NAMES = {
  SESSION_START: "Getting ready", TEACHER_DEMONSTRATION: "Buddy reads first", CHILD_READING: "Child reading",
  STALL_PROMPT: "Helping with the next words", UNCERTAIN_AUDIO: "Asking to hear it again",
  INDIVIDUAL_WORD_CORRECTION: "Word practice", COMPLETE_LINE_DEMONSTRATION: "Buddy reads the line",
  COMPLETE_LINE_REPETITION: "Child reads the line again", LINE_COMPLETED: "Line done", STANZA_COMPLETED: "Verse done",
  LINE_SKIPPED: "Leaving a line for later", SESSION_COMPLETED: "Finished",
};

async function playSay(msg) {
  app.sayQueue.push(msg);
  if (app.demo && msg.kind.startsWith("stall")) app.demo.waitPrompt = false; // Buddy helped: the demo child goes on
  if (app.tutorSpeaking) return;
  while (app.sayQueue.length) {
    const m = app.sayQueue.shift();
    const ui = SAY_UI[m.kind] || SAY_UI.prompt;
    app.tutorSpeaking = true;
    sendJSON({ type: "audio_start", id: m.id });
    setDock("talking", "Buddy is talking…");
    setBuddy(ui.buddy);
    bubble(ui.label, m.text, ui.tone, LANGS[app.text.language].html);
    if (ui.chip) showChip(ui.chip, ui.tone === "rewind");
    if (ui.party) celebrate($("celebrate"), ui.party === "big" ? 70 : 26, m.text);
    try {
      for (const clip of m.clips) {
        const buf = await getBuffer(clip.url);
        glow(clip.span, true);
        await playBuffer(buf);
        glow(clip.span, false);
      }
    } catch (e) {
      console.warn("tutor audio failed", e);
    }
    await new Promise((r) => setTimeout(r, 150)); // let the room go quiet
    app.tutorSpeaking = false;
    app.lastSayEnd = performance.now();
    sendJSON({ type: "audio_done", id: m.id });
    $("helpChip").hidden = true;
  }
  if (app.running && app.paused) {
    setBuddy("sleepy");
  } else if (app.running) {
    setDock("listening", "I'm listening…");
    setBuddy("listening");
    clearTimeout(app.bubbleTimer);
    yourTurnBubble();
  }
}

// after Buddy speaks, say plainly what the child should do now
function yourTurnBubble() {
  const st = app.last;
  const L = LANGS[app.text.language].html;
  if (st && st.mode === "drill" && st.target != null) {
    bubble(ui("sayWord"), app.text.words[st.target].t.replace(/[,.!?;:।]+$/, ""), "help", L);
    showChip("Word practice");
  } else if (st && st.repeat_line) {
    bubble(ui("turn"), ui("wholeLine"), "help", L);
  } else {
    app.bubbleTimer = setTimeout(() => { if (app.running && !app.tutorSpeaking && !app.paused) listeningBubble(); }, 2600);
  }
}

function showChip(text, rewind) {
  $("helpChipText").textContent = text;
  $("helpChip").classList.toggle("is-rewind", !!rewind);
  $("helpChip").hidden = false;
}

function celebrate(layer, count, text) {
  if (text) {
    const pop = document.createElement("div");
    pop.className = "praise-pop" + (reduceMotion.matches ? " static" : "");
    pop.textContent = text;
    pop.lang = LANGS[app.text?.language || "en-IN"].html;
    layer.appendChild(pop);
    setTimeout(() => pop.remove(), 1700);
  }
  if (reduceMotion.matches) return;
  const h = layer.clientHeight + 60;
  for (let i = 0; i < count; i++) {
    const c = document.createElement("span");
    const isStar = i % 4 === 0;
    c.className = "confetti" + (isStar ? " is-star" : "");
    const color = COLORS[i % COLORS.length];
    if (isStar) c.innerHTML = `<svg viewBox="0 0 24 24"><path d="${Art.starPath(12, 12, 10)}" fill="${color}" stroke="#2B2A5E" stroke-width="1.5" stroke-linejoin="round"/></svg>`;
    c.style.cssText = `--x:${Math.random() * 100}%;--dx:${(Math.random() - 0.5) * 160}px;--r:${(Math.random() - 0.5) * 900}deg;--d:${1.3 + Math.random()}s;--delay:${Math.random() * 0.35}s;--c:${color};--fall:${h}px`;
    layer.appendChild(c);
    setTimeout(() => c.remove(), 2800);
  }
}

// =====================================================================================
// Session
// =====================================================================================
function sendJSON(obj) {
  if (app.ws && app.ws.readyState === 1) app.ws.send(JSON.stringify(obj));
}

// Part K: a parent or guardian agrees before the microphone is ever used
function askConsent() {
  if (storeGet("rb.consent") === "1") return Promise.resolve(true);
  const dlg = $("consentDlg");
  $("consentBox").checked = false;
  $("consentYes").disabled = true;
  dlg.showModal();
  return new Promise((resolve) => {
    $("consentBox").onchange = () => { $("consentYes").disabled = !$("consentBox").checked; };
    $("consentYes").onclick = () => { storeSet("rb.consent", "1"); dlg.close(); resolve(true); };
    $("consentNo").onclick = () => { dlg.close(); resolve(false); };
    dlg.oncancel = () => resolve(false);
  });
}

async function startSession(mode) {
  if (app.running || !app.text) return;
  if (mode === "mic" && !(await askConsent())) {
    bubble("That's okay!", "A grown-up can allow the microphone any time. You can also watch the Demo reader.", "");
    return;
  }
  stopListen();
  stopHint();
  try {
    await ensureAudio();
  } catch (e) {
    bubble("Hmm…", "This browser can't play or record sound here. Please try Chrome, Edge or Safari.", "error");
    return;
  }
  if (mode === "mic" && !navigator.mediaDevices?.getUserMedia) {
    bubble("I can't use the microphone here", "The microphone only works on a secure (https) page. Try the Demo reader instead!", "error");
    setDock("error", "Microphone unavailable");
    return;
  }
  renderPassage();
  $("heardList").innerHTML = "";
  $("heardEmpty").hidden = false;
  app.mode = mode;
  app.running = true;
  app.ready = false;
  app.paused = false;
  app.leaving = false;
  app.summary = null;
  setPauseButton(false);
  setControls();
  setDock("connecting", "Getting ready…");
  setBuddy("idle");
  bubble("Getting ready…", "Buddy is putting on listening ears!");
  const proto = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${proto}://${location.host}/ws/session`);
  ws.binaryType = "arraybuffer";
  app.ws = ws;
  ws.onopen = () => ws.send(JSON.stringify({ type: "start", text_id: app.text.id, mode }));
  ws.onmessage = (ev) => onMessage(JSON.parse(ev.data), mode);
  ws.onerror = () => {
    if (!app.ready) {
      bubble("Oh no!", "I can't reach my listening ears right now. Check the internet and try again.", "error");
      setDock("error", "Couldn't connect");
    }
  };
  ws.onclose = () => { if (app.running) endSession(); };
}

async function onMessage(m, mode) {
  switch (m.type) {
    case "ready":
      try {
        if (mode === "mic") await startMic();
        else await startDemo();
      } catch (e) {
        const denied = e && (e.name === "NotAllowedError" || e.name === "SecurityError");
        bubble(denied ? "I need the microphone" : "Hmm…", denied
          ? "Please allow the microphone in the browser so I can hear you. Or try the Demo reader!"
          : "I couldn't start listening. Please try again.", "error");
        app.leaving = true;
        stopSession();
        setDock("error", denied ? "Microphone blocked" : "Couldn't start");
        return;
      }
      app.ready = true;
      sendJSON({ type: "live" });
      setDock("listening", mode === "mic" ? "I'm listening…" : "Demo reader is reading…");
      setBuddy("listening");
      bubble("I'm listening…", mode === "mic" ? "Start reading whenever you're ready!" : "Watch the demo reader. Buddy will help when it gets stuck.");
      break;
    case "state":
      app.lastStateAt = performance.now();
      paintState(m);
      break;
    case "speech":
      if (!app.tutorSpeaking && app.running && !app.paused) {
        setDock(m.speaking ? "hearing" : "listening", m.speaking ? "I can hear you!" : "I'm listening…");
        setBuddy(m.speaking ? "hearing" : "listening");
      }
      break;
    case "heard": {
      const li = document.createElement("li");
      li.textContent = m.text || "(silence)";
      li.lang = LANGS[app.text.language].html;
      $("heardList").appendChild(li);
      $("heardEmpty").hidden = true;
      break;
    }
    case "say":
      playSay(m);
      break;
    case "summary":
      onSummary(m.summary);
      break;
    case "auto_pause": // the child asked to stop: Buddy already said "we can take a little break"
      app.paused = true;
      setPauseButton(true);
      setDock("paused", "Taking a break. Tap to carry on");
      break;
    case "error":
      bubble("Oh no!", m.message, "error");
      break;
  }
}

function togglePause() {
  if (!app.running || !app.ready) return;
  app.paused = !app.paused;
  sendJSON({ type: app.paused ? "pause" : "resume" });
  setPauseButton(app.paused);
  if (app.paused) {
    setDock("paused", "Paused. Tap to carry on");
    setBuddy("sleepy");
    bubble("Taking a little break", "Press play when you're ready to keep reading.", "");
  } else {
    setDock("listening", "I'm listening…");
    setBuddy("listening");
    listeningBubble();
  }
}

function setPauseButton(paused) {
  $("pauseBtn").innerHTML = paused
    ? `<svg class="icon"><use href="#i-play"/></svg><span>Resume</span>`
    : `<svg class="icon"><use href="#i-pause"/></svg><span>Pause</span>`;
}

function stopSession() {
  if (!app.running) return;
  sendJSON({ type: "stop" });
  // the server replies with a summary and closes; fall back if it does not
  setTimeout(() => { if (app.running) endSession(); }, 1500);
  stopMic();
  stopDemo();
}

function endSession() {
  app.running = false;
  app.ready = false;
  app.paused = false;
  stopMic();
  stopDemo();
  if (app.ws) { try { app.ws.close(); } catch (e) { /* ignore */ } }
  app.ws = null;
  setControls();
  if (!app.summary && !app.leaving && $("micDock").dataset.state !== "error") {
    setDock("idle", "Tap to start reading");
    setBuddy("idle");
  }
  positionMarker();
}

function setControls() {
  $("pauseBtn").disabled = !app.running;
  $("endBtn").disabled = !app.running;
  $("listenBtn").disabled = app.running;
  $("demoBtn").disabled = app.running;
}

function onSummary(s) {
  if (app.leaving) return;
  const covered = s.words_read + s.words_helped;
  if (!covered) {
    // nothing read yet: no report card, just reset
    resetReaderUI();
    toast("No words yet. Try reading the first line out loud!");
    return;
  }
  app.summary = { s, status: app.last.status.slice(), text: app.text };
  const go = () => {
    if (app.tutorSpeaking || app.sayQueue.length) { setTimeout(go, 200); return; }
    setTimeout(() => {
      if (app.leaving) return;
      app.summary.status = app.last.status.slice(); // the final highlight state arrives just after the summary
      location.hash = "#/done";
    }, s.words_total && covered >= s.words_total ? 900 : 250);
  };
  go();
}

// =====================================================================================
// Listen first
// =====================================================================================
async function listenFirst() {
  if (app.listening) { stopListen(); return; }
  stopHint();
  await ensureAudio();
  app.listening = true;
  $("listenBtn").innerHTML = `<svg class="icon"><use href="#i-stop"/></svg> Stop listening`;
  $("micBtn").disabled = true;
  $("demoBtn").disabled = true;
  setDock("talking", "Listen carefully…");
  setBuddy("talking");
  bubble("Listen first!", "I'll read it to you. Then it's your turn.", "help");
  try {
    const res = await fetch(`/api/listen/${app.text.id}`);
    if (!res.ok) throw new Error("listen failed");
    const { clips } = await res.json();
    for (const c of clips) {
      if (!app.listening) break;
      const line = document.querySelector(`.line[data-line="${c.line}"]`);
      line?.classList.add("is-listening");
      await playBuffer(await getBuffer(c.url));
      line?.classList.remove("is-listening");
    }
    if (app.listening) bubble("Your turn!", "Press the microphone and read it out loud.", "praise");
  } catch (e) {
    bubble("Oops", "I couldn't read it out right now. You can still start reading!", "error");
  }
  stopListen(true);
}

function stopListen(finished) {
  if (!app.listening) return;
  app.listening = false;
  if (!finished && app.currentSource) { try { app.currentSource.stop(); } catch (e) { /* already stopped */ } }
  document.querySelectorAll(".line.is-listening").forEach((l) => l.classList.remove("is-listening"));
  $("listenBtn").innerHTML = `<svg class="icon"><use href="#i-volume"/></svg> Listen first`;
  $("micBtn").disabled = !app.text;
  $("demoBtn").disabled = false;
  setDock("idle", "Tap to start reading");
  setBuddy("idle");
}

// =====================================================================================
// Summary
// =====================================================================================
function renderSummary() {
  const { s, status, text } = app.summary;
  const covered = s.words_read + s.words_helped;
  const finished = s.finished ?? covered >= s.words_total;
  const L = LANGS[text.language];
  const skipped = s.lines_skipped || [];
  $("sumTitle").textContent = finished ? "Well Done!" : "Great effort!";
  $("sumSub").textContent = !finished ? `You read ${covered} of ${s.words_total} words.`
    : skipped.length ? `You reached the end! ${skipped.length === 1 ? "One line" : `${skipped.length} lines`} to practise another time.`
      : "You finished reading!";
  $("sumPoem").innerHTML = `<span lang="${L.html}">${esc(text.title)}</span>`;
  $("sumBubble").textContent = finished ? "Amazing! You did it!" : "Let's read more next time!";
  const ratio = s.words_total ? s.words_read / s.words_total : 0;
  // every reading earns at least one star: effort counts
  const stars = finished ? (ratio > 0.85 ? 3 : ratio > 0.5 ? 2 : 1) : (covered / s.words_total > 0.5 ? 2 : 1);
  $("sumStars").innerHTML = [0, 1, 2].map((i) => `<svg viewBox="0 0 40 40" class="${i < stars ? "" : "is-dim"}" style="animation-delay:${0.3 + i * 0.15}s"><path d="${Art.starPath(20, 20, 17, 0.5)}" fill="#FFC93C" stroke="#2B2A5E" stroke-width="2.5" stroke-linejoin="round"/></svg>`).join("");
  $("sRead").textContent = covered;
  $("sPractised").textContent = s.words_practised ?? 0;
  $("sLines").textContent = `${s.lines_completed ?? 0}/${s.lines_total ?? "?"}`;
  $("sLater").textContent = skipped.length;
  const pct = s.lines_total ? Math.round((100 * (s.lines_completed || 0)) / s.lines_total) : 0;
  $("sumProgText").textContent = `${pct}% of lines completed`;
  requestAnimationFrame(() => { $("sumFill").style.width = `${pct}%`; });

  // parent-facing: factual, about the reading, never about the child
  const mins = Math.floor(s.seconds / 60), secs = Math.round(s.seconds % 60);
  $("parentMeta").innerHTML = `<span lang="${L.html}">${esc(text.title)}</span> · ${L.en} · ${mins ? `${mins} min ` : ""}${secs} s`;
  const facts = [
    ["Words in the passage", s.words_total],
    ["Read correctly without help", s.words_read],
    ["Words that needed practice", s.words_to_practise.length],
    ["Word practice attempts", s.correction_attempts ?? 0],
    ["Times Buddy helped when stuck", s.prompts],
    ["Lines completed", `${s.lines_completed ?? 0} of ${s.lines_total ?? "?"}`],
    ["Lines left for another time", skipped.length],
  ];
  $("parentFacts").innerHTML = facts.map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join("");
  $("sPractise").innerHTML = (s.words_to_practise.length
    ? `<div class="chips-practise">${s.words_to_practise.map((w) => `<span class="p-chip" lang="${L.html}">${esc(w)}</span>`).join("")}</div>`
    : `<p class="selectable">No words needed practice. Lovely reading!</p>`)
    + (skipped.length ? `<h4 class="skipped-head">Lines left for another time</h4>` + skipped.map((l) =>
      `<div class="skip-card selectable"><b lang="${L.html}">Line ${l.line}: ${esc(l.text)}</b>
       <span>${l.words.length ? `Practice recommended: <span lang="${L.html}">${l.words.map(esc).join(", ")}</span>. ` : ""}${l.mistakes} tries, so Buddy moved on.</span></div>`).join("") : "");
  let html = "", line = -1;
  text.words.forEach((w, i) => {
    if (w.line !== line && line !== -1) html += "<br>";
    line = w.line;
    const st = status[i] || "todo";
    html += `<span class="mw ${st}" lang="${L.html}">${esc(w.t)}</span> `;
  });
  $("miniMap").innerHTML = html;
  if (finished) setTimeout(() => celebrate($("sumCelebrate"), 80), 250);
}

$("anotherBtn").onclick = () => { location.hash = `#/library/${app.summary?.text.language || app.lang}`; };
$("againBtn").onclick = () => { location.hash = `#/read/${app.summary?.text.id || ""}`; };

// =====================================================================================
// Wiring
// =====================================================================================
$("micBtn").onclick = () => {
  if (!app.running) startSession("mic");
  else if (app.ready && !app.tutorSpeaking) togglePause();
};
$("pauseBtn").onclick = togglePause;
$("endBtn").onclick = () => stopSession();
$("demoBtn").onclick = () => startSession("demo");
$("listenBtn").onclick = listenFirst;
document.addEventListener("keydown", (e) => {
  // Escape pauses a running session (and resumes it)
  if (e.key === "Escape" && app.running && app.ready) togglePause();
});

window.addEventListener("scroll", () => {
  document.querySelector(".topnav").classList.toggle("is-scrolled", scrollY > 12);
}, { passive: true });

buildScene();
requestAnimationFrame(animateWave);
route();
