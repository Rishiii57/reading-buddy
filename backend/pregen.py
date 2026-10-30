"""Pre-generate cached tutor audio: every phrase in every language, and every line of every text.

Single practice words are generated on first use and cached by the app.

    python -m backend.pregen [--words]   # --words also generates every single word, said slowly
"""
import argparse
import asyncio
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from .content import load_library  # noqa: E402
from .gnani import usage  # noqa: E402
from .main import SPAN_SPEED, WORD_SPEED, span_text, tts  # noqa: E402
from .phrases import PHRASES  # noqa: E402


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", action="store_true")
    args = ap.parse_args()
    jobs = []
    for lang, phrases in PHRASES.items():
        jobs += [(p, lang, 1.0) for p in phrases.values()]
    for t in load_library().values():
        for a, b in t.line_words:
            jobs.append((span_text(t, a, b), t.language, SPAN_SPEED))
            if args.words:
                jobs += [(span_text(t, p, p + 1), t.language, WORD_SPEED) for p in range(a, b)]
    before = usage.data["tts_calls"]
    for j in jobs:  # one at a time: the TTS API rate-limits bursts
        await tts.get(*j)
    print(f"{len(jobs)} clips ready, {usage.data['tts_calls'] - before} new TTS calls")


if __name__ == "__main__":
    asyncio.run(main())
