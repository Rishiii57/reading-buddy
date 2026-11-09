"""Buddy, the reading teacher: a strict, patient, line-by-line state machine.

It follows the Reading Buddy teaching spec:

  SESSION_START              greet, name the poem, read the opening line, "your turn"
  CHILD_READING              follow the child word by word against the text
  STALL_PROMPT               stuck mid-line: the next 2-3 words as a phrase; still stuck: the rest
                             of the line; still silent: "Take your time. I'm here to help."
  UNCERTAIN_AUDIO            an unclear transcript: "Can you read it again?" (never a mistake)
  INDIVIDUAL_WORD_CORRECTION a finished line with confirmed wrong or skipped words: each word,
                             said alone, repeated by the child until it is recognised
  COMPLETE_LINE_DEMONSTRATION / COMPLETE_LINE_REPETITION
                             Buddy reads the whole original line, the child reads it again
  LINE_COMPLETED / STANZA_COMPLETED / LINE_SKIPPED / SESSION_COMPLETED

Mistakes are counted per line: each confirmed wrong or skipped word in a reading, and each
wrong attempt at a practice word. Silence, noise, unclear transcripts, fillers and quick
self-corrections never count. More than `max_line_mistakes` on a line: "That's okay! Leave
this line. We should move on." Skipped lines are named at the end and in the parent summary.

Matching is strict: only spelling and script variants from the speech model (nukta, anusvara,
vowel length, case, and known mishearings learned from correct readings) count as the word.

Pure and clock-injected: every method takes `now` (seconds), so the same code runs live and
in offline replay. It returns actions; the caller turns `say` actions into audio.
"""
import random
from dataclasses import dataclass, field

from .aligner import AlignConfig, align
from .content import Text
from .normalize import similarity, tokenize


def _strict_align() -> AlignConfig:
    return AlignConfig(match_thr=0.85, short_match_thr=0.9, ins_cost=1.0)


# a child asking to stop (Rule 6: respect fatigue): "stop", "I'm tired", "बस", "થાકી ગયો"
_BREAK_WORDS = {"stop", "tired", "break", "enough", "बस", "रुको", "थक", "थका", "थकी", "थक गया", "બસ", "થાક્યો", "થાકી", "થાકી ગયો", "રોકો"}


@dataclass
class TutorConfig:
    stall_mid_s: float = 3.0          # silence after speech end before helping mid-line (was 2.0: interrupted thinking pauses)
    young_stall_mid_s: float = 3.4    # the same for Grade 1 and pre-primary texts: young readers decode slowly
    echo_stall_mid_s: float = 4.5     # pre-primary rhymes: the child is recalling a line Buddy just said
    echo_lenient: bool = True         # pre-primary rhymes: slips are 'helped', not drilled (oral repetition is the goal)
    adaptive_stall: bool = True       # learn the reader's own thinking pauses (REQ-STALL-TIMING)
    stall_gap_k: float = 1.3          # mid-line limit = k x the median of this reader's resumed pauses...
    stall_mid_max_s: float = 5.0      # ...but never more than this
    stall_line_start_s: float = 4.0   # longer at a line or verse end (a normal pause)
    stall_text_start_s: float = 6.0   # before the first word
    after_tutor_s: float = 3.5        # give the child longer to start right after Buddy speaks
    drill_wait_s: float = 4.0         # silence before Buddy says the practice word again
    self_correct_s: float = 2.0       # wait this long for a self-correction at a segment end
    max_line_mistakes: int = 10       # more than this on one line: leave it and move on
    silent_reprompts: int = 2         # demonstrations on silence before "Take your time"
    prompt_words: int = 3             # a stall prompt: at most this many words, never past a comma
    uncertain_gap_s: float = 10.0     # ask "can you read it again?" at most this often
    speaking_max_s: float = 10.0      # safety expiry for a speech_start without transcript
    min_reliability: float = 0.5      # share of a segment that must match the text to count as reading
    chatter_sim: float = 0.4          # in word practice, words less like the target than this are talk
    vad_silence_ms: int = 300         # matches the x-min-silence-ms sent to Prisma
    align: AlignConfig = field(default_factory=_strict_align)


TODO, READ, HELPED, PRACTISE, SKIPPED = "todo", "read", "helped", "practise", "skipped"
_RANK = {TODO: 0, READ: 1, HELPED: 2, SKIPPED: 3, PRACTISE: 4}


class TutorEngine:
    def __init__(self, text: Text, cfg: TutorConfig | None = None, now: float = 0.0, seed: int = 0):
        self.text = text
        self.cfg = cfg or TutorConfig()
        self.words = text.words
        self.N = len(self.words)
        self.n_lines = len(text.line_words)
        self.status = [TODO] * self.N
        self.state = "SESSION_START"
        self.p = 0                      # next expected word
        self.line = 0                   # line being read
        self.mode = "read"              # "read" | "drill"
        self.repeat = False             # COMPLETE_LINE_REPETITION: Buddy just read this line
        self.line_errors: set[int] = set()
        self.free: set[int] = set()     # words Buddy just said: the child may go on past them
        self.drill: list[int] = []      # words still to practise, in order
        self.drill_heard: list[str] = []
        self.mistakes: dict[int, int] = {}
        self.line_hard_words: dict[int, set[int]] = {}
        self.completed_lines: list[int] = []
        self.skipped_lines: list[int] = []
        self.stall_level = 0
        self.silent_count = 0
        self.last_uncertain = -1e9
        self.pending: list[str] = []
        self.pending_since = 0.0
        self.pending_after_reading = False
        self.speaking = False
        self.speech_started_at = 0.0
        self.tutor_busy = False
        self.tutor_busy_since = 0.0
        self.tutor_spans: list[list] = []
        self.last_activity = now
        self.last_tutor_end = -1.0
        self.last_speech_end = now
        self.started_at = now
        self.fragment = False
        self.done = False
        self.paused = False
        self._finish_actions: list[dict] = []
        self.log: list[dict] = []
        self.rng = random.Random(seed)
        self.counts = {"prompts": 0, "corrections": 0, "attempts": 0, "practised": 0, "praise": 0, "skips": 0}
        self.echo = getattr(text, "pre_primary", False)  # pre-readers: Buddy reads every line first
        self.young = str(text.grade).split("-")[0].strip().lower() in ("1", "0", "nursery", "lkg", "ukg")
        self.pause_gaps: list[float] = []   # mid-line pauses after which the reader went on by themselves
        self._gap_open = False

    # ----- inputs -------------------------------------------------------------
    def start(self, now: float) -> list[dict]:
        """SESSION_START: greet, name the poem, demonstrate the opening line, invite the child."""
        self.last_activity = now
        start, end = self._line_range(0)
        self._set_state("TEACHER_DEMONSTRATION", now)
        return [self._say(now, "intro", [("phrase", "welcome"), ("phrase", "today"), ("title",),
                                         ("phrase", "listen_first"), ("span", start, end), ("phrase", "read_with_me")])]

    def restart_clock(self, now: float) -> None:
        self.last_activity = now

    def pause(self, now: float) -> None:
        """Paused by the child or grown-up: nothing happens until resume."""
        self.paused = True
        self.pending = []
        self._log(now, "pause")

    def resume(self, now: float) -> None:
        self.paused = False
        self.speaking = False
        self.last_activity = now
        self._log(now, "resume")

    def on_speech_start(self, now: float) -> list[dict]:
        if self._gap_open and self.mode == "read" and not self.tutor_busy:
            # the reader paused mid-line and carried on alone: remember how long they needed
            self.pause_gaps = (self.pause_gaps + [now - self.last_speech_end])[-6:]
        self._gap_open = False
        self.speaking = True
        self.speech_started_at = now
        return []

    def mid_limit(self) -> float:
        """How long to wait mid-line before helping: per level, then adapted to this reader's pauses."""
        cfg = self.cfg
        base = cfg.echo_stall_mid_s if self.echo else cfg.young_stall_mid_s if self.young else cfg.stall_mid_s
        if not cfg.adaptive_stall or len(self.pause_gaps) < 2:
            return base
        gaps = sorted(self.pause_gaps)
        med = gaps[len(gaps) // 2] if len(gaps) % 2 else (gaps[len(gaps) // 2 - 1] + gaps[len(gaps) // 2]) / 2
        return min(cfg.stall_mid_max_s, max(base, cfg.stall_gap_k * med))

    def on_transcript(self, text: str, now: float, latency_ms: float = 0.0,
                      duration_ms: float | None = None) -> list[dict]:
        self.speaking = False
        speech_end = now - latency_ms / 1000.0 - self.cfg.vad_silence_ms / 1000.0
        speech_start = speech_end - (duration_ms or 0) / 1000.0
        self.last_activity = max(self.last_activity, speech_end)
        self.last_speech_end = speech_end
        self._log(now, "transcript", text=text)
        tokens = tokenize(text)
        if self.done or self.paused or not tokens:
            return []
        self.silent_count = 0
        if self._asks_for_break(tokens):
            return self._take_break(now)
        # speech that overlapped Buddy's own voice was partly muted: never count it as a mistake
        self.fragment = any(a < speech_end and (b is None or b > speech_start) for a, b in self.tutor_spans)
        if self.mode == "drill":
            return self._drill_attempt(tokens, now)
        # a held word or two may be a misread the next words confirm; more than that was talk
        batch = (self.pending if len(self.pending) <= 2 else []) + tokens
        self.pending = []
        return self._read(batch, now)

    def on_tutor_audio_start(self, now: float) -> None:
        self.tutor_busy = True
        self.tutor_busy_since = now

    def on_tutor_audio_end(self, now: float) -> None:
        self.tutor_busy = False
        self.last_activity = max(self.last_activity, now)
        self.last_tutor_end = now
        if self.tutor_spans and self.tutor_spans[-1][1] is None:
            self.tutor_spans[-1][1] = now
        self.tutor_spans = self.tutor_spans[-4:]
        if self.state in ("TEACHER_DEMONSTRATION", "STALL_PROMPT", "COMPLETE_LINE_DEMONSTRATION",
                          "UNCERTAIN_AUDIO", "LINE_COMPLETED", "STANZA_COMPLETED", "LINE_SKIPPED"):
            self._set_state("COMPLETE_LINE_REPETITION" if self.repeat else "CHILD_READING", now)

    def tick(self, now: float) -> list[dict]:
        if self.done or self.paused or self.state == "SESSION_START":
            return []  # nothing before the session has started
        if self.tutor_busy:
            if now - self.tutor_busy_since <= 20:
                return []
            self.on_tutor_audio_end(now)  # the client never acknowledged
        if self.speaking:
            if now - self.speech_started_at <= self.cfg.speaking_max_s:
                return []
            self.speaking = False
        cfg = self.cfg
        idle = now - self.last_activity
        just_spoke = self.last_activity == self.last_tutor_end  # nothing heard since Buddy spoke

        if self.mode == "drill":
            if self.silent_count > cfg.silent_reprompts:
                return []  # we said "take your time": wait for the child
            if idle >= max(cfg.drill_wait_s, cfg.after_tutor_s if just_spoke else 0):
                return self._silence(now, word=True)
            return []

        if self.pending:
            if now - self.pending_since < cfg.self_correct_s:
                return []  # give the child time to correct themselves
            return self._resolve_pending(now)

        start, end = self._line_range(self.line)
        if self.p == 0 and self.stall_level == 0:
            limit = cfg.stall_text_start_s
        elif self.p == start and self.stall_level == 0:
            limit = cfg.stall_line_start_s
        else:
            limit = self.mid_limit()
        if just_spoke:
            limit = max(limit, cfg.after_tutor_s)
        if idle < limit:
            return []
        if self._errors_in_line():
            return self._check_line(now)  # stopped after a slip: practise what was read so far
        return self._stall(now)

    # ----- CHILD_READING / WORD_ALIGNMENT --------------------------------------
    def _read(self, batch: list[str], now: float) -> list[dict]:
        al = align(batch, self.words, self.p, self.cfg.align, frozenset(self.free))
        ops = al.ops
        last_match = max((k for k, op in enumerate(ops) if op[0] == "match"), default=-1)
        matches = [op for op in ops if op[0] == "match"]
        content = sum(1 for op in matches if any(not self.words[j].short for j in op[2]))
        sure = sum(len(op[1]) for op in matches if op[3] >= self.cfg.align.good_sim)
        if len(batch) >= 2 and (sure / len(batch) < self.cfg.min_reliability or content == 0):
            # mostly not the text: talk, noise or an unclear transcript. Never a mistake.
            self.pending = []
            self._log(now, "uncertain", text=" ".join(batch))
            return self._uncertain(now) if not self.fragment else []
        if last_match < 0 and not any(op[0] == "sub" for op in ops):
            # nothing recognisable yet: hold it in case the next words show it was a misread
            if not self.fragment:
                self.pending = batch[-3:]
                self.pending_since = self.last_speech_end
                self.pending_after_reading = False
            return []
        if al.start < self.p:
            self._log(now, "restart", frm=self.p, to=al.start)  # Situation E: follow the child
            self.p = max(al.start, self._line_range(self.line)[0])
        p_before = self.p
        actions: list[dict] = []
        # while Buddy talks the mic is muted, which can only cut off the START of a segment:
        # in such a segment, misses before the first matched word are not the child's mistakes
        muted_until = next((k for k, op in enumerate(ops) if op[0] == "match"), len(ops)) if self.fragment else 0
        for k, op in enumerate(ops[: last_match + 1] if last_match >= 0 else ops):
            kind = op[0]
            idxs = op[2] if kind == "match" else [op[2] if kind == "sub" else op[1]] if kind != "ins" else []
            for j in idxs:
                if self.words[j].line < self.line:
                    continue  # re-reading an earlier line: just follow
                if self.words[j].line > self.line:
                    actions += self._finish_line(now)
                    if self.mode == "drill" or self.done:
                        return actions  # stop here: the child goes back to practise this line
                if kind == "match":
                    self.line_errors.discard(j)
                    self._mark(j, HELPED if j in self.free else READ)
                elif kind == "del" and j in self.free:
                    self._mark(j, HELPED)  # Buddy said it; the child carried on after it
                elif k >= muted_until:
                    self.line_errors.add(j)  # a confirmed wrong or skipped word
                self.p = j + 1
        if last_match < len(ops) - 1:
            trailing = [batch[op[1]] for op in ops[last_match + 1:] if op[0] in ("ins", "sub")]
            if trailing and not self.fragment:
                self.pending = trailing[-3:]
                self.pending_since = self.last_speech_end
                self.pending_after_reading = True
        if self.p > p_before:
            start_l, end_l = self._line_range(self.line)
            self._gap_open = start_l < self.p < end_l  # stopped inside a line: a thinking pause starts
            self.stall_level = 0
            self.free = {j for j in self.free if j >= self.p}
            self.last_activity = max(self.last_activity, now)
            self._log(now, "progress", frm=p_before, to=self.p)
            actions.append({"type": "progress"})
        if self.p >= self._line_range(self.line)[1] and not self.pending:
            actions += self._finish_line(now)
        return actions

    def _resolve_pending(self, now: float) -> list[dict]:
        """A held word with no follow-up: a skip ahead, a misread then a stop, or just noise."""
        held, self.pending = self.pending, []
        if not self.pending_after_reading or len(held) > 2 or self.p >= self.N:
            return []
        good = self.cfg.align.good_sim
        end = self._line_range(self.line)[1]
        ahead = next((k for k in range(self.p + 1, min(end, self.p + 4))
                      if similarity(held[0], self.words[k].norm) >= good), None)
        if ahead is not None:  # "...the tree and together": the word before was skipped
            self.line_errors.update(j for j in range(self.p, ahead) if j not in self.free)
            self._mark(ahead, READ)
            self.p = ahead + 1
        elif max(similarity(t, self.words[self.p].norm) for t in held) >= 0.3:
            self.line_errors.add(self.p)  # a misread, then a stop
            self.p += 1
        else:
            return []
        self._log(now, "progress", to=self.p)
        if self.p >= end:
            return [{"type": "progress"}] + self._finish_line(now)
        return [{"type": "progress"}]

    def _check_line(self, now: float) -> list[dict]:
        """The child stopped partway after a slip: practise the words read wrong so far."""
        if self.echo and self.cfg.echo_lenient:
            return self._stall(now)  # a rhyme: just help with the next words, no drilling
        return self._start_correction(sorted(self._errors_in_line()), now)

    def _finish_line(self, now: float) -> list[dict]:
        errs = sorted(self._errors_in_line())
        if errs and self.echo and self.cfg.echo_lenient:
            for j in errs:  # repeated after Buddy, imperfectly: counts as 'with help', never drilled
                self._mark(j, HELPED)
            self.line_errors.clear()
            self._log(now, "echo_slips_accepted", words=errs)
            errs = []
        if errs:
            return self._start_correction(errs, now)
        L = self.line
        end = self._line_range(L)[1]
        was_repeat = self.repeat
        self.completed_lines.append(L)
        self._set_state("LINE_COMPLETED", now, line=L)
        self._next_line(now)
        if self.done:
            return [{"type": "progress"}] + self._finish_actions
        if was_repeat:
            return [{"type": "progress"}, self._praise(now, "line_done")] + self._echo_next(now)
        if self.words[end - 1].stanza_end:
            self._set_state("STANZA_COMPLETED", now)
            return [{"type": "progress"}, self._praise(now, self.rng.choice(["stanza_done", "keep_going"]))] + self._echo_next(now)
        return [{"type": "progress"}] + self._echo_next(now)

    def _echo_next(self, now: float) -> list[dict]:
        """Echo reading for pre-primary rhymes: Buddy says the next line, then the child says it."""
        if not self.echo or self.done:
            return []
        start, end = self._line_range(self.line)
        self._set_state("TEACHER_DEMONSTRATION", now, line=self.line)
        return [self._say(now, "echo_line", [("phrase", "listen"), ("span", start, end), ("phrase", "now_you_try")])]

    def _next_line(self, now: float) -> None:
        self.line_errors.clear()
        self.free.clear()
        self.repeat = False
        self.mode = "read"
        self.drill = []
        self.stall_level = 0
        self.line += 1
        if self.line >= self.n_lines:
            self.p = self.N
            self._finish_actions = self._finish(now)
            return
        self.p = self._line_range(self.line)[0]

    # ----- STALL_PROMPT and UNCERTAIN_AUDIO (never mistakes) ---------------------
    def _stall(self, now: float) -> list[dict]:
        start, end = self._line_range(self.line)
        if self.stall_level == 0:
            # the next 2-3 words as a meaningful phrase: never past a comma or the line end
            stop = self._phrase_end(self.p)
            self._prompted(self.p, stop)
            self.stall_level = 1
            self.counts["prompts"] += 1
            self._set_state("STALL_PROMPT", now, frm=self.p, to=stop, line=self.line)
            self._log(now, "prompt", level=1, line=self.line, frm=self.p, to=stop)
            return [{"type": "progress"}, self._say(now, "stall_phrase", [("phrase", "listen"), ("span", self.p, stop)])]
        if self.stall_level == 1:
            # still stuck: demonstrate the rest of the line and ask the child to say it
            self._prompted(self.p, end)
            self.stall_level = 2
            self.counts["prompts"] += 1
            self._set_state("STALL_PROMPT", now, frm=self.p, to=end, line=self.line)
            self._log(now, "prompt", level=2, line=self.line, frm=self.p, to=end)
            return [{"type": "progress"}, self._say(now, "stall_rest", [("span", self.p, end), ("phrase", "now_you_try")])]
        if self.stall_level == 2:
            self.stall_level = 3  # still silent: no pressure, just wait
            self._log(now, "take_time")
            return [self._say(now, "take_time", [("phrase", "take_time")])]
        return []

    def _uncertain(self, now: float, word: int | None = None) -> list[dict]:
        if now - self.last_uncertain < self.cfg.uncertain_gap_s:
            return []
        self.last_uncertain = now
        self._set_state("UNCERTAIN_AUDIO", now)
        if word is not None:
            return [self._say(now, "uncertain_word", [("phrase", "say_word_again"), ("span", word, word + 1)], word=word)]
        return [self._say(now, "uncertain", [("phrase", "say_again")])]

    def _silence(self, now: float, word: bool) -> list[dict]:
        """Silence is never a mistake: demonstrate again, then 'take your time', then wait."""
        self.silent_count += 1
        w = self.drill[0]
        self._log(now, "silence", word=w)
        if self.silent_count > self.cfg.silent_reprompts:
            return [self._say(now, "take_time", [("phrase", "take_time")])]
        return [self._say(now, "fix_again", [("span", w, w + 1)], word=w)]

    def _asks_for_break(self, tokens: list[str]) -> bool:
        joined = " ".join(tokens)
        line_words = {self.words[j].norm for j in range(*self._line_range(self.line))}
        return any((t in _BREAK_WORDS and t not in line_words) for t in tokens) or any(
            b in joined for b in _BREAK_WORDS if " " in b)

    def _take_break(self, now: float) -> list[dict]:
        self._log(now, "break_requested")
        self.paused = True
        self.pending = []
        return [self._say(now, "break", [("phrase", "take_break")]), {"type": "pause"}]

    # ----- INDIVIDUAL_WORD_CORRECTION ------------------------------------------
    def _start_correction(self, errs: list[int], now: float) -> list[dict]:
        L = self.line
        self.counts["corrections"] += 1
        self._log(now, "correction", line=L, words=errs)
        for j in errs:
            self._mark(j, PRACTISE)
        self.line_hard_words.setdefault(L, set()).update(errs)
        acts = self._add_mistakes(len(errs), now)
        if acts is not None:
            return acts
        self.mode = "drill"
        self.drill = list(errs)
        self.drill_heard = []
        self.silent_count = 0
        self.pending = []
        self.free.clear()
        self.p = self.drill[0]
        w = self.drill[0]
        self._set_state("INDIVIDUAL_WORD_CORRECTION", now, word=w)
        # "Let's practise this word together." then the word alone
        return [{"type": "progress"}, self._say(now, "fix_word", [("phrase", "lets_fix"), ("span", w, w + 1)], word=w)]

    def _drill_attempt(self, tokens: list[str], now: float) -> list[dict]:
        w = self.drill[0]
        target = self.words[w]
        sims = [1.0 if t in target.aliases else similarity(t, target.norm) for t in tokens]
        best = max(sims)
        thr = self.cfg.align.short_match_thr if len(target.loose) <= self.cfg.align.short_len else self.cfg.align.match_thr
        # the same close-sounding form, heard again and again, is how the speech model hears this
        # child say the word ("aunt" for "ant"), not a reading error; a different word never passes
        if len(tokens) == 1 and best >= 0.6:
            self.drill_heard.append(tokens[0])
            if self.drill_heard[-3:] == [tokens[0]] * 3:
                self._log(now, "accepted_as_heard", word=w, heard=tokens[0])
                best = thr
        if best >= thr:
            self.counts["attempts"] += 1
            self.counts["practised"] += 1
            self.drill_heard = []
            self.silent_count = 0
            self._log(now, "drill_ok", word=w)
            self.drill.pop(0)
            if self.drill:
                nxt = self.drill[0]
                self.p = nxt
                self._set_state("INDIVIDUAL_WORD_CORRECTION", now, word=nxt)
                return [{"type": "progress"},
                        self._say(now, "fix_next", [("phrase", "word_ok"), ("span", nxt, nxt + 1)], word=nxt)]
            # every word recognised: the complete original line, then the child reads it again
            start, end = self._line_range(self.line)
            self.mode = "read"
            self.repeat = True
            self.line_errors.clear()
            self.stall_level = 0
            self.p = start
            self._set_state("COMPLETE_LINE_DEMONSTRATION", now, line=self.line)
            return [{"type": "progress"},
                    self._say(now, "repeat_line", [("phrase", "word_ok"), ("span", start, end), ("phrase", "say_line")])]
        if self.fragment or (len(tokens) >= 2 and best < self.cfg.chatter_sim):
            self._log(now, "uncertain", text=" ".join(tokens))
            return self._uncertain(now, word=w) if not self.fragment else []
        self.counts["attempts"] += 1
        self._log(now, "drill_miss", word=w, heard=" ".join(tokens))
        acts = self._add_mistakes(1, now)
        if acts is not None:
            return acts
        return [self._say(now, "fix_again", [("span", w, w + 1)], word=w)]  # the word alone, again

    def _add_mistakes(self, n: int, now: float) -> list[dict] | None:
        """Count confirmed mistakes on the current line; past the limit, leave the line."""
        L = self.line
        self.mistakes[L] = self.mistakes.get(L, 0) + n
        if self.mistakes[L] > self.cfg.max_line_mistakes:
            return self._skip_line(now)
        return None

    def _skip_line(self, now: float) -> list[dict]:
        L = self.line
        start, end = self._line_range(L)
        self.counts["skips"] += 1
        self.skipped_lines.append(L)
        self._set_state("LINE_SKIPPED", now, line=L, mistakes=self.mistakes.get(L, 0))
        for j in range(start, end):
            if self.status[j] == TODO:
                self.status[j] = SKIPPED
        self._next_line(now)
        # exactly: "That's okay! Leave this line. We should move on."
        acts = [{"type": "progress"}, self._say(now, "skip_line", [("phrase", "skip_line")])]
        if self.done:
            acts += self._finish_actions
        return acts

    # ----- Buddy speaking -------------------------------------------------------
    def _praise(self, now: float, key: str) -> dict:
        self.counts["praise"] += 1
        self._log(now, "praise", phrase=key)
        return self._say(now, "praise", [("phrase", key)])

    def _finish(self, now: float) -> list[dict]:
        self.done = True
        self._set_state("SESSION_COMPLETED", now, skipped=self.skipped_lines)
        self._log(now, "finish", skipped=self.skipped_lines)
        parts = [("phrase", "finish")]
        if self.skipped_lines:
            parts.append(("phrase", "missed_lines"))
            parts += [("span", *self._line_range(L)) for L in self.skipped_lines]
        return [self._say(now, "finish", parts), {"type": "summary", "summary": self.summary(now)}]

    def _say(self, now: float, kind: str, parts: list, **extra) -> dict:
        self.tutor_busy = True
        self.tutor_busy_since = now
        self.tutor_spans.append([now, None])
        return {"type": "say", "kind": kind, "parts": parts, **extra}

    # ----- helpers --------------------------------------------------------------
    def _phrase_end(self, p: int) -> int:
        """End of a meaningful phrase from p: up to prompt_words words, stopping after a comma."""
        end = self._line_range(self.line)[1]
        stop = p
        while stop < end and stop - p < self.cfg.prompt_words:
            stop += 1
            if self.words[stop - 1].display.rstrip()[-1:] in ",;:—":
                break
        return max(stop, p + 1)

    def _prompted(self, a: int, b: int) -> None:
        for j in range(a, b):
            self.free.add(j)
            self._mark(j, HELPED)

    def _set_state(self, state: str, now: float, **data) -> None:
        self.state = state
        self._log(now, "state", state=state, **data)

    def _line_range(self, L: int) -> tuple[int, int]:
        return self.text.line_range(min(L, self.n_lines - 1))

    def _errors_in_line(self) -> set[int]:
        start, end = self._line_range(self.line)
        return {j for j in self.line_errors if start <= j < end}

    def _mark(self, j: int, st: str) -> None:
        if _RANK[st] > _RANK[self.status[j]]:
            self.status[j] = st

    def _log(self, now: float, event: str, **data) -> None:
        self.log.append({"t": round(now - self.started_at, 3), "event": event, **data})

    def snapshot(self) -> dict:
        return {"pointer": self.p, "status": self.status, "done": self.done, "paused": self.paused,
                "mode": self.mode, "state": self.state,
                "target": self.drill[0] if self.mode == "drill" and self.drill else None,
                "line": min(self.line, self.n_lines - 1), "repeat_line": self.mode == "read" and self.repeat}

    def summary(self, now: float) -> dict:
        def clean(j):
            return self.words[j].display.strip(",.!?;:।")
        practise, seen = [], set()
        for j, st in enumerate(self.status):
            if st == PRACTISE and self.words[j].norm not in seen:
                seen.add(self.words[j].norm)
                practise.append(clean(j))
        elapsed = max(1.0, now - self.started_at)
        read_alone = sum(1 for st in self.status if st == READ)
        helped = sum(1 for st in self.status if st in (HELPED, PRACTISE))
        return {
            "words_total": self.N,
            "words_read": read_alone,
            "words_helped": helped,
            "words_to_practise": practise,
            "words_practised": self.counts["practised"],
            "correction_attempts": self.counts["attempts"],
            "lines_total": self.n_lines,
            "lines_completed": len(self.completed_lines),
            "lines_skipped": [{"line": L + 1, "text": self.text.lines[L], "mistakes": self.mistakes.get(L, 0),
                               "words": [clean(j) for j in sorted(self.line_hard_words.get(L, ()))],
                               "reason": f"more than {self.cfg.max_line_mistakes} mistakes"}
                              for L in self.skipped_lines],
            "finished": self.done,
            "prompts": self.counts["prompts"],
            "corrections": self.counts["corrections"],
            "seconds": round(elapsed, 1),
            "words_per_minute": round(60 * (read_alone + helped) / elapsed, 1),
        }
