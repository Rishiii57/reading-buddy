"""Align a batch of transcript tokens against the expected text.

A small semi-global dynamic-programming alignment (edit distance with affine
gaps for skipped words). The alignment may start at the reader's pointer, or a
few words earlier (the child repeating or restarting), and may end anywhere.

Operations returned, in reading order:
  ("match", tok_idxs, word_idxs, sim)   word(s) read correctly (or close enough)
  ("sub",   tok_idx,  word_idx,  sim)   a different word was read
  ("del",   word_idx)                   expected word skipped
  ("ins",   tok_idx)                    extra word (filler, self-correction, noise)
"""
from dataclasses import dataclass, field

from .content import Word
from .normalize import similarity

INF = float("inf")


@dataclass
class AlignConfig:
    match_thr: float = 0.6      # similarity at or above this counts as the word
    short_match_thr: float = 0.7  # stricter for words of 4 letters or fewer ("bed" is not "red")
    short_len: int = 4
    good_sim: float = 0.85      # at or above this costs nothing
    sub_cost: float = 1.1
    near_sim: float = 0.5       # a near-miss ("उसके" for "उसने") still lines up with its word...
    near_cost: float = 0.7      # ...more cheaply than an unrelated word, but it is not a match
    ins_cost: float = 0.8
    gap_open: float = 1.4
    gap_ext: float = 0.25
    back_cost: float = 0.3      # starting earlier than the pointer (re-reading)
    free_del: float = 0.35      # skipping a word the tutor just said (cheap, but a misread still wins)
    back_window: int = 12
    ahead_min: int = 12


@dataclass
class Alignment:
    start: int
    ops: list = field(default_factory=list)
    cost: float = 0.0


def _threshold(word: Word, cfg: AlignConfig) -> float:
    return cfg.short_match_thr if len(word.loose) <= cfg.short_len else cfg.match_thr


def _match_cost(sim: float, thr: float, cfg: AlignConfig) -> float:
    if sim >= cfg.good_sim:
        return 0.0
    if sim >= thr:
        return (1.0 - sim) * 0.8
    if sim >= cfg.near_sim:
        return cfg.near_cost
    return cfg.sub_cost


def align(tokens: list[str], words: list[Word], p: int, cfg: AlignConfig,
          free: frozenset[int] = frozenset()) -> Alignment:
    n, N = len(tokens), len(words)
    s = max(0, p - cfg.back_window)
    e = min(N, p + max(cfg.ahead_min, 2 * n + 6))
    if n == 0 or s >= e:
        return Alignment(start=p)
    W = words[s:e]
    cols = len(W)
    p0 = p - s  # column index of the pointer

    def del_open(j):  # cost to start skipping word W[j]
        w = W[j]
        if w.idx in free:
            return cfg.free_del
        if j > 0 and W[j - 1].norm == w.norm:  # repeated word ("ठंडी ठंडी")
            return cfg.gap_ext
        return cfg.gap_open

    def del_ext(j):  # a run of words the tutor just said costs free_del once, not per word
        return 0.0 if W[j].idx in free else cfg.gap_ext

    # score tables and back-pointers: state 0=M 1=D 2=I
    S = [[[INF] * (cols + 1) for _ in range(n + 1)] for _ in range(3)]
    B = [[[None] * (cols + 1) for _ in range(n + 1)] for _ in range(3)]
    for j in range(0, min(p0, cols) + 1):
        S[0][0][j] = 0.0 if j == p0 else cfg.back_cost
        B[0][0][j] = ("start",)

    sim_cache = {}

    def sim(ti, wj):
        key = (ti, wj)
        if key not in sim_cache:
            w = W[wj]
            sim_cache[key] = 1.0 if tokens[ti] in w.aliases else similarity(tokens[ti], w.norm)
        return sim_cache[key]

    def best_prev(i, j):
        vals = [(S[k][i][j], k) for k in range(3)]
        return min(vals)

    for i in range(0, n + 1):
        for j in range(0, cols + 1):
            if i == 0 and j <= p0:
                pass  # start cells already set; D can still extend below
            # D: skip expected word W[j-1]
            if j >= 1:
                cand = [(S[0][i][j - 1] + del_open(j - 1), 0), (S[2][i][j - 1] + del_open(j - 1), 2),
                        (S[1][i][j - 1] + del_ext(j - 1), 1)]
                v, k = min(cand)
                if v < S[1][i][j]:
                    S[1][i][j], B[1][i][j] = v, ("del", k)
            if i >= 1:
                # I: extra token
                v, k = best_prev(i - 1, j)
                v += cfg.ins_cost
                if v < S[2][i][j]:
                    S[2][i][j], B[2][i][j] = v, ("ins", k)
                if j >= 1:
                    # M: one token vs one word
                    sm = sim(i - 1, j - 1)
                    v, k = best_prev(i - 1, j - 1)
                    v += _match_cost(sm, _threshold(W[j - 1], cfg), cfg)
                    if v < S[0][i][j]:
                        S[0][i][j], B[0][i][j] = v, ("m11", k, sm)
                    # one token vs two or three words written together
                    # ("sunlight" vs "sun light", Gujarati "લાલને" vs "લાલ ને")
                    for span in (2, 3):
                        if j >= span:
                            joined = "".join(W[x].norm for x in range(j - span, j))
                            sm2 = similarity(tokens[i - 1], joined)
                            if sm2 >= cfg.good_sim:
                                v, k = best_prev(i - 1, j - span)
                                if v < S[0][i][j]:
                                    S[0][i][j], B[0][i][j] = v, ("m1n", k, sm2, span)
                    # two tokens vs one word
                    if i >= 2:
                        sm3 = similarity(tokens[i - 2] + tokens[i - 1], W[j - 1].norm)
                        if sm3 >= cfg.good_sim:
                            v, k = best_prev(i - 2, j - 1)
                            if v < S[0][i][j]:
                                S[0][i][j], B[0][i][j] = v, ("m21", k, sm3)

    # end anywhere, but not on a trailing skip
    best, bk, bj = INF, 0, p0
    for j in range(cols + 1):
        for k in (0, 2):
            if S[k][n][j] < best - 1e-9:
                best, bk, bj = S[k][n][j], k, j

    ops = []
    i, j, k = n, bj, bk
    while True:
        bp = B[k][i][j]
        if bp is None or bp[0] == "start":
            break
        kind = bp[0]
        if kind == "del":
            ops.append(("del", W[j - 1].idx))
            j, k = j - 1, bp[1]
        elif kind == "ins":
            ops.append(("ins", i - 1))
            i, k = i - 1, bp[1]
        elif kind == "m11":
            sm = bp[2]
            if sm >= _threshold(W[j - 1], cfg):
                ops.append(("match", [i - 1], [W[j - 1].idx], sm))
            else:
                ops.append(("sub", i - 1, W[j - 1].idx, sm))
            i, j, k = i - 1, j - 1, bp[1]
        elif kind == "m1n":
            span = bp[3]
            ops.append(("match", [i - 1], [W[x].idx for x in range(j - span, j)], bp[2]))
            i, j, k = i - 1, j - span, bp[1]
        elif kind == "m21":
            ops.append(("match", [i - 2, i - 1], [W[j - 1].idx], bp[2]))
            i, j, k = i - 2, j - 1, bp[1]
    ops.reverse()
    return Alignment(start=s + j, ops=ops, cost=best)
