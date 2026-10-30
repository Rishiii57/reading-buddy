"""Learn which words Prisma mishears even when they are read correctly.

From correct synthetic readings (voice B only, so voice A stays held out for evaluation),
every close substitution ("aunt" heard for "ant", "peter" for "pitter") is a speech-model
artifact, not a reading error. The strict tutor accepts these forms for that word.

    python -m eval.build_aliases      # writes content/stt_aliases.json
"""
import json
from collections import defaultdict
from pathlib import Path

from backend.aligner import AlignConfig, align
from backend.content import CONTENT_DIR, load_library
from backend.normalize import tokenize

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "eval" / "runs" / "stt"
SOURCE_VARIANT = "clean_b"


def main():
    lib = load_library()
    cfg = AlignConfig()  # the forgiving alignment, to pair each heard token with its word
    aliases: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
    for f in sorted(RUNS.glob(f"*__{SOURCE_VARIANT}.json")):
        run = json.loads(f.read_text())
        text = lib[run["meta"]["text_id"]]
        p = 0
        for e in run["events"]:
            if e["type"] != "transcript":
                continue
            toks = tokenize(e.get("text", ""))
            if not toks:
                continue
            al = align(toks, text.words, p, cfg)
            for op in al.ops:
                if op[0] == "match":
                    p = op[2][-1] + 1
                    if op[3] < 1.0 and len(op[1]) == 1 and len(op[2]) == 1:
                        aliases[text.id][text.words[op[2][0]].norm].add(toks[op[1][0]])
                elif op[0] == "sub" and op[3] >= 0.5:
                    aliases[text.id][text.words[op[2]].norm].add(toks[op[1]])
                    p = op[2] + 1
    out = {tid: {w: sorted(v) for w, v in ws.items()} for tid, ws in sorted(aliases.items())}
    (CONTENT_DIR / "stt_aliases.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
