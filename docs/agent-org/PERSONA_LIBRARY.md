# Persona library

50 synthetic child personas, Nursery to Class 4. They are **testing profiles, not real children**: no real child's data, voice or likeness is used. Source of truth: `agent_org/personas/build_library.py` → `library.json` (validated by `persona.load()`); this page is generated from it.

## Distribution

| Grade | Nursery | LKG | UKG | Class 1 | Class 2 | Class 3 | Class 4 | Total |
|---|---|---|---|---|---|---|---|---|
| Agents | 10 | 8 | 8 | 6 | 6 | 6 | 6 | 50 |

| Language preference | English | Hindi | Gujarati |
|---|---|---|---|
| Agents | 17 | 17 | 16 |

| Grade × language | English | Hindi | Gujarati |
|---|---|---|---|
| Nursery | 4 | 3 | 3 |
| LKG | 3 | 3 | 2 |
| UKG | 2 | 3 | 3 |
| Class 1 | 2 | 2 | 2 |
| Class 2 | 2 | 2 | 2 |
| Class 3 | 2 | 2 | 2 |
| Class 4 | 2 | 2 | 2 |

The spec's suggested split (Nursery 10, LKG 8, UKG 8, Class 1–4 six each) is kept: pre-primary children are the least served by the current content and the most sensitive to interface and timing problems, so they get the most agents.

Journeys: read_whole_poem 18, make_mistakes 8, listen_then_read 6, explore_and_read 6, discover_and_start 5, restart_session 4, replay_line 3. 10 children start without a grown-up having set up the microphone.

## How a persona drives behaviour

- **Reading**: `can_decode`, `word_accuracy` (scaled by how well they read that script), `echo_skill` (repeating what Buddy just said), `words_per_s`, mistakes (`common_mistakes` → concrete substitutions such as b/d swaps, first-letter guesses, dropped endings, matra/nasal/conjunct errors), skips of small words, repeats, self-corrections.
- **Pauses**: `p_hesitate` and `hesitation_s` (thinking pauses mid-line), word-by-word gaps.
- **Speech channel**: `volume` (quiet speech loses words), language comfort, an assumed young-voice error penalty.
- **Interface**: `ui_english_reading` (can they read the English buttons?), script recognition per language, `technology_familiarity`, curious off-task taps, tapping the mic to talk, talking over Buddy.
- **Endurance**: `attention_span_s`, `patience` (objective frustration threshold), saying they are tired.
- **Task**: `journey` (discover and start, listen then read, read a whole poem, make mistakes, explore, replay a line, restart).

## Overview

| ID | Name | Grade | Age | Proficiency | Language | Reads English UI | Mistakes | Style | Journey | Grown-up set up |
|---|---|---|---|---|---|---|---|---|---|---|
| N01 | Aarav | Nursery | 3.5 | pre_reader | English | 0.00 | drops_endings, word_by_word | taps big colourful things; repeats what he hears; cannot rea | discover_and_start | no |
| N02 | Anaya | Nursery | 3.5 | pre_reader | Hindi | 0.00 | word_by_word | loves listening, rarely speaks up; whispers when she does | listen_then_read | yes |
| N03 | Vihaan | Nursery | 3.5 | pre_reader | Gujarati | 0.00 | word_by_word | taps everything on the screen, fast and often | discover_and_start | no |
| N04 | Saanvi | Nursery | 3.5 | pre_reader | English | 0.00 | word_by_word | loud and eager, says words as soon as he hears them | read_whole_poem | yes |
| N05 | Reyansh | Nursery | 3.5 | pre_reader | Hindi | 0.00 | word_by_word | very quiet, long silences before answering | discover_and_start | yes |
| N06 | Diya | Nursery | 3.5 | pre_reader | Gujarati | 0.00 | word_by_word | asks for things to be said again | replay_line | yes |
| N07 | Arjun | Nursery | 3.5 | pre_reader | English | 0.00 | word_by_word | gets tired quickly and says so | read_whole_poem | yes |
| N08 | Myra | Nursery | 3.5 | pre_reader | Hindi | 0.00 | adds_words, repeats_words | mixes Hindi and English words, repeats words | read_whole_poem | no |
| N09 | Advik | Nursery | 3.5 | pre_reader | Gujarati | 0.00 | word_by_word | patient; speech sounds still developing | listen_then_read | yes |
| N10 | Kiara | Nursery | 4.2 | emergent | English | 0.00 | word_by_word | knows some letters, likes doing things again | restart_session | yes |
| L01 | Ishita | LKG | 4.5 | emergent | Hindi | 0.05 | letter_confusion, guesses_from_first_letter, word_by_word | waits for instructions, gets upset when told to repeat a wor | listen_then_read | yes |
| L02 | Ayaan | LKG | 4.5 | emergent | English | 0.05 | letter_confusion, word_by_word | mixes up b/d and p/q | make_mistakes | yes |
| L03 | Aadhya | LKG | 4.5 | emergent | Gujarati | 0.05 | guesses_from_first_letter | chatty, guesses words from pictures | discover_and_start | no |
| L04 | Vivaan | LKG | 4.5 | emergent | English | 0.05 | word_by_word | fast and impatient, wants to finish quickly | read_whole_poem | yes |
| L05 | Prisha | LKG | 4.5 | emergent | Hindi | 0.05 | word_by_word | careful and slow, long pauses between words | read_whole_poem | yes |
| L06 | Krish | LKG | 4.5 | emergent | Gujarati | 0.05 | word_by_word | likes to hear things first | listen_then_read | yes |
| L07 | Anvi | LKG | 4.5 | emergent | English | 0.05 | word_by_word | loves praise, tries hard, many mistakes | restart_session | yes |
| L08 | Shaurya | LKG | 4.5 | emergent | Hindi | 0.05 | word_by_word | says when tired | read_whole_poem | yes |
| U01 | Dhruv | UKG | 5.5 | early | Gujarati | 0.20 | word_by_word, matra_errors, loses_place | reads one word at a time with long gaps between words | read_whole_poem | yes |
| U02 | Navya | UKG | 5.5 | early | English | 0.15 | word_by_word, skips_small_words | reads single words but struggles to join them | read_whole_poem | yes |
| U03 | Atharv | UKG | 5.5 | early | Hindi | 0.10 | matra_errors, nasal_errors | drops and swaps matras | make_mistakes | yes |
| U04 | Riya | UKG | 5.5 | early | Gujarati | 0.10 | conjunct_errors, loses_place | gets upset quickly; taps mic to talk | discover_and_start | no |
| U05 | Hridaan | UKG | 5.5 | early | Hindi | 0.15 | - | wants to choose a story herself | explore_and_read | yes |
| U06 | Tara | UKG | 5.5 | early | English | 0.35 | - | tech-savvy; explores every button | explore_and_read | yes |
| U07 | Yash | UKG | 5.5 | early | Gujarati | 0.10 | - | reads in a whisper | read_whole_poem | yes |
| U08 | Pari | UKG | 5.5 | early | Hindi | 0.10 | repeats_words, self_corrects | repeats words, corrects himself | replay_line | yes |
| C1-01 | Rudra | Class 1 | 6.5 | early | English | 0.35 | skips_small_words | skips small words like 'a' and 'the' | read_whole_poem | yes |
| C1-02 | Ira | Class 1 | 6.5 | early | Hindi | 0.35 | letter_confusion | confuses ब/व, श/स | make_mistakes | yes |
| C1-03 | Dev | Class 1 | 6.5 | early | Gujarati | 0.10 | word_by_word | slow, word by word | read_whole_poem | yes |
| C1-04 | Jiya | Class 1 | 6.5 | early | English | 0.35 | - | reads English letters but follows spoken English with diffic | listen_then_read | yes |
| C1-05 | Om | Class 1 | 6.5 | early | Hindi | 0.10 | - | confident, races ahead, talks over Buddy | read_whole_poem | no |
| C1-06 | Siya | Class 1 | 6.5 | early | Gujarati | 0.10 | - | tires after a couple of minutes | read_whole_poem | yes |
| C2-01 | Kabir | Class 2 | 7.5 | developing | English | 0.70 | reads_too_fast, guesses_from_first_letter, drops_endings, skips_small_words | confident, reads fast, talks over Buddy, impatient with corr | make_mistakes | no |
| C2-02 | Neel | Class 2 | 7.5 | developing | Hindi | 0.10 | monotone | accurate but flat | read_whole_poem | yes |
| C2-03 | Avni | Class 2 | 7.5 | developing | Gujarati | 0.60 | matra_errors, guesses_from_first_letter | speaks Gujarati well, reads it poorly | make_mistakes | yes |
| C2-04 | Kian | Class 2 | 7.5 | developing | English | 0.60 | loses_place, repeats_words | loses place and restarts lines | restart_session | yes |
| C2-05 | Mahi | Class 2 | 7.5 | developing | Hindi | 0.10 | adds_words, self_corrects | adds words, corrects herself | make_mistakes | yes |
| C2-06 | Parth | Class 2 | 7.5 | developing | Gujarati | 0.60 | - | independent; reads the screen | explore_and_read | no |
| C3-01 | Zoya | Class 3 | 8.5 | developing | English | 0.75 | monotone | fluent but no expression | read_whole_poem | yes |
| C3-02 | Rohan | Class 3 | 8.5 | developing | Hindi | 0.10 | conjunct_errors | trips on joined letters | make_mistakes | yes |
| C3-03 | Nisha | Class 3 | 8.5 | developing | Gujarati | 0.10 | reads_too_fast, drops_endings | rushes, drops endings, talks over Buddy | read_whole_poem | yes |
| C3-04 | Aarush | Class 3 | 8.5 | developing | English | 0.70 | letter_confusion, word_by_word | reverses letters; very persistent | listen_then_read | yes |
| C3-05 | Esha | Class 3 | 8.5 | developing | Hindi | 0.10 | - | likes to hear model reading | replay_line | yes |
| C3-06 | Veer | Class 3 | 8.5 | developing | Gujarati | 0.75 | - | independent; tires after a while | explore_and_read | no |
| C4-01 | Meera | Class 4 | 9.5 | fluent | Hindi | 0.90 | monotone, self_corrects | independent; explores the whole app; reads at natural pace w | explore_and_read | no |
| C4-02 | Trisha | Class 4 | 9.5 | fluent | English | 0.85 | monotone | fluent; needs help with rhythm and intonation | read_whole_poem | yes |
| C4-03 | Manav | Class 4 | 9.5 | fluent | Gujarati | 0.10 | self_corrects | careful, self-corrects | make_mistakes | yes |
| C4-04 | Khushi | Class 4 | 9.5 | fluent | English | 0.85 | - | gets bored with easy texts | explore_and_read | yes |
| C4-05 | Laksh | Class 4 | 9.5 | fluent | Hindi | 0.10 | reads_too_fast, skips_small_words |  | restart_session | yes |
| C4-06 | Ritika | Class 4 | 9.5 | fluent | Gujarati | 0.85 | matra_errors, conjunct_errors | English-medium; Gujarati reading weaker | read_whole_poem | yes |

## Profiles

### N01 · Aarav (Nursery, ~3.5 years)

1. **ID** N01 · 2. **Grade/age** Nursery, 3.5 · 3. **Reading proficiency** pre_reader · 4. **Language preference** English (English speak 0.60 / read 0.00; Hindi speak 0.70 / read 0.00) · 5. **Vocabulary** very small (simple nouns) · 6. **Pronunciation** 0.60 drops final consonants, 'r' sounds like 'w' · 7. **Attention span** 120 s · 8. **Confidence** 0.50 · 9. **Patience** 3 · 10. **Learning preferences** needs_audio_for_everything, likes_pictures, likes_praise · 11. **Common mistakes** drops_endings, word_by_word · 12. **Technology familiarity** 0.40 · 13. **Interaction style** taps big colourful things; repeats what he hears; cannot read any text · 14. **Testing objectives** Can a non-reader start a session alone?; Does Buddy's audio guidance carry a pre-reader through a line?

Behaviour: 0.9 words/s, accuracy 0.00, echo 0.55, decodes no, skips small words 0.50, hesitates 0.60 (2-5 s), self-corrects 0.00, volume 0.70, talks over Buddy 0.25, taps mic to talk 0.35, curious taps 0.12, says tired after 70 s. Seed 101. Cannot read yet. Copies words he has just heard.

### N02 · Anaya (Nursery, ~3.5 years)

1. **ID** N02 · 2. **Grade/age** Nursery, 3.5 · 3. **Reading proficiency** pre_reader · 4. **Language preference** Hindi (Hindi speak 0.80 / read 0.00; English speak 0.30 / read 0.00) · 5. **Vocabulary** small, spoken · 6. **Pronunciation** 0.60 loves listening, rarely speaks up; whispers when she does · 7. **Attention span** 110 s · 8. **Confidence** 0.25 · 9. **Patience** 3 · 10. **Learning preferences** listen_first, likes_songs · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.40 · 13. **Interaction style** loves listening, rarely speaks up; whispers when she does · 14. **Testing objectives** Listen to the poem first, then read it

Behaviour: 0.8 words/s, accuracy 0.00, echo 0.45, decodes no, skips small words 0.40, hesitates 0.80 (2-5 s), self-corrects 0.00, volume 0.40, talks over Buddy 0.20, taps mic to talk 0.30, curious taps 0.12. Seed 1000. Enjoys rhymes read to her but is shy about speaking.

### N03 · Vihaan (Nursery, ~3.5 years)

1. **ID** N03 · 2. **Grade/age** Nursery, 3.5 · 3. **Reading proficiency** pre_reader · 4. **Language preference** Gujarati (Gujarati speak 0.80 / read 0.00; Hindi speak 0.30 / read 0.00) · 5. **Vocabulary** small, spoken · 6. **Pronunciation** 0.60 taps everything on the screen, fast and often · 7. **Attention span** 60 s · 8. **Confidence** 0.60 · 9. **Patience** 2.5 · 10. **Learning preferences** - · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.55 · 13. **Interaction style** taps everything on the screen, fast and often · 14. **Testing objectives** Discover how to start reading without help

Behaviour: 0.8 words/s, accuracy 0.00, echo 0.50, decodes no, skips small words 0.40, hesitates 0.60 (2-5 s), self-corrects 0.00, volume 0.70, talks over Buddy 0.20, taps mic to talk 0.50, curious taps 0.25. Seed 1017. Very curious with tablets; short attention.

### N04 · Saanvi (Nursery, ~3.5 years)

1. **ID** N04 · 2. **Grade/age** Nursery, 3.5 · 3. **Reading proficiency** pre_reader · 4. **Language preference** English (English speak 0.75 / read 0.00; Hindi speak 0.60 / read 0.00) · 5. **Vocabulary** small, spoken · 6. **Pronunciation** 0.60 loud and eager, says words as soon as he hears them · 7. **Attention span** 110 s · 8. **Confidence** 0.90 · 9. **Patience** 3 · 10. **Learning preferences** - · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.50 · 13. **Interaction style** loud and eager, says words as soon as he hears them · 14. **Testing objectives** Read an entire poem

Behaviour: 0.8 words/s, accuracy 0.00, echo 0.80, decodes no, skips small words 0.40, hesitates 0.60 (2-5 s), self-corrects 0.00, volume 1.00, talks over Buddy 0.40, taps mic to talk 0.30, curious taps 0.12. Seed 1034. Knows many nursery rhymes by heart; repeats eagerly.

### N05 · Reyansh (Nursery, ~3.5 years)

1. **ID** N05 · 2. **Grade/age** Nursery, 3.5 · 3. **Reading proficiency** pre_reader · 4. **Language preference** Hindi (Hindi speak 0.75 / read 0.00) · 5. **Vocabulary** small, spoken · 6. **Pronunciation** 0.60 very quiet, long silences before answering · 7. **Attention span** 110 s · 8. **Confidence** 0.20 · 9. **Patience** 3.5 · 10. **Learning preferences** - · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.40 · 13. **Interaction style** very quiet, long silences before answering · 14. **Testing objectives** Discover how to start reading without help

Behaviour: 0.8 words/s, accuracy 0.00, echo 0.50, decodes no, skips small words 0.40, hesitates 0.90 (3-7 s), self-corrects 0.00, volume 0.35, talks over Buddy 0.20, taps mic to talk 0.30, curious taps 0.12. Seed 1051. Shy; speaks in a whisper.

### N06 · Diya (Nursery, ~3.5 years)

1. **ID** N06 · 2. **Grade/age** Nursery, 3.5 · 3. **Reading proficiency** pre_reader · 4. **Language preference** Gujarati (Gujarati speak 0.85 / read 0.00; English speak 0.10 / read 0.00) · 5. **Vocabulary** small, spoken · 6. **Pronunciation** 0.60 asks for things to be said again · 7. **Attention span** 110 s · 8. **Confidence** 0.60 · 9. **Patience** 3 · 10. **Learning preferences** wants_replay, needs_audio_for_everything · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.40 · 13. **Interaction style** asks for things to be said again · 14. **Testing objectives** Hear a line again when unsure

Behaviour: 0.8 words/s, accuracy 0.00, echo 0.55, decodes no, skips small words 0.40, hesitates 0.60 (2-5 s), self-corrects 0.00, volume 0.70, talks over Buddy 0.20, taps mic to talk 0.30, curious taps 0.12. Seed 1068. Speaks only Gujarati at home; wants to hear things twice.

### N07 · Arjun (Nursery, ~3.5 years)

1. **ID** N07 · 2. **Grade/age** Nursery, 3.5 · 3. **Reading proficiency** pre_reader · 4. **Language preference** English (English speak 0.55 / read 0.00; Hindi speak 0.80 / read 0.00) · 5. **Vocabulary** small, spoken · 6. **Pronunciation** 0.60 gets tired quickly and says so · 7. **Attention span** 80 s · 8. **Confidence** 0.60 · 9. **Patience** 3 · 10. **Learning preferences** - · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.40 · 13. **Interaction style** gets tired quickly and says so · 14. **Testing objectives** Read an entire poem

Behaviour: 0.8 words/s, accuracy 0.00, echo 0.50, decodes no, skips small words 0.40, hesitates 0.60 (2-5 s), self-corrects 0.00, volume 0.70, talks over Buddy 0.20, taps mic to talk 0.30, curious taps 0.12, says tired after 45 s. Seed 1085. English-medium school, Hindi at home; tires fast.

### N08 · Myra (Nursery, ~3.5 years)

1. **ID** N08 · 2. **Grade/age** Nursery, 3.5 · 3. **Reading proficiency** pre_reader · 4. **Language preference** Hindi (Hindi speak 0.70 / read 0.00; English speak 0.50 / read 0.00) · 5. **Vocabulary** small, spoken · 6. **Pronunciation** 0.60 mixes Hindi and English words, repeats words · 7. **Attention span** 110 s · 8. **Confidence** 0.60 · 9. **Patience** 3 · 10. **Learning preferences** - · 11. **Common mistakes** adds_words, repeats_words · 12. **Technology familiarity** 0.40 · 13. **Interaction style** mixes Hindi and English words, repeats words · 14. **Testing objectives** Read an entire poem

Behaviour: 0.8 words/s, accuracy 0.00, echo 0.50, decodes no, skips small words 0.40, hesitates 0.60 (2-5 s), self-corrects 0.00, volume 0.70, talks over Buddy 0.20, taps mic to talk 0.30, curious taps 0.12. Seed 1102. Code-mixes Hindi and English.

### N09 · Advik (Nursery, ~3.5 years)

1. **ID** N09 · 2. **Grade/age** Nursery, 3.5 · 3. **Reading proficiency** pre_reader · 4. **Language preference** Gujarati (Gujarati speak 0.60 / read 0.00) · 5. **Vocabulary** small, spoken · 6. **Pronunciation** 0.45 patient; speech sounds still developing · 7. **Attention span** 110 s · 8. **Confidence** 0.60 · 9. **Patience** 5 · 10. **Learning preferences** listen_first · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.40 · 13. **Interaction style** patient; speech sounds still developing · 14. **Testing objectives** Listen to the poem first, then read it

Behaviour: 0.8 words/s, accuracy 0.00, echo 0.40, decodes no, skips small words 0.40, hesitates 0.60 (2-5 s), self-corrects 0.00, volume 0.70, talks over Buddy 0.20, taps mic to talk 0.30, curious taps 0.12. Seed 1119. Speech sounds still developing (r/l, s/sh).

### N10 · Kiara (Nursery, ~4.2 years)

1. **ID** N10 · 2. **Grade/age** Nursery, 4.2 · 3. **Reading proficiency** emergent · 4. **Language preference** English (English speak 0.80 / read 0.10; Hindi speak 0.40 / read 0.00) · 5. **Vocabulary** small · 6. **Pronunciation** 0.65 knows some letters, likes doing things again · 7. **Attention span** 110 s · 8. **Confidence** 0.60 · 9. **Patience** 3 · 10. **Learning preferences** - · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.60 · 13. **Interaction style** knows some letters, likes doing things again · 14. **Testing objectives** Finish, then read the same text again

Behaviour: 0.8 words/s, accuracy 0.20, echo 0.70, decodes yes, skips small words 0.40, hesitates 0.60 (2-5 s), self-corrects 0.00, volume 0.70, talks over Buddy 0.20, taps mic to talk 0.30, curious taps 0.12. Seed 1136. Recognises a few letters; loves repeating favourites.

### L01 · Ishita (LKG, ~4.5 years)

1. **ID** L01 · 2. **Grade/age** LKG, 4.5 · 3. **Reading proficiency** emergent · 4. **Language preference** Hindi (Hindi speak 0.85 / read 0.25; English speak 0.40 / read 0.10) · 5. **Vocabulary** small, everyday Hindi words · 6. **Pronunciation** 0.65 confuses ब/व and श/स; similar-looking letters · 7. **Attention span** 150 s · 8. **Confidence** 0.45 · 9. **Patience** 3.5 · 10. **Learning preferences** listen_first, likes_praise · 11. **Common mistakes** letter_confusion, guesses_from_first_letter, word_by_word · 12. **Technology familiarity** 0.50 · 13. **Interaction style** waits for instructions, gets upset when told to repeat a word many times · 14. **Testing objectives** Listen first then read; How word practice treats letter confusions

Behaviour: 0.7 words/s, accuracy 0.45, echo 0.70, decodes yes, skips small words 0.25, hesitates 0.70 (2-4.5 s), self-corrects 0.10, volume 0.60, talks over Buddy 0.10, taps mic to talk 0.15, curious taps 0.06. Seed 201. Knows a few Hindi letters; mixes up letters that look or sound alike.

### L02 · Ayaan (LKG, ~4.5 years)

1. **ID** L02 · 2. **Grade/age** LKG, 4.5 · 3. **Reading proficiency** emergent · 4. **Language preference** English (English speak 0.70 / read 0.25; Hindi speak 0.60 / read 0.00) · 5. **Vocabulary** small · 6. **Pronunciation** 0.65 mixes up b/d and p/q · 7. **Attention span** 140 s · 8. **Confidence** 0.60 · 9. **Patience** 3.3 · 10. **Learning preferences** - · 11. **Common mistakes** letter_confusion, word_by_word · 12. **Technology familiarity** 0.50 · 13. **Interaction style** mixes up b/d and p/q · 14. **Testing objectives** Make reading mistakes and understand the corrections

Behaviour: 0.7 words/s, accuracy 0.40, echo 0.65, decodes yes, skips small words 0.30, hesitates 0.65 (2-4.5 s), self-corrects 0.05, volume 0.70, talks over Buddy 0.15, taps mic to talk 0.20, curious taps 0.08. Seed 1153. Confuses letters that look alike.

### L03 · Aadhya (LKG, ~4.5 years)

1. **ID** L03 · 2. **Grade/age** LKG, 4.5 · 3. **Reading proficiency** emergent · 4. **Language preference** Gujarati (Gujarati speak 0.85 / read 0.20; English speak 0.30 / read 0.00) · 5. **Vocabulary** small · 6. **Pronunciation** 0.65 chatty, guesses words from pictures · 7. **Attention span** 140 s · 8. **Confidence** 0.60 · 9. **Patience** 3.3 · 10. **Learning preferences** - · 11. **Common mistakes** guesses_from_first_letter · 12. **Technology familiarity** 0.50 · 13. **Interaction style** chatty, guesses words from pictures · 14. **Testing objectives** Discover how to start reading without help

Behaviour: 0.7 words/s, accuracy 0.40, echo 0.65, decodes yes, skips small words 0.30, hesitates 0.65 (2-4.5 s), self-corrects 0.05, volume 0.70, talks over Buddy 0.25, taps mic to talk 0.40, curious taps 0.08. Seed 1170. Guesses words from the picture or first letter.

### L04 · Vivaan (LKG, ~4.5 years)

1. **ID** L04 · 2. **Grade/age** LKG, 4.5 · 3. **Reading proficiency** emergent · 4. **Language preference** English (English speak 0.80 / read 0.30) · 5. **Vocabulary** small · 6. **Pronunciation** 0.65 fast and impatient, wants to finish quickly · 7. **Attention span** 90 s · 8. **Confidence** 0.85 · 9. **Patience** 2.5 · 10. **Learning preferences** - · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.50 · 13. **Interaction style** fast and impatient, wants to finish quickly · 14. **Testing objectives** Read an entire poem

Behaviour: 1.2 words/s, accuracy 0.40, echo 0.65, decodes yes, skips small words 0.30, hesitates 0.30 (2-4.5 s), self-corrects 0.05, volume 0.70, talks over Buddy 0.15, taps mic to talk 0.20, curious taps 0.08. Seed 1187. Impatient; dislikes waiting.

### L05 · Prisha (LKG, ~4.5 years)

1. **ID** L05 · 2. **Grade/age** LKG, 4.5 · 3. **Reading proficiency** emergent · 4. **Language preference** Hindi (Hindi speak 0.85 / read 0.30) · 5. **Vocabulary** small · 6. **Pronunciation** 0.65 careful and slow, long pauses between words · 7. **Attention span** 140 s · 8. **Confidence** 0.60 · 9. **Patience** 4.5 · 10. **Learning preferences** - · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.50 · 13. **Interaction style** careful and slow, long pauses between words · 14. **Testing objectives** Read an entire poem

Behaviour: 0.5 words/s, accuracy 0.40, echo 0.65, decodes yes, skips small words 0.30, hesitates 0.85 (3-6 s), self-corrects 0.05, volume 0.70, talks over Buddy 0.15, taps mic to talk 0.20, curious taps 0.08. Seed 1204. Careful, sounds out each letter.

### L06 · Krish (LKG, ~4.5 years)

1. **ID** L06 · 2. **Grade/age** LKG, 4.5 · 3. **Reading proficiency** emergent · 4. **Language preference** Gujarati (Gujarati speak 0.80 / read 0.15; Hindi speak 0.60 / read 0.05) · 5. **Vocabulary** small · 6. **Pronunciation** 0.65 likes to hear things first · 7. **Attention span** 140 s · 8. **Confidence** 0.60 · 9. **Patience** 3.3 · 10. **Learning preferences** listen_first, wants_replay · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.50 · 13. **Interaction style** likes to hear things first · 14. **Testing objectives** Listen to the poem first, then read it

Behaviour: 0.7 words/s, accuracy 0.40, echo 0.65, decodes yes, skips small words 0.30, hesitates 0.65 (2-4.5 s), self-corrects 0.05, volume 0.70, talks over Buddy 0.15, taps mic to talk 0.20, curious taps 0.08. Seed 1221. Bilingual Gujarati-Hindi; reads very little yet.

### L07 · Anvi (LKG, ~4.5 years)

1. **ID** L07 · 2. **Grade/age** LKG, 4.5 · 3. **Reading proficiency** emergent · 4. **Language preference** English (English speak 0.70 / read 0.20; Gujarati speak 0.50 / read 0.00) · 5. **Vocabulary** small · 6. **Pronunciation** 0.65 loves praise, tries hard, many mistakes · 7. **Attention span** 140 s · 8. **Confidence** 0.90 · 9. **Patience** 3.3 · 10. **Learning preferences** likes_praise · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.50 · 13. **Interaction style** loves praise, tries hard, many mistakes · 14. **Testing objectives** Finish, then read the same text again

Behaviour: 0.7 words/s, accuracy 0.35, echo 0.65, decodes yes, skips small words 0.30, hesitates 0.65 (2-4.5 s), self-corrects 0.05, volume 0.70, talks over Buddy 0.15, taps mic to talk 0.20, curious taps 0.08. Seed 1238. Very motivated by stars and praise.

### L08 · Shaurya (LKG, ~4.5 years)

1. **ID** L08 · 2. **Grade/age** LKG, 4.5 · 3. **Reading proficiency** emergent · 4. **Language preference** Hindi (Hindi speak 0.80 / read 0.25) · 5. **Vocabulary** small · 6. **Pronunciation** 0.65 says when tired · 7. **Attention span** 100 s · 8. **Confidence** 0.60 · 9. **Patience** 3.3 · 10. **Learning preferences** - · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.50 · 13. **Interaction style** says when tired · 14. **Testing objectives** Read an entire poem

Behaviour: 0.7 words/s, accuracy 0.40, echo 0.65, decodes yes, skips small words 0.30, hesitates 0.65 (2-4.5 s), self-corrects 0.05, volume 0.70, talks over Buddy 0.15, taps mic to talk 0.20, curious taps 0.08, says tired after 55 s. Seed 1255. Gets tired after a minute of reading.

### U01 · Dhruv (UKG, ~5.5 years)

1. **ID** U01 · 2. **Grade/age** UKG, 5.5 · 3. **Reading proficiency** early · 4. **Language preference** Gujarati (Gujarati speak 0.90 / read 0.50; English speak 0.50 / read 0.30; Hindi speak 0.50 / read 0.10) · 5. **Vocabulary** growing Gujarati vocabulary · 6. **Pronunciation** 0.75 drops matras in longer words · 7. **Attention span** 180 s · 8. **Confidence** 0.55 · 9. **Patience** 4 · 10. **Learning preferences** likes_poems, likes_praise · 11. **Common mistakes** word_by_word, matra_errors, loses_place · 12. **Technology familiarity** 0.60 · 13. **Interaction style** reads one word at a time with long gaps between words · 14. **Testing objectives** Word-by-word reading with pauses; Is a slow reader interrupted?

Behaviour: 0.8 words/s, accuracy 0.70, echo 0.80, decodes yes, skips small words 0.15, hesitates 0.90 (2-4 s), self-corrects 0.20, volume 0.80, talks over Buddy 0.05, taps mic to talk 0.10, curious taps 0.04. Seed 301. Can read single Gujarati words but struggles to string them into a sentence.

### U02 · Navya (UKG, ~5.5 years)

1. **ID** U02 · 2. **Grade/age** UKG, 5.5 · 3. **Reading proficiency** early · 4. **Language preference** English (English speak 0.75 / read 0.50; Hindi speak 0.50 / read 0.10) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 reads single words but struggles to join them · 7. **Attention span** 170 s · 8. **Confidence** 0.60 · 9. **Patience** 3.8 · 10. **Learning preferences** - · 11. **Common mistakes** word_by_word, skips_small_words · 12. **Technology familiarity** 0.55 · 13. **Interaction style** reads single words but struggles to join them · 14. **Testing objectives** Read an entire poem

Behaviour: 0.9 words/s, accuracy 0.60, echo 0.75, decodes yes, skips small words 0.35, hesitates 0.80 (1.8-4 s), self-corrects 0.10, volume 0.80, talks over Buddy 0.10, taps mic to talk 0.12, curious taps 0.06. Seed 1272. Can read words, not yet sentences.

### U03 · Atharv (UKG, ~5.5 years)

1. **ID** U03 · 2. **Grade/age** UKG, 5.5 · 3. **Reading proficiency** early · 4. **Language preference** Hindi (Hindi speak 0.85 / read 0.50) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 drops and swaps matras · 7. **Attention span** 170 s · 8. **Confidence** 0.60 · 9. **Patience** 3.8 · 10. **Learning preferences** - · 11. **Common mistakes** matra_errors, nasal_errors · 12. **Technology familiarity** 0.55 · 13. **Interaction style** drops and swaps matras · 14. **Testing objectives** Make reading mistakes and understand the corrections

Behaviour: 0.9 words/s, accuracy 0.60, echo 0.75, decodes yes, skips small words 0.20, hesitates 0.60 (1.8-4 s), self-corrects 0.10, volume 0.80, talks over Buddy 0.10, taps mic to talk 0.12, curious taps 0.06. Seed 1289. Mixes up short and long vowel signs.

### U04 · Riya (UKG, ~5.5 years)

1. **ID** U04 · 2. **Grade/age** UKG, 5.5 · 3. **Reading proficiency** early · 4. **Language preference** Gujarati (Gujarati speak 0.85 / read 0.45) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 gets upset quickly; taps mic to talk · 7. **Attention span** 170 s · 8. **Confidence** 0.60 · 9. **Patience** 2.8 · 10. **Learning preferences** - · 11. **Common mistakes** conjunct_errors, loses_place · 12. **Technology familiarity** 0.55 · 13. **Interaction style** gets upset quickly; taps mic to talk · 14. **Testing objectives** Discover how to start reading without help

Behaviour: 0.9 words/s, accuracy 0.60, echo 0.75, decodes yes, skips small words 0.20, hesitates 0.60 (1.8-4 s), self-corrects 0.10, volume 0.80, talks over Buddy 0.10, taps mic to talk 0.25, curious taps 0.06. Seed 1306. Struggles with joined letters; low frustration tolerance.

### U05 · Hridaan (UKG, ~5.5 years)

1. **ID** U05 · 2. **Grade/age** UKG, 5.5 · 3. **Reading proficiency** early · 4. **Language preference** Hindi (Hindi speak 0.90 / read 0.50; English speak 0.40 / read 0.20) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 wants to choose a story herself · 7. **Attention span** 170 s · 8. **Confidence** 0.60 · 9. **Patience** 3.8 · 10. **Learning preferences** - · 11. **Common mistakes** - · 12. **Technology familiarity** 0.55 · 13. **Interaction style** wants to choose a story herself · 14. **Testing objectives** Explore the library and pick something suitable, then read

Behaviour: 0.9 words/s, accuracy 0.60, echo 0.75, decodes yes, skips small words 0.20, hesitates 0.60 (1.8-4 s), self-corrects 0.10, volume 0.80, talks over Buddy 0.10, taps mic to talk 0.12, curious taps 0.06. Seed 1323. Wants to pick her own story.

### U06 · Tara (UKG, ~5.5 years)

1. **ID** U06 · 2. **Grade/age** UKG, 5.5 · 3. **Reading proficiency** early · 4. **Language preference** English (English speak 0.85 / read 0.50) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 tech-savvy; explores every button · 7. **Attention span** 170 s · 8. **Confidence** 0.60 · 9. **Patience** 3.8 · 10. **Learning preferences** - · 11. **Common mistakes** - · 12. **Technology familiarity** 0.90 · 13. **Interaction style** tech-savvy; explores every button · 14. **Testing objectives** Explore the library and pick something suitable, then read

Behaviour: 0.9 words/s, accuracy 0.60, echo 0.75, decodes yes, skips small words 0.20, hesitates 0.60 (1.8-4 s), self-corrects 0.10, volume 0.80, talks over Buddy 0.10, taps mic to talk 0.12, curious taps 0.15. Seed 1340. Uses a tablet daily; explores.

### U07 · Yash (UKG, ~5.5 years)

1. **ID** U07 · 2. **Grade/age** UKG, 5.5 · 3. **Reading proficiency** early · 4. **Language preference** Gujarati (Gujarati speak 0.80 / read 0.50) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 reads in a whisper · 7. **Attention span** 170 s · 8. **Confidence** 0.30 · 9. **Patience** 3.8 · 10. **Learning preferences** - · 11. **Common mistakes** - · 12. **Technology familiarity** 0.55 · 13. **Interaction style** reads in a whisper · 14. **Testing objectives** Read an entire poem

Behaviour: 0.9 words/s, accuracy 0.60, echo 0.75, decodes yes, skips small words 0.20, hesitates 0.60 (1.8-4 s), self-corrects 0.10, volume 0.40, talks over Buddy 0.10, taps mic to talk 0.12, curious taps 0.06. Seed 1357. Low confidence, reads very softly.

### U08 · Pari (UKG, ~5.5 years)

1. **ID** U08 · 2. **Grade/age** UKG, 5.5 · 3. **Reading proficiency** early · 4. **Language preference** Hindi (Hindi speak 0.85 / read 0.50) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 repeats words, corrects himself · 7. **Attention span** 170 s · 8. **Confidence** 0.60 · 9. **Patience** 3.8 · 10. **Learning preferences** wants_replay · 11. **Common mistakes** repeats_words, self_corrects · 12. **Technology familiarity** 0.55 · 13. **Interaction style** repeats words, corrects himself · 14. **Testing objectives** Hear a line again when unsure

Behaviour: 0.9 words/s, accuracy 0.60, echo 0.75, decodes yes, skips small words 0.20, hesitates 0.60 (1.8-4 s), self-corrects 0.30, volume 0.80, talks over Buddy 0.10, taps mic to talk 0.12, curious taps 0.06. Seed 1374. Repeats words while thinking.

### C1-01 · Rudra (Class 1, ~6.5 years)

1. **ID** C1-01 · 2. **Grade/age** Class 1, 6.5 · 3. **Reading proficiency** early · 4. **Language preference** English (English speak 0.85 / read 0.65) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 skips small words like 'a' and 'the' · 7. **Attention span** 190 s · 8. **Confidence** 0.60 · 9. **Patience** 4 · 10. **Learning preferences** - · 11. **Common mistakes** skips_small_words · 12. **Technology familiarity** 0.65 · 13. **Interaction style** skips small words like 'a' and 'the' · 14. **Testing objectives** Read an entire poem

Behaviour: 1.3 words/s, accuracy 0.72, echo 0.85, decodes yes, skips small words 0.45, hesitates 0.45 (1.5-3.5 s), self-corrects 0.15, volume 0.85, talks over Buddy 0.12, taps mic to talk 0.08, curious taps 0.04. Seed 1391. Frequently skips small words.

### C1-02 · Ira (Class 1, ~6.5 years)

1. **ID** C1-02 · 2. **Grade/age** Class 1, 6.5 · 3. **Reading proficiency** early · 4. **Language preference** Hindi (Hindi speak 0.90 / read 0.65; English speak 0.50 / read 0.30) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 confuses ब/व, श/स · 7. **Attention span** 190 s · 8. **Confidence** 0.60 · 9. **Patience** 4 · 10. **Learning preferences** - · 11. **Common mistakes** letter_confusion · 12. **Technology familiarity** 0.65 · 13. **Interaction style** confuses ब/व, श/स · 14. **Testing objectives** Make reading mistakes and understand the corrections

Behaviour: 1.3 words/s, accuracy 0.72, echo 0.85, decodes yes, skips small words 0.25, hesitates 0.45 (1.5-3.5 s), self-corrects 0.15, volume 0.85, talks over Buddy 0.12, taps mic to talk 0.08, curious taps 0.04. Seed 1408. Confuses similar Hindi letters.

### C1-03 · Dev (Class 1, ~6.5 years)

1. **ID** C1-03 · 2. **Grade/age** Class 1, 6.5 · 3. **Reading proficiency** early · 4. **Language preference** Gujarati (Gujarati speak 0.90 / read 0.60) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 slow, word by word · 7. **Attention span** 190 s · 8. **Confidence** 0.60 · 9. **Patience** 4 · 10. **Learning preferences** - · 11. **Common mistakes** word_by_word · 12. **Technology familiarity** 0.65 · 13. **Interaction style** slow, word by word · 14. **Testing objectives** Read an entire poem

Behaviour: 0.9 words/s, accuracy 0.72, echo 0.85, decodes yes, skips small words 0.25, hesitates 0.70 (1.5-3.5 s), self-corrects 0.15, volume 0.85, talks over Buddy 0.12, taps mic to talk 0.08, curious taps 0.04. Seed 1425. Slow, careful Gujarati reader.

### C1-04 · Jiya (Class 1, ~6.5 years)

1. **ID** C1-04 · 2. **Grade/age** Class 1, 6.5 · 3. **Reading proficiency** early · 4. **Language preference** English (English speak 0.45 / read 0.55; Gujarati speak 0.90 / read 0.40) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 reads English letters but follows spoken English with difficulty · 7. **Attention span** 190 s · 8. **Confidence** 0.60 · 9. **Patience** 4 · 10. **Learning preferences** listen_first · 11. **Common mistakes** - · 12. **Technology familiarity** 0.65 · 13. **Interaction style** reads English letters but follows spoken English with difficulty · 14. **Testing objectives** Listen to the poem first, then read it

Behaviour: 1.3 words/s, accuracy 0.72, echo 0.85, decodes yes, skips small words 0.25, hesitates 0.45 (1.5-3.5 s), self-corrects 0.15, volume 0.85, talks over Buddy 0.12, taps mic to talk 0.08, curious taps 0.04. Seed 1442. Gujarati at home; English-medium school.

### C1-05 · Om (Class 1, ~6.5 years)

1. **ID** C1-05 · 2. **Grade/age** Class 1, 6.5 · 3. **Reading proficiency** early · 4. **Language preference** Hindi (Hindi speak 0.90 / read 0.70) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 confident, races ahead, talks over Buddy · 7. **Attention span** 190 s · 8. **Confidence** 0.95 · 9. **Patience** 4 · 10. **Learning preferences** - · 11. **Common mistakes** - · 12. **Technology familiarity** 0.65 · 13. **Interaction style** confident, races ahead, talks over Buddy · 14. **Testing objectives** Read an entire poem

Behaviour: 1.9 words/s, accuracy 0.72, echo 0.85, decodes yes, skips small words 0.25, hesitates 0.45 (1.5-3.5 s), self-corrects 0.15, volume 0.85, talks over Buddy 0.30, taps mic to talk 0.08, curious taps 0.04. Seed 1459. Confident Hindi reader for his age.

### C1-06 · Siya (Class 1, ~6.5 years)

1. **ID** C1-06 · 2. **Grade/age** Class 1, 6.5 · 3. **Reading proficiency** early · 4. **Language preference** Gujarati (Gujarati speak 0.90 / read 0.60) · 5. **Vocabulary** growing · 6. **Pronunciation** 0.75 tires after a couple of minutes · 7. **Attention span** 120 s · 8. **Confidence** 0.60 · 9. **Patience** 4 · 10. **Learning preferences** - · 11. **Common mistakes** - · 12. **Technology familiarity** 0.65 · 13. **Interaction style** tires after a couple of minutes · 14. **Testing objectives** Read an entire poem

Behaviour: 1.3 words/s, accuracy 0.72, echo 0.85, decodes yes, skips small words 0.25, hesitates 0.45 (1.5-3.5 s), self-corrects 0.15, volume 0.85, talks over Buddy 0.12, taps mic to talk 0.08, curious taps 0.04, says tired after 70 s. Seed 1476. Tires quickly in the evening.

### C2-01 · Kabir (Class 2, ~7.5 years)

1. **ID** C2-01 · 2. **Grade/age** Class 2, 7.5 · 3. **Reading proficiency** developing · 4. **Language preference** English (English speak 0.85 / read 0.75; Hindi speak 0.80 / read 0.50) · 5. **Vocabulary** age-typical English · 6. **Pronunciation** 0.70 rushes and blurs longer words · 7. **Attention span** 200 s · 8. **Confidence** 0.90 · 9. **Patience** 4 · 10. **Learning preferences** likes_speed, dislikes_repeating · 11. **Common mistakes** reads_too_fast, guesses_from_first_letter, drops_endings, skips_small_words · 12. **Technology familiarity** 0.85 · 13. **Interaction style** confident, reads fast, talks over Buddy, impatient with corrections · 14. **Testing objectives** Make mistakes on purpose; Do corrections make sense to a fast reader?

Behaviour: 3.2 words/s, accuracy 0.75, echo 0.90, decodes yes, skips small words 0.30, hesitates 0.10 (0.8-1.5 s), self-corrects 0.25, volume 1.00, talks over Buddy 0.35, taps mic to talk 0.05, curious taps 0.03. Seed 501. Reads quickly and guesses words from the first letter.

### C2-02 · Neel (Class 2, ~7.5 years)

1. **ID** C2-02 · 2. **Grade/age** Class 2, 7.5 · 3. **Reading proficiency** developing · 4. **Language preference** Hindi (Hindi speak 0.90 / read 0.80) · 5. **Vocabulary** age-typical · 6. **Pronunciation** 0.82 accurate but flat · 7. **Attention span** 210 s · 8. **Confidence** 0.60 · 9. **Patience** 4.2 · 10. **Learning preferences** - · 11. **Common mistakes** monotone · 12. **Technology familiarity** 0.75 · 13. **Interaction style** accurate but flat · 14. **Testing objectives** Read an entire poem

Behaviour: 1.8 words/s, accuracy 0.80, echo 0.90, decodes yes, skips small words 0.15, hesitates 0.30 (1.2-3 s), self-corrects 0.25, volume 0.90, talks over Buddy 0.12, taps mic to talk 0.05, curious taps 0.03. Seed 1493. Reads accurately without expression.

### C2-03 · Avni (Class 2, ~7.5 years)

1. **ID** C2-03 · 2. **Grade/age** Class 2, 7.5 · 3. **Reading proficiency** developing · 4. **Language preference** Gujarati (Gujarati speak 0.90 / read 0.40; English speak 0.80 / read 0.75) · 5. **Vocabulary** age-typical · 6. **Pronunciation** 0.82 speaks Gujarati well, reads it poorly · 7. **Attention span** 210 s · 8. **Confidence** 0.60 · 9. **Patience** 4.2 · 10. **Learning preferences** - · 11. **Common mistakes** matra_errors, guesses_from_first_letter · 12. **Technology familiarity** 0.75 · 13. **Interaction style** speaks Gujarati well, reads it poorly · 14. **Testing objectives** Make reading mistakes and understand the corrections

Behaviour: 1.8 words/s, accuracy 0.80, echo 0.90, decodes yes, skips small words 0.15, hesitates 0.30 (1.2-3 s), self-corrects 0.25, volume 0.90, talks over Buddy 0.12, taps mic to talk 0.05, curious taps 0.03. Seed 1510. Reads English better than Gujarati.

### C2-04 · Kian (Class 2, ~7.5 years)

1. **ID** C2-04 · 2. **Grade/age** Class 2, 7.5 · 3. **Reading proficiency** developing · 4. **Language preference** English (English speak 0.85 / read 0.70) · 5. **Vocabulary** age-typical · 6. **Pronunciation** 0.82 loses place and restarts lines · 7. **Attention span** 210 s · 8. **Confidence** 0.60 · 9. **Patience** 4.2 · 10. **Learning preferences** - · 11. **Common mistakes** loses_place, repeats_words · 12. **Technology familiarity** 0.75 · 13. **Interaction style** loses place and restarts lines · 14. **Testing objectives** Finish, then read the same text again

Behaviour: 1.8 words/s, accuracy 0.80, echo 0.90, decodes yes, skips small words 0.15, hesitates 0.30 (1.2-3 s), self-corrects 0.25, volume 0.90, talks over Buddy 0.12, taps mic to talk 0.05, curious taps 0.03. Seed 1527. Loses his place.

### C2-05 · Mahi (Class 2, ~7.5 years)

1. **ID** C2-05 · 2. **Grade/age** Class 2, 7.5 · 3. **Reading proficiency** developing · 4. **Language preference** Hindi (Hindi speak 0.90 / read 0.75) · 5. **Vocabulary** age-typical · 6. **Pronunciation** 0.82 adds words, corrects herself · 7. **Attention span** 210 s · 8. **Confidence** 0.60 · 9. **Patience** 4.2 · 10. **Learning preferences** - · 11. **Common mistakes** adds_words, self_corrects · 12. **Technology familiarity** 0.75 · 13. **Interaction style** adds words, corrects herself · 14. **Testing objectives** Make reading mistakes and understand the corrections

Behaviour: 1.8 words/s, accuracy 0.80, echo 0.90, decodes yes, skips small words 0.15, hesitates 0.30 (1.2-3 s), self-corrects 0.50, volume 0.90, talks over Buddy 0.12, taps mic to talk 0.05, curious taps 0.03. Seed 1544. Self-corrects a lot.

### C2-06 · Parth (Class 2, ~7.5 years)

1. **ID** C2-06 · 2. **Grade/age** Class 2, 7.5 · 3. **Reading proficiency** developing · 4. **Language preference** Gujarati (Gujarati speak 0.90 / read 0.70; English speak 0.80 / read 0.70) · 5. **Vocabulary** age-typical · 6. **Pronunciation** 0.82 independent; reads the screen · 7. **Attention span** 210 s · 8. **Confidence** 0.60 · 9. **Patience** 4.2 · 10. **Learning preferences** - · 11. **Common mistakes** - · 12. **Technology familiarity** 0.85 · 13. **Interaction style** independent; reads the screen · 14. **Testing objectives** Explore the library and pick something suitable, then read

Behaviour: 1.8 words/s, accuracy 0.80, echo 0.90, decodes yes, skips small words 0.15, hesitates 0.30 (1.2-3 s), self-corrects 0.25, volume 0.90, talks over Buddy 0.12, taps mic to talk 0.05, curious taps 0.03. Seed 1561. Uses the app alone.

### C3-01 · Zoya (Class 3, ~8.5 years)

1. **ID** C3-01 · 2. **Grade/age** Class 3, 8.5 · 3. **Reading proficiency** developing · 4. **Language preference** English (English speak 0.90 / read 0.85) · 5. **Vocabulary** age-typical · 6. **Pronunciation** 0.82 fluent but no expression · 7. **Attention span** 240 s · 8. **Confidence** 0.60 · 9. **Patience** 4.5 · 10. **Learning preferences** wants_rhythm_feedback · 11. **Common mistakes** monotone · 12. **Technology familiarity** 0.80 · 13. **Interaction style** fluent but no expression · 14. **Testing objectives** Read an entire poem

Behaviour: 2.1 words/s, accuracy 0.87, echo 0.93, decodes yes, skips small words 0.10, hesitates 0.25 (1-2.5 s), self-corrects 0.35, volume 0.95, talks over Buddy 0.10, taps mic to talk 0.02, curious taps 0.02. Seed 1578. Struggles with reading expression.

### C3-02 · Rohan (Class 3, ~8.5 years)

1. **ID** C3-02 · 2. **Grade/age** Class 3, 8.5 · 3. **Reading proficiency** developing · 4. **Language preference** Hindi (Hindi speak 0.95 / read 0.80) · 5. **Vocabulary** age-typical · 6. **Pronunciation** 0.82 trips on joined letters · 7. **Attention span** 240 s · 8. **Confidence** 0.60 · 9. **Patience** 4.5 · 10. **Learning preferences** - · 11. **Common mistakes** conjunct_errors · 12. **Technology familiarity** 0.80 · 13. **Interaction style** trips on joined letters · 14. **Testing objectives** Make reading mistakes and understand the corrections

Behaviour: 2.1 words/s, accuracy 0.87, echo 0.93, decodes yes, skips small words 0.10, hesitates 0.25 (1-2.5 s), self-corrects 0.35, volume 0.95, talks over Buddy 0.10, taps mic to talk 0.02, curious taps 0.02. Seed 1595. Trips on conjunct consonants.

### C3-03 · Nisha (Class 3, ~8.5 years)

1. **ID** C3-03 · 2. **Grade/age** Class 3, 8.5 · 3. **Reading proficiency** developing · 4. **Language preference** Gujarati (Gujarati speak 0.95 / read 0.85) · 5. **Vocabulary** age-typical · 6. **Pronunciation** 0.82 rushes, drops endings, talks over Buddy · 7. **Attention span** 240 s · 8. **Confidence** 0.60 · 9. **Patience** 4.5 · 10. **Learning preferences** - · 11. **Common mistakes** reads_too_fast, drops_endings · 12. **Technology familiarity** 0.80 · 13. **Interaction style** rushes, drops endings, talks over Buddy · 14. **Testing objectives** Read an entire poem

Behaviour: 3 words/s, accuracy 0.87, echo 0.93, decodes yes, skips small words 0.10, hesitates 0.25 (1-2.5 s), self-corrects 0.35, volume 0.95, talks over Buddy 0.30, taps mic to talk 0.02, curious taps 0.02. Seed 1612. Rushes through text.

### C3-04 · Aarush (Class 3, ~8.5 years)

1. **ID** C3-04 · 2. **Grade/age** Class 3, 8.5 · 3. **Reading proficiency** developing · 4. **Language preference** English (English speak 0.90 / read 0.60) · 5. **Vocabulary** age-typical · 6. **Pronunciation** 0.82 reverses letters; very persistent · 7. **Attention span** 240 s · 8. **Confidence** 0.60 · 9. **Patience** 5.5 · 10. **Learning preferences** listen_first · 11. **Common mistakes** letter_confusion, word_by_word · 12. **Technology familiarity** 0.80 · 13. **Interaction style** reverses letters; very persistent · 14. **Testing objectives** Listen to the poem first, then read it

Behaviour: 1.1 words/s, accuracy 0.70, echo 0.93, decodes yes, skips small words 0.10, hesitates 0.25 (1-2.5 s), self-corrects 0.35, volume 0.95, talks over Buddy 0.10, taps mic to talk 0.02, curious taps 0.02. Seed 1629. Reverses letters (dyslexia-like pattern).

### C3-05 · Esha (Class 3, ~8.5 years)

1. **ID** C3-05 · 2. **Grade/age** Class 3, 8.5 · 3. **Reading proficiency** developing · 4. **Language preference** Hindi (Hindi speak 0.95 / read 0.85; Gujarati speak 0.20 / read 0.05) · 5. **Vocabulary** age-typical · 6. **Pronunciation** 0.82 likes to hear model reading · 7. **Attention span** 240 s · 8. **Confidence** 0.60 · 9. **Patience** 4.5 · 10. **Learning preferences** wants_replay · 11. **Common mistakes** - · 12. **Technology familiarity** 0.80 · 13. **Interaction style** likes to hear model reading · 14. **Testing objectives** Hear a line again when unsure

Behaviour: 2.1 words/s, accuracy 0.87, echo 0.93, decodes yes, skips small words 0.10, hesitates 0.25 (1-2.5 s), self-corrects 0.35, volume 0.95, talks over Buddy 0.10, taps mic to talk 0.02, curious taps 0.02. Seed 1646. Strong Hindi reader.

### C3-06 · Veer (Class 3, ~8.5 years)

1. **ID** C3-06 · 2. **Grade/age** Class 3, 8.5 · 3. **Reading proficiency** developing · 4. **Language preference** Gujarati (Gujarati speak 0.90 / read 0.80; English speak 0.80 / read 0.75) · 5. **Vocabulary** age-typical · 6. **Pronunciation** 0.82 independent; tires after a while · 7. **Attention span** 240 s · 8. **Confidence** 0.60 · 9. **Patience** 4.5 · 10. **Learning preferences** - · 11. **Common mistakes** - · 12. **Technology familiarity** 0.80 · 13. **Interaction style** independent; tires after a while · 14. **Testing objectives** Explore the library and pick something suitable, then read

Behaviour: 2.1 words/s, accuracy 0.87, echo 0.93, decodes yes, skips small words 0.10, hesitates 0.25 (1-2.5 s), self-corrects 0.35, volume 0.95, talks over Buddy 0.10, taps mic to talk 0.02, curious taps 0.02, says tired after 110 s. Seed 1663. Explores the app without a grown-up.

### C4-01 · Meera (Class 4, ~9.5 years)

1. **ID** C4-01 · 2. **Grade/age** Class 4, 9.5 · 3. **Reading proficiency** fluent · 4. **Language preference** Hindi (Hindi speak 0.95 / read 0.90; English speak 0.80 / read 0.80; Gujarati speak 0.30 / read 0.10) · 5. **Vocabulary** rich Hindi and English · 6. **Pronunciation** 0.92 accurate; flat rhythm and intonation · 7. **Attention span** 300 s · 8. **Confidence** 0.80 · 9. **Patience** 5 · 10. **Learning preferences** wants_challenge, wants_rhythm_feedback · 11. **Common mistakes** monotone, self_corrects · 12. **Technology familiarity** 0.90 · 13. **Interaction style** independent; explores the whole app; reads at natural pace with line-end pauses · 14. **Testing objectives** Use the app independently; Explore poems for her grade; Is there feedback on rhythm and expression?

Behaviour: 2.4 words/s, accuracy 0.96, echo 0.97, decodes yes, skips small words 0.03, hesitates 0.25 (1-2.5 s), self-corrects 0.60, volume 1.00, talks over Buddy 0.05, taps mic to talk 0.00, curious taps 0.01. Seed 701. Reads Hindi fluently; wants to sound good reading poems aloud.

### C4-02 · Trisha (Class 4, ~9.5 years)

1. **ID** C4-02 · 2. **Grade/age** Class 4, 9.5 · 3. **Reading proficiency** fluent · 4. **Language preference** English (English speak 0.95 / read 0.95) · 5. **Vocabulary** rich · 6. **Pronunciation** 0.92 fluent; needs help with rhythm and intonation · 7. **Attention span** 280 s · 8. **Confidence** 0.60 · 9. **Patience** 4.8 · 10. **Learning preferences** wants_rhythm_feedback · 11. **Common mistakes** monotone · 12. **Technology familiarity** 0.85 · 13. **Interaction style** fluent; needs help with rhythm and intonation · 14. **Testing objectives** Read an entire poem

Behaviour: 2.4 words/s, accuracy 0.92, echo 0.96, decodes yes, skips small words 0.05, hesitates 0.20 (1-2.2 s), self-corrects 0.45, volume 1.00, talks over Buddy 0.08, taps mic to talk 0.00, curious taps 0.01. Seed 1680. Fluent; rhythm needs work.

### C4-03 · Manav (Class 4, ~9.5 years)

1. **ID** C4-03 · 2. **Grade/age** Class 4, 9.5 · 3. **Reading proficiency** fluent · 4. **Language preference** Gujarati (Gujarati speak 0.95 / read 0.90) · 5. **Vocabulary** rich · 6. **Pronunciation** 0.92 careful, self-corrects · 7. **Attention span** 280 s · 8. **Confidence** 0.60 · 9. **Patience** 4.8 · 10. **Learning preferences** - · 11. **Common mistakes** self_corrects · 12. **Technology familiarity** 0.85 · 13. **Interaction style** careful, self-corrects · 14. **Testing objectives** Make reading mistakes and understand the corrections

Behaviour: 2.4 words/s, accuracy 0.92, echo 0.96, decodes yes, skips small words 0.05, hesitates 0.20 (1-2.2 s), self-corrects 0.70, volume 1.00, talks over Buddy 0.08, taps mic to talk 0.00, curious taps 0.01. Seed 1697. Careful Gujarati reader.

### C4-04 · Khushi (Class 4, ~9.5 years)

1. **ID** C4-04 · 2. **Grade/age** Class 4, 9.5 · 3. **Reading proficiency** fluent · 4. **Language preference** English (English speak 0.95 / read 0.95; Hindi speak 0.80 / read 0.70) · 5. **Vocabulary** rich · 6. **Pronunciation** 0.92 gets bored with easy texts · 7. **Attention span** 120 s · 8. **Confidence** 0.60 · 9. **Patience** 2.5 · 10. **Learning preferences** wants_challenge · 11. **Common mistakes** - · 12. **Technology familiarity** 0.85 · 13. **Interaction style** gets bored with easy texts · 14. **Testing objectives** Explore the library and pick something suitable, then read

Behaviour: 2.4 words/s, accuracy 0.92, echo 0.96, decodes yes, skips small words 0.05, hesitates 0.20 (1-2.2 s), self-corrects 0.45, volume 1.00, talks over Buddy 0.08, taps mic to talk 0.00, curious taps 0.01. Seed 1714. Finds most texts too easy.

### C4-05 · Laksh (Class 4, ~9.5 years)

1. **ID** C4-05 · 2. **Grade/age** Class 4, 9.5 · 3. **Reading proficiency** fluent · 4. **Language preference** Hindi (Hindi speak 0.95 / read 0.90) · 5. **Vocabulary** rich · 6. **Pronunciation** 0.92  · 7. **Attention span** 280 s · 8. **Confidence** 0.60 · 9. **Patience** 4.8 · 10. **Learning preferences** - · 11. **Common mistakes** reads_too_fast, skips_small_words · 12. **Technology familiarity** 0.85 · 13. **Interaction style** - · 14. **Testing objectives** Finish, then read the same text again

Behaviour: 3 words/s, accuracy 0.92, echo 0.96, decodes yes, skips small words 0.15, hesitates 0.20 (1-2.2 s), self-corrects 0.45, volume 1.00, talks over Buddy 0.08, taps mic to talk 0.00, curious taps 0.01. Seed 1731. Very fast reader.

### C4-06 · Ritika (Class 4, ~9.5 years)

1. **ID** C4-06 · 2. **Grade/age** Class 4, 9.5 · 3. **Reading proficiency** fluent · 4. **Language preference** Gujarati (Gujarati speak 0.85 / read 0.50; English speak 0.95 / read 0.90) · 5. **Vocabulary** rich · 6. **Pronunciation** 0.92 English-medium; Gujarati reading weaker · 7. **Attention span** 280 s · 8. **Confidence** 0.60 · 9. **Patience** 4.8 · 10. **Learning preferences** - · 11. **Common mistakes** matra_errors, conjunct_errors · 12. **Technology familiarity** 0.85 · 13. **Interaction style** English-medium; Gujarati reading weaker · 14. **Testing objectives** Read an entire poem

Behaviour: 2.4 words/s, accuracy 0.92, echo 0.96, decodes yes, skips small words 0.05, hesitates 0.20 (1-2.2 s), self-corrects 0.45, volume 1.00, talks over Buddy 0.08, taps mic to talk 0.00, curious taps 0.01. Seed 1748. Reads English better than Gujarati.

