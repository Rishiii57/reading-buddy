"""Measures computed from a run's agent reports. Shared by the PM (to state acceptance criteria)
and QA (to check them before and after a change). Each takes a list of report dicts and returns a
number; lower_is_better says which way is an improvement."""
import json
import statistics
from pathlib import Path


def load_reports(run_dir: Path) -> list[dict]:
    out = []
    for f in sorted(Path(run_dir).glob("*/report.json")):
        r = json.loads(f.read_text())
        r["_dir"] = str(f.parent)
        out.append(r)
    return out


def _started(r):
    return (r.get("metrics") or {}).get("intro_s") is not None or (r.get("metrics") or {}).get("session_s")


def _issue(r, code):
    for i in (r.get("experience") or {}).get("issues", []):
        if i["code"] == code:
            return i
    return None


def _count(r, code, pred=None):
    i = _issue(r, code)
    if not i:
        return 0
    if pred is None:
        return i["count"]
    return sum(1 for e in i.get("evidence", []) if pred(e))


def _rate(reports, f):
    return round(sum(f(r) for r in reports) / max(1, len(reports)), 3)


METRICS = {
    # name: (fn(reports) -> float, lower_is_better, description)
    "session_start_rate": (lambda rs: _rate(rs, lambda r: 1 if _started(r) else 0), False,
                           "share of agents who got a reading session going"),
    "completion_rate": (lambda rs: _rate(rs, lambda r: 1 if r.get("outcome") == "completed" else 0), False,
                        "share of agents who finished the text"),
    "abandon_rate": (lambda rs: _rate(rs, lambda r: 1 if str(r.get("outcome", "")).startswith(("abandoned", "could_not", "left")) else 0), True,
                     "share of agents who gave up, could not start, or left"),
    "coverage": (lambda rs: _rate(rs, lambda r: min(1.0, ((r.get("tutor_summary") or {}).get("words_read", 0) + (r.get("tutor_summary") or {}).get("words_helped", 0)) / max(1, (r.get("metrics") or {}).get("words_total") or 1))), False,
                 "average share of the text covered (read or helped)"),
    "stall_interruptions_per_agent": (lambda rs: _rate(rs, lambda r: _count(r, "INTERRUPTED_WHILE_THINKING", lambda e: str(e.get("buddy_kind", "")).startswith("stall"))), True,
                                      "stall prompts that cut into a child's thinking pause"),
    "correction_interruptions_per_agent": (lambda rs: _rate(rs, lambda r: _count(r, "INTERRUPTED_WHILE_THINKING", lambda e: str(e.get("buddy_kind", "")).startswith(("fix", "repeat")))), True,
                                           "mid-line corrections that cut into a child's thinking pause"),
    "interruptions_per_agent": (lambda rs: _rate(rs, lambda r: _count(r, "INTERRUPTED_WHILE_THINKING")), True,
                                "all interruptions of thinking pauses"),
    "mic_tap_pause_rate": (lambda rs: _rate(rs, lambda r: 1 if _issue(r, "MIC_TAP_PAUSED_SESSION") else 0), True,
                           "share of agents whose session paused when they tapped the mic to talk"),
    "unheard_words_per_agent": (lambda rs: _rate(rs, lambda r: (r.get("metrics") or {}).get("unheard_words", 0)), True,
                                "words the child said that were dropped because the mic was muted"),
    "drill_repeat_rate": (lambda rs: _rate(rs, lambda r: 1 if _issue(r, "SAME_WORD_ASKED_AGAIN_AND_AGAIN") else 0), True,
                          "share of agents asked to repeat the same word 3+ times"),
    "spoken_guidance_gap_rate": (lambda rs: _rate(rs, lambda r: 1 if _issue(r, "NO_SPOKEN_GUIDANCE_BEFORE_START") else 0), True,
                                 "share of agents who met written-only instructions they could not read"),
    "consent_blocked_rate": (lambda rs: _rate(rs, lambda r: 1 if _issue(r, "CONSENT_BLOCKS_CHILD") else 0), True,
                             "share of agents stopped by the grown-up consent box"),
    "consent_self_approved_rate": (lambda rs: _rate(rs, lambda r: 1 if _issue(r, "CONSENT_SELF_APPROVED") else 0), True,
                                   "share of agents (children) who ticked the parent box themselves"),
    "level_mismatch_rate": (lambda rs: _rate(rs, lambda r: 1 if _issue(r, "NO_TEXT_FOR_MY_LEVEL") else 0), True,
                            "share of agents with no text at their level"),
    "false_corrections_per_agent": (lambda rs: _rate(rs, lambda r: _count(r, "FALSE_CORRECTION") + _count(r, "FALSE_CORRECTION_STT")), True,
                                    "corrections of words the child read right"),
    "missed_errors_per_agent": (lambda rs: _rate(rs, lambda r: _count(r, "MISSED_ERROR")), True,
                                "child misreadings accepted as correct"),
    "long_talk_rate": (lambda rs: _rate(rs, lambda r: 1 if _issue(r, "LONG_TUTOR_TALK") else 0), True,
                       "share of agents who sat through 12 s+ of Buddy talking in one go"),
    "intro_s_median": (lambda rs: round(statistics.median([r["metrics"]["intro_s"] for r in rs if (r.get("metrics") or {}).get("intro_s")] or [0]), 1), True,
                       "median seconds from tapping the mic to the child's first turn"),
    "frustration_peak_mean": (lambda rs: _rate(rs, lambda r: (r.get("experience") or {}).get("frustration_peak", 0)), True,
                              "mean peak frustration"),
    "stuck_rate": (lambda rs: _rate(rs, lambda r: 1 if _issue(r, "STUCK_WITHOUT_HELP") else 0), True,
                   "share of agents stuck 10 s+ without help"),
    "break_ignored_rate": (lambda rs: _rate(rs, lambda r: 1 if _issue(r, "BREAK_REQUEST_IGNORED") else 0), True,
                           "share of agents whose 'I'm tired' was ignored"),
    "wrong_language_rate": (lambda rs: _rate(rs, lambda r: 1 if _issue(r, "WRONG_LANGUAGE_TEXT") else 0), True,
                            "share of agents who ended up in a language they did not choose"),
    "replay_missing_rate": (lambda rs: _rate(rs, lambda r: 1 if _issue(r, "NO_REPLAY_CONTROL") else 0), True,
                            "share of agents who wanted to hear a line again and found no way"),
    "restart_failed_rate": (lambda rs: _rate(rs, lambda r: 1 if (_issue(r, "RESTART_FAILED") or _issue(r, "RESTART_NOT_FOUND")) else 0), True,
                            "share of agents for whom 'read it again' failed"),
    "harness_error_rate": (lambda rs: _rate(rs, lambda r: 1 if r.get("outcome") == "harness_error" else 0), True,
                           "agent runs that crashed (not a product measure)"),
}


def compute(reports: list[dict], names: list[str] | None = None) -> dict:
    return {n: METRICS[n][0](reports) for n in (names or METRICS)}


def by_group(reports: list[dict], key) -> dict:
    groups: dict = {}
    for r in reports:
        groups.setdefault(key(r), []).append(r)
    return {k: {"n": len(v), **compute(v)} for k, v in sorted(groups.items())}
