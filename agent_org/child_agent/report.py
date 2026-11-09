"""Turn one child agent's session into its individual experience report.

Two layers, kept apart on purpose:
  * the child's own experience: what they did, saw, heard and felt (report.md, report.json
    "experience"), written only from what the child perceived;
  * evidence for the Product Manager: the full trace, every utterance with ground truth and
    what the speech model wrote, Buddy's spoken lines, and the server's session record
    (tutor event log). The child never sees these; they let the PM check root causes.
"""
import json

# How a child of each age band would put each problem (no LLM: fixed phrasing per code).
QUOTES = {
    "NAV_TEXT_NOT_FOUND": ("I pressed lots of things but I couldn't find the story.",
                           "I couldn't find where the poems were, so I stopped."),
    "NO_TEXT_FOR_MY_LEVEL": ("The words were too hard. I can't read those yet.",
                             "Everything was for big kids."),
    "WRONG_LANGUAGE_TEXT": ("This isn't my language!", "I wanted a poem in my language but got a different one."),
    "NO_SPOKEN_GUIDANCE_BEFORE_START": ("Nobody told me what to do.", "It didn't say what to do, it was only writing."),
    "LISTEN_FIRST_NOT_FOUND": ("I wanted it to read to me first.", "I couldn't find the button to hear the poem first."),
    "LISTEN_FIRST_STUCK": ("It kept going and going.", "Listen first took too long."),
    "COULD_NOT_START_SESSION": ("It didn't start.", "I couldn't get it to start listening to me."),
    "CONSENT_BLOCKS_CHILD": ("A box came and I didn't know what it said.", "A grown-up box came and I couldn't go on."),
    "CONSENT_SELF_APPROVED": ("", "There was a box for parents, so I just ticked it myself."),
    "BUDDY_LANGUAGE_NOT_UNDERSTOOD": ("I don't know what Buddy said.", "Buddy talked in a language I don't really know."),
    "LONG_TUTOR_TALK": ("Buddy talked too long.", "Buddy talks a lot before I get to read."),
    "SPEECH_IGNORED_WHILE_BUDDY_TALKS": ("I said it but Buddy didn't hear me!", "Buddy didn't hear me when I was talking."),
    "STUCK_WITHOUT_HELP": ("I didn't know the word and nobody helped.", "I got stuck and had to wait."),
    "INTERRUPTED_WHILE_THINKING": ("Buddy talked when I was thinking!", "I was just thinking and Buddy jumped in."),
    "FALSE_CORRECTION": ("But I said it right!", "Buddy said I got a word wrong but I read it right."),
    "FALSE_CORRECTION_STT": ("But I said it right!", "I read it right but Buddy heard something else."),
    "CORRECTED_A_WORD_NOT_YET_READ": ("Why that word?", "Buddy asked me about a word I didn't even read yet."),
    "SAME_WORD_ASKED_AGAIN_AND_AGAIN": ("Again? I said it already!", "Buddy made me say the same word again and again."),
    "MIC_TAP_PAUSED_SESSION": ("I pressed the mic to talk and it stopped!", "I pressed the microphone and it paused."),
    "HARD_TO_RESUME": ("It stopped and I didn't know how to make it go.", "It paused and I didn't know how to carry on."),
    "BREAK_REQUEST_IGNORED": ("I'm tired but it kept going.", "I said I was tired but Buddy didn't stop."),
    "LEFT_READING_BY_ACCIDENT": ("Where did my poem go?", "I pressed something and the poem went away."),
    "SESSION_STOPPED_UNEXPECTEDLY": ("It just stopped.", "It stopped by itself."),
}
POSITIVE = {
    "praise": ("Buddy said yay! I liked that.", "I liked it when Buddy said well done."),
    "finished": ("I did it!", "I finished the whole poem!"),
    "helped": ("Buddy helped me with the hard word.", "When I got stuck Buddy told me the words."),
}

SEVERITY_HINT = {  # the child's own sense of how bad it was (the PM decides real severity)
    "NAV_TEXT_NOT_FOUND": "blocked", "COULD_NOT_START_SESSION": "blocked", "CONSENT_BLOCKS_CHILD": "blocked",
    "NO_TEXT_FOR_MY_LEVEL": "blocked", "SESSION_STOPPED_UNEXPECTEDLY": "blocked",
    "FALSE_CORRECTION": "upsetting", "FALSE_CORRECTION_STT": "upsetting", "INTERRUPTED_WHILE_THINKING": "upsetting",
    "SAME_WORD_ASKED_AGAIN_AND_AGAIN": "upsetting", "MIC_TAP_PAUSED_SESSION": "confusing",
    "SPEECH_IGNORED_WHILE_BUDDY_TALKS": "confusing", "NO_SPOKEN_GUIDANCE_BEFORE_START": "confusing",
    "BUDDY_LANGUAGE_NOT_UNDERSTOOD": "confusing", "CONSENT_SELF_APPROVED": "risk",
}


def _quote(agent, code):
    q = QUOTES.get(code, ("Something went wrong.", "Something went wrong."))
    young = agent.p.pre_primary or agent.p.age < 6
    return q[0] if young and q[0] else q[1]


def ux_scores(agent, summary) -> dict:
    """1 (bad) .. 5 (good), from observed facts only."""
    m = agent.metrics
    started = agent.session_started_at is not None
    disc = 5 if m["nav_clicks"] <= 3 else 4 if m["nav_clicks"] <= 5 else 3 if started else 1
    guid = 5 - min(4, sum(1 for c in ("NO_SPOKEN_GUIDANCE_BEFORE_START", "BUDDY_LANGUAGE_NOT_UNDERSTOOD",
                                      "CONSENT_BLOCKS_CHILD", "LISTEN_FIRST_NOT_FOUND", "HARD_TO_RESUME") if c in agent.issues) * 1.5)
    inter = 5 - min(4, m["interruptions"] + (1 if m["unheard_words"] else 0) + (1 if "MIC_TAP_PAUSED_SESSION" in agent.issues else 0))
    fc = sum(agent.issues[c]["count"] for c in ("FALSE_CORRECTION", "FALSE_CORRECTION_STT") if c in agent.issues)
    corr = 5 - min(4, fc * 1.5 + (1 if "SAME_WORD_ASKED_AGAIN_AND_AGAIN" in agent.issues else 0))
    words_total = (summary or {}).get("words_total") or max(1, agent.text_meta.get("words", 1))
    covered = ((summary or {}).get("words_read", 0) + (summary or {}).get("words_helped", 0))
    comp = 1 + round(4 * min(1.0, covered / words_total)) if started else 1
    enjoy = max(1, min(5, 3 + min(2, m["praise_heard"]) - round(agent.affect.peak)))
    return {"discoverability": disc, "guidance": round(guid), "interruption_load": inter,
            "correction_quality": round(corr), "completion": comp, "enjoyment": enjoy}


def build(agent, record, error) -> dict:
    out = agent.out
    summary = agent.summary or (record or {}).get("summary")
    words_total = (summary or {}).get("words_total") or agent.text_meta.get("words")
    # ground-truth comparison against Buddy's final word colours (what the child saw at the end)
    final_status = (agent.last_state or {}).get("status")
    wrong_unflagged = []
    if final_status:
        for j, tries in agent.attempts.items():
            reading = [a for a in tries if not a.get("drill")]
            if reading and not reading[-1]["correct"] and j < len(final_status) and final_status[j] == "read":
                wrong_unflagged.append({"word": reading[-1]["target"], "child_said": reading[-1]["said"],
                                        "kind": reading[-1]["kind"], "speech_model_wrote": reading[-1]["stt"]})
    if wrong_unflagged:
        agent.issues.setdefault("MISSED_ERROR", {"code": "MISSED_ERROR", "count": len(wrong_unflagged),
                                                 "evidence_level": "observed", "first_t": None,
                                                 "details": [f"Read '{w['word']}' as '{w['child_said']}' and it was "
                                                             "marked as read correctly." for w in wrong_unflagged[:6]],
                                                 "evidence": wrong_unflagged[:6]})
    positives = []
    if agent.metrics["praise_heard"]:
        positives.append(POSITIVE["praise"][0 if agent.p.pre_primary else 1])
    if summary and summary.get("finished"):
        positives.append(POSITIVE["finished"][0 if agent.p.pre_primary else 1])
    if any(s.get("kind", "").startswith("stall") for s in agent.buddy_said) and agent.metrics["praise_heard"]:
        positives.append(POSITIVE["helped"][0 if agent.p.pre_primary else 1])
    issues = []
    for code, rec in agent.issues.items():
        issues.append({**rec, "child_quote": _quote(agent, code) if code in QUOTES else "",
                       "child_severity": SEVERITY_HINT.get(code, "annoying")})
    issues.sort(key=lambda r: (r["first_t"] is None, r["first_t"] or 0))
    n_attempted = sum(1 for t in agent.attempts.values() if any(not a.get("drill") for a in t))
    n_wrong = sum(1 for t in agent.attempts.values()
                  if [a for a in t if not a.get("drill")] and not [a for a in t if not a.get("drill")][-1]["correct"])
    corrections = [c for c in agent.corrections if c["kind"] == "fix_word"]
    report = {
        "schema": "reading-buddy.child-report.v1",
        "run_id": agent.run_id, "agent_id": agent.p.id, "seed": agent.seed,
        "persona": {k: getattr(agent.p, k) for k in ("id", "name", "grade", "age", "reading_proficiency",
                                                       "language_preference", "journey", "grown_up_setup",
                                                       "technology_familiarity", "patience", "attention_span_s")},
        "outcome": agent.outcome, "harness_error": error,
        "text": agent.text_meta,
        "experience": {"issues": issues, "positives": positives,
                       "frustration_peak": round(agent.affect.peak, 2),
                       "frustration_events": agent.affect.events},
        "metrics": {**{k: (round(v, 1) if isinstance(v, float) else v) for k, v in agent.metrics.items()},
                    "words_total": words_total, "words_attempted": n_attempted, "words_said_wrong": n_wrong,
                    "corrections": len(corrections),
                    "buddy_turns": len(agent.buddy_said),
                    "stall_prompts": sum(1 for s in agent.buddy_said if (s.get("kind") or "").startswith("stall")),
                    "uncertain_prompts": sum(1 for s in agent.buddy_said if (s.get("kind") or "").startswith("uncertain"))},
        "tutor_summary": summary,
        "ux_scores": ux_scores(agent, summary),
        "artefacts": {"screens": agent.shots, "trace": "trace.jsonl", "ws": "ws.jsonl",
                      "utterances": "utterances.json", "server_record": "server_record.json"},
        "simulation_notes": {"tts_placeholder_clips": (record or {}).get("tts_offline"),
                             "speech": "simulated STT (zero credits); child speech and recognition errors are modelled"},
    }
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    (out / "trace.jsonl").write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in agent.trace))
    (out / "ws.jsonl").write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in agent.ws_log))
    (out / "utterances.json").write_text(json.dumps({"utterances": agent.utterances,
                                                     "attempts": {str(k): v for k, v in agent.attempts.items()},
                                                     "buddy_said": agent.buddy_said}, ensure_ascii=False, indent=1))
    if record:
        (out / "server_record.json").write_text(json.dumps(record, ensure_ascii=False, indent=1))
    (out / "report.md").write_text(render_md(agent, report), encoding="utf-8")
    return report


def render_md(agent, r) -> str:
    p = agent.p
    lines = [f"# {p.id} · {p.name}, {p.grade} ({p.age:g} y) · {p.language_preference}",
             "", f"*Journey:* {p.journey} · *Outcome:* **{r['outcome']}**", ""]
    if r["text"]:
        lines.append(f"*Text:* {r['text'].get('title')} ({', '.join(r['text'].get('tags', []))})")
    lines += ["", "## In my words", ""]
    said = [i["child_quote"] for i in r["experience"]["issues"] if i["child_quote"]]
    for q in said[:6] + r["experience"]["positives"]:
        lines.append(f"> {q}")
    if not said and not r["experience"]["positives"]:
        lines.append("> (nothing to say)")
    lines += ["", "## What happened (observed)", ""]
    for i in r["experience"]["issues"]:
        lines.append(f"- **{i['code']}** ×{i['count']} ({i['evidence_level']}): {i['details'][0] if i['details'] else ''}")
    m = r["metrics"]
    lines += ["", "## Numbers", "",
              f"taps {m['clicks']} (dead {m['dead_clicks']}) · time to text {m.get('time_to_text_s')} s · "
              f"intro {m.get('intro_s')} s · first word {m.get('time_to_first_word_s')} s · "
              f"words attempted {m['words_attempted']}/{m['words_total']} · said wrong {m['words_said_wrong']} · "
              f"corrections {m['corrections']} · stall prompts {m['stall_prompts']} · interruptions {m['interruptions']} · "
              f"unheard words {m['unheard_words']} · frustration peak {r['experience']['frustration_peak']}/{p.patience}",
              "", "UX scores (1-5): " + ", ".join(f"{k} {v}" for k, v in r["ux_scores"].items()), ""]
    if r["artefacts"]["screens"]:
        lines.append("Screenshots: " + ", ".join(r["artefacts"]["screens"]))
    return "\n".join(lines) + "\n"
