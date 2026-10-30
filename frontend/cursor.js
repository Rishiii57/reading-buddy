// Playful cursor: a smiling star pointer, a cartoon hand over buttons, a sparkle trail and
// click bursts. The overlay never takes pointer events. The native cursor is hidden only
// after this has initialised on a fine-pointer device, so the fallback is always the system
// cursor. Text fields and selectable text keep the normal I-beam. Touch gets tap ripples.
"use strict";

(() => {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const fine = window.matchMedia("(hover: hover) and (pointer: fine)");
  const COLORS = ["#FFC93C", "#FF7A59", "#FF6FA8", "#3CCB9A", "#7B5CFF", "#4FB8FF"];
  const TEXT_SEL = 'input, textarea, select, [contenteditable="true"], .selectable';
  const CARD_SEL = "[data-cursor='card']";
  const HAND_SEL = "button, a[href], [role='button'], [role='tab'], summary, label, [data-cursor='hand']";

  const starSVG = `<svg viewBox="0 0 40 40" width="36" height="36" aria-hidden="true">
      <path d="${Art.starPath(21, 21, 17, 0.52, -135)}" fill="#FFC93C" stroke="#2B2A5E" stroke-width="2.6" stroke-linejoin="round"/>
      <path d="M14 15 l3 -3" stroke="#fff" stroke-width="2.4" stroke-linecap="round" opacity=".9"/>
      <circle cx="18.5" cy="22" r="1.7" fill="#2B2A5E"/><circle cx="25" cy="22" r="1.7" fill="#2B2A5E"/>
      <path d="M19 26 q2.8 2.6 5.6 0" fill="none" stroke="#2B2A5E" stroke-width="1.7" stroke-linecap="round"/>
      <circle cx="16.5" cy="25" r="1.5" fill="#FF8FA3" opacity=".8"/><circle cx="27" cy="25" r="1.5" fill="#FF8FA3" opacity=".8"/></svg>`;
  const handSVG = `<svg viewBox="0 0 46 48" width="32" height="34" aria-hidden="true">
      <path d="M14 27 V6 a4 4 0 0 1 8 0 V20 a3.5 3.5 0 0 1 7 0 V22 a3.5 3.5 0 0 1 7 0 V25 a3.5 3.5 0 0 1 7 0 V34 c0 7 -5 12 -12 12 H25 c-6 0 -9 -3 -12 -7 L5 30 a3.6 3.6 0 0 1 5.5 -4.6 Z"
        fill="#FFF6DA" stroke="#2B2A5E" stroke-width="2.6" stroke-linejoin="round"/>
      <path d="M22 20 v6 M29 22 v5 M36 25 v4" stroke="#2B2A5E" stroke-width="2" stroke-linecap="round"/>
      <path d="M16 7 v6" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>`;
  // where the click lands, in CSS pixels from the top-left of each graphic
  const HOT = { star: [8.1, 8.1], hand: [12.5, 1.6] };

  // ---------- touch / pen: tap ripples (every device) ----------
  document.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "mouse" || reduce.matches) return;
    const r = document.createElement("span");
    r.className = "tap-ripple";
    r.style.left = `${e.clientX}px`;
    r.style.top = `${e.clientY}px`;
    r.style.setProperty("--c", COLORS[(Math.random() * COLORS.length) | 0]);
    document.body.appendChild(r);
    setTimeout(() => r.remove(), 650);
  }, { passive: true });

  function start() {

    const root = document.createElement("div");
    root.id = "fun-cursor";
    root.setAttribute("aria-hidden", "true");
    root.innerHTML = `<div class="fc-trail"></div><div class="fc-pointer is-hidden"><div class="fc-star">${starSVG}</div><div class="fc-hand">${handSVG}</div></div>`;
    document.body.appendChild(root);
    const pointer = root.querySelector(".fc-pointer");
    const trail = root.querySelector(".fc-trail");

    let x = -100, y = -100, tx = -100, ty = -100, lastSpark = 0, sparks = 0;
    let state = "default", down = null, visible = false, dirty = true;

    function setState(s) {
      if (s === state) return;
      state = s;
      pointer.dataset.state = s;
      document.documentElement.classList.toggle("fc-native-text", s === "text");
      dirty = true;
    }

    function stateFor(el) {
      if (!el || !el.closest) return "default";
      if (el.closest(TEXT_SEL)) return "text";
      const hand = el.closest(HAND_SEL);
      if (hand && (hand.disabled || hand.getAttribute("aria-disabled") === "true")) return "disabled";
      if (el.closest(CARD_SEL)) return "card";
      if (hand) return "hand";
      return "default";
    }

    function spark(px, py, burst) {
      if (reduce.matches || sparks > 26) return;
      const s = document.createElement("span");
      s.className = burst ? "fc-spark fc-burst" : "fc-spark";
      const ang = Math.random() * Math.PI * 2;
      const dist = burst ? 22 + Math.random() * 18 : 6 + Math.random() * 10;
      s.style.cssText = `left:${px}px;top:${py}px;--dx:${Math.cos(ang) * dist}px;--dy:${Math.sin(ang) * dist + (burst ? 0 : 12)}px;--c:${COLORS[(Math.random() * COLORS.length) | 0]};--s:${burst ? 1 : 0.6 + Math.random() * 0.5}`;
      root.appendChild(s);
      sparks++;
      setTimeout(() => { s.remove(); sparks--; }, burst ? 650 : 700);
    }

    document.addEventListener("pointermove", (e) => {
      if (e.pointerType !== "mouse") return;
      x = e.clientX;
      y = e.clientY;
      if (!visible) {
        visible = true;
        tx = x; ty = y;
        pointer.classList.remove("is-hidden");
        trail.classList.remove("is-hidden");
      }
      if (down && Math.hypot(x - down[0], y - down[1]) > 6) pointer.classList.add("is-dragging");
      const now = performance.now();
      if (state !== "text" && now - lastSpark > 55) {
        lastSpark = now;
        if (Math.abs(e.movementX) + Math.abs(e.movementY) > 6) spark(x, y, false);
      }
      dirty = true;
    }, { passive: true });

    document.addEventListener("pointerover", (e) => { if (e.pointerType === "mouse") setState(stateFor(e.target)); }, { passive: true });
    document.addEventListener("pointerdown", (e) => {
      if (e.pointerType !== "mouse") {
        // a touch on a hybrid device: hide the fake cursor until the mouse moves again
        visible = false;
        pointer.classList.add("is-hidden");
        trail.classList.add("is-hidden");
        return;
      }
      down = [e.clientX, e.clientY];
      pointer.classList.add("is-pressed");
      if (state !== "text") for (let i = 0; i < 8; i++) spark(e.clientX, e.clientY, true);
    });
    const release = () => { down = null; pointer.classList.remove("is-pressed", "is-dragging"); };
    document.addEventListener("pointerup", release);
    document.addEventListener("pointercancel", release);
    document.addEventListener("dragend", release);
    document.documentElement.addEventListener("mouseleave", () => {
      visible = false;
      pointer.classList.add("is-hidden");
      trail.classList.add("is-hidden");
    });
    // focus moving by keyboard can put a new element under a still mouse
    document.addEventListener("focusin", () => setState(stateFor(document.elementFromPoint(x, y))));

    function frame() {
      const ease = reduce.matches ? 1 : 0.2;
      tx += (x - tx) * ease;
      ty += (y - ty) * ease;
      if (dirty || Math.abs(x - tx) > 0.3 || Math.abs(y - ty) > 0.3) {
        const [hx, hy] = state === "hand" || state === "card" ? HOT.hand : HOT.star;
        pointer.style.transform = `translate3d(${x - hx}px, ${y - hy}px, 0)`;
        trail.style.transform = `translate3d(${tx + 10}px, ${ty + 14}px, 0)`;
        dirty = false;
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
    pointer.dataset.state = "default";
  }

  // the system cursor is hidden only once the overlay is running, and only for a fine pointer;
  // this follows the device if it changes (a tablet with a mouse plugged in, for example)
  let started = false;
  function syncPointerKind() {
    if (fine.matches && !started) {
      started = true;
      start();
    }
    document.documentElement.classList.toggle("fun-cursor", fine.matches && started);
    const r = document.getElementById("fun-cursor");
    if (r) r.hidden = !fine.matches;
  }
  fine.addEventListener("change", syncPointerKind);
  syncPointerKind();
})();
