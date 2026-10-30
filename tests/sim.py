"""Tiny simulated-clock driver for the tutor engine (used by tests and debugging)."""
from backend.tutor import TutorEngine


def simulate(text, script, until=40.0, tutor_audio_s=1.5, cfg=None):
    """script: list of (time, 'ss'|'tr'|'pause'|'resume', transcript). Returns (engine, actions)."""
    e = TutorEngine(text, cfg, now=0.0)
    e.state = "CHILD_READING"  # scripted readers start reading straight away (no greeting)
    out, events, ei, tt = [], sorted(script), 0, 0.0
    while tt < until:
        while ei < len(events) and events[ei][0] <= tt:
            _, kind, txt = events[ei]
            ei += 1
            if kind == "pause":
                e.pause(tt)
                acts = []
            elif kind == "resume":
                e.resume(tt)
                acts = []
            else:
                acts = e.on_speech_start(tt) if kind == "ss" else e.on_transcript(txt, tt, 150)
            out += [(tt, a) for a in acts]
        out += [(tt, a) for a in e.tick(tt)]
        if e.tutor_busy and tt - e.tutor_busy_since >= tutor_audio_s:
            e.on_tutor_audio_end(tt)
        tt = round(tt + 0.1, 2)
    return e, [(t, a) for t, a in out if a["type"] != "progress"]
