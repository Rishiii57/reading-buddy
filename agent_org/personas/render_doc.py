"""Writes docs/agent-org/PERSONA_LIBRARY.md from library.json (python -m agent_org.personas.render_doc)."""
from collections import Counter
from pathlib import Path

from .persona import GRADES, load

DOC = Path(__file__).resolve().parent.parent.parent / "docs" / "agent-org" / "PERSONA_LIBRARY.md"
LANG = {"en-IN": "English", "hi-IN": "Hindi", "gu-IN": "Gujarati"}


def main():
    ps = load()
    g = Counter(p.grade for p in ps)
    lang = Counter(p.language_preference for p in ps)
    L = ["# Persona library", "",
         "50 synthetic child personas, Nursery to Class 4. They are **testing profiles, not real children**: no real "
         "child's data, voice or likeness is used. Source of truth: `agent_org/personas/build_library.py` → "
         "`library.json` (validated by `persona.load()`); this page is generated from it.", "",
         "## Distribution", "",
         "| Grade | " + " | ".join(GRADES) + " | Total |", "|---" * (len(GRADES) + 2) + "|",
         "| Agents | " + " | ".join(str(g[x]) for x in GRADES) + f" | {len(ps)} |", "",
         "| Language preference | English | Hindi | Gujarati |", "|---|---|---|---|",
         f"| Agents | {lang['en-IN']} | {lang['hi-IN']} | {lang['gu-IN']} |", "",
         "| Grade × language | English | Hindi | Gujarati |", "|---|---|---|---|"]
    for gr in GRADES:
        c = Counter(p.language_preference for p in ps if p.grade == gr)
        L.append(f"| {gr} | {c['en-IN']} | {c['hi-IN']} | {c['gu-IN']} |")
    L += ["", "The spec's suggested split (Nursery 10, LKG 8, UKG 8, Class 1–4 six each) is kept: pre-primary children are "
          "the least served by the current content and the most sensitive to interface and timing problems, so they "
          "get the most agents.", "",
          "Journeys: " + ", ".join(f"{k} {v}" for k, v in Counter(p.journey for p in ps).most_common()) + ". "
          f"{sum(1 for p in ps if not p.grown_up_setup)} children start without a grown-up having set up the microphone.", "",
          "## How a persona drives behaviour", "",
          "- **Reading**: `can_decode`, `word_accuracy` (scaled by how well they read that script), `echo_skill` (repeating what "
          "Buddy just said), `words_per_s`, mistakes (`common_mistakes` → concrete substitutions such as b/d swaps, "
          "first-letter guesses, dropped endings, matra/nasal/conjunct errors), skips of small words, repeats, self-corrections.",
          "- **Pauses**: `p_hesitate` and `hesitation_s` (thinking pauses mid-line), word-by-word gaps.",
          "- **Speech channel**: `volume` (quiet speech loses words), language comfort, an assumed young-voice error penalty.",
          "- **Interface**: `ui_english_reading` (can they read the English buttons?), script recognition per language, "
          "`technology_familiarity`, curious off-task taps, tapping the mic to talk, talking over Buddy.",
          "- **Endurance**: `attention_span_s`, `patience` (objective frustration threshold), saying they are tired.",
          "- **Task**: `journey` (discover and start, listen then read, read a whole poem, make mistakes, explore, replay a line, restart).", "",
          "## Overview", "",
          "| ID | Name | Grade | Age | Proficiency | Language | Reads English UI | Mistakes | Style | Journey | Grown-up set up |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for p in ps:
        L.append(f"| {p.id} | {p.name} | {p.grade} | {p.age:g} | {p.reading_proficiency} | {LANG[p.language_preference]} | "
                 f"{p.ui_english_reading:.2f} | {', '.join(p.common_mistakes) or '-'} | {p.interaction_style[:60]} | {p.journey} | "
                 f"{'yes' if p.grown_up_setup else 'no'} |")
    L += ["", "## Profiles", ""]
    for p in ps:
        b = p.behaviour
        langs = "; ".join(f"{LANG[k]} speak {v['speak']:.2f} / read {v['read']:.2f}" for k, v in p.languages.items())
        L += [f"### {p.id} · {p.name} ({p.grade}, ~{p.age:g} years)", "",
              f"1. **ID** {p.id} · 2. **Grade/age** {p.grade}, {p.age:g} · 3. **Reading proficiency** {p.reading_proficiency} "
              f"· 4. **Language preference** {LANG[p.language_preference]} ({langs}) · 5. **Vocabulary** {p.vocabulary_level} "
              f"· 6. **Pronunciation** {p.pronunciation['accuracy']:.2f} {p.pronunciation.get('notes', '')} · 7. **Attention span** "
              f"{p.attention_span_s:g} s · 8. **Confidence** {p.confidence:.2f} · 9. **Patience** {p.patience:g} · 10. **Learning "
              f"preferences** {', '.join(p.learning_preferences) or '-'} · 11. **Common mistakes** {', '.join(p.common_mistakes) or '-'} "
              f"· 12. **Technology familiarity** {p.technology_familiarity:.2f} · 13. **Interaction style** {p.interaction_style or '-'} "
              f"· 14. **Testing objectives** {'; '.join(p.testing_objectives)}", "",
              f"Behaviour: {b.words_per_s:g} words/s, accuracy {b.word_accuracy:.2f}, echo {b.echo_skill:.2f}, decodes "
              f"{'yes' if b.can_decode else 'no'}, skips small words {b.p_skip_small:.2f}, hesitates {b.p_hesitate:.2f} "
              f"({b.hesitation_s[0]:g}-{b.hesitation_s[1]:g} s), self-corrects {b.p_self_correct:.2f}, volume {b.volume:.2f}, "
              f"talks over Buddy {b.p_talk_over_buddy:.2f}, taps mic to talk {b.p_tap_mic_to_talk:.2f}, curious taps "
              f"{b.p_off_task_click:.2f}" + (f", says tired after {b.says_tired_after_s:g} s" if b.says_tired_after_s else "")
              + f". Seed {p.seed}. {p.profile_note}", ""]
    DOC.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(DOC)


if __name__ == "__main__":
    main()
