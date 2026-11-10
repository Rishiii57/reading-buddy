# QA workflow

QA is independent of Engineering. It measures; it does not read Engineering's notes to decide. Code having changed is never enough: an item is resolved only when QA has validated it.

## For every submitted requirement

```bash
python -m agent_org.qa.validate REQ-STALL-TIMING --cycle c01 --reps 2 --max-personas 14
```

1. **Reproduce the original issue.** Re-run the affected personas (from the PM analysis, plus any persona in the requirement's scope) on the **base** build. The base build is a separate worktree at the commit Engineering started from. Each persona runs with its own seed and with `+1000` for a second repetition.
2. **Test the new implementation.** Run exactly the same personas and seeds on the **candidate** build (the requirement's worktree).
3. **Check the acceptance criteria** from the PM requirement, computed with `agent_org/metrics.py` on before vs after.
4. **Run regressions:**
   - guard metrics on the same personas: completion not down by more than 0.1, abandonment not up by more than 0.1, false corrections not up by more than 0.25 per agent, mean peak frustration not up by more than 0.3, no harness errors;
   - the offline tutor replay on recorded Prisma transcripts, base vs candidate: tracking, errors caught and stalls prompted not lower, false corrections per 50 words not up by more than 0.05, stall prompt ≤ 4.0 s;
   - unit tests on the candidate.
5. **Compare before and after.** Every metric is reported side by side.
6. **Report.** `runs/<cycle>/qa/<REQ>/r<round>/VALIDATION.md` (+ `.json`), with links to every session's evidence.

Verdict: **validated_fixed** if every acceptance criterion passes, every guard passes, the replay checks pass and the tests pass. Otherwise **returned_to_engineering**, with the failing checks as evidence. The verdict is written to the PM backlog.

The measuring instrument (child agents and metrics) is the same code for both builds, so a difference comes from the app, not the tester.

## Whole-product regression

After validated requirements are merged, the next cycle's full 50-agent re-test runs on the merged build, and the PM compares it with the previous cycle. Any validated item whose symptom reappears is marked **regressed** and reopened. Product-level differences (usability, learning, grade, language) go into `PRODUCT_IMPROVEMENT_HISTORY.md`.

## Coverage

| Area | How |
|---|---|
| Functional and user-journey | 50 child agents in the real UI (start, listen first, read, mistakes, replay, restart, pause/resume, break) |
| Edge cases | consent without a grown-up, curious taps, talking over Buddy, mic taps, leaving mid-session |
| Speech and language | audio evaluation Part A (measured Prisma WER, latency, tutor on real transcripts) and Part B (text-level conditions per language) |
| Audio | placeholder-free checks need real audio: augmented variants (`audio_eval.augment`) streamed through Prisma when credits are approved |
| Performance | latency from recorded Prisma sessions; intro and response timing in agent metrics |
| Regression | unit tests, offline replay, guard metrics, full re-test each cycle |

## Known limits

- Simulated speech: the child's speech and recognition errors are modelled, not recorded.
- Placeholder audio for uncached Buddy lines (sound is silent, timing is realistic).
- Small samples: QA reports counts, not significance. Use `--reps 3` or more for borderline results.
