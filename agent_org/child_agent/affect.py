"""Objective frustration and engagement (pattern from autouser's affect.py).

Frustration grows only from events the harness observes, never from a label the agent gives
itself. A child abandons when frustration reaches the persona's patience, or when the session
outlasts their attention span. Praise and progress bring it down a little, as they do for
real children.
"""
from dataclasses import dataclass, field

WEIGHTS = {
    "interrupted_pause": 1.0,     # Buddy talked while the child was pausing to think
    "false_correction": 1.2,      # told to practise a word they read right
    "unheard_speech": 0.8,        # spoke while the mic was muted; Buddy ignored it
    "dead_click": 0.5,            # tapped something and nothing happened
    "drill_repeat": 0.7,          # asked to say the same word yet again (3rd time and on)
    "not_understood": 0.6,        # could not understand what Buddy or the screen asked
    "long_wait": 0.4,             # Buddy talked for a long stretch
    "stuck": 0.6,                 # could not read and no help came
    "unexpected_pause": 0.8,      # the session paused when the child did not mean it to
    "wrong_screen": 0.6,          # ended up somewhere they did not mean to go
    "praise": -0.4,
    "progress": -0.15,
}


@dataclass
class Affect:
    patience: float
    frustration: float = 0.0
    peak: float = 0.0
    events: list = field(default_factory=list)

    def add(self, kind: str, t: float, **info) -> None:
        w = WEIGHTS[kind]
        self.frustration = max(0.0, self.frustration + w)
        self.peak = max(self.peak, self.frustration)
        self.events.append({"t": round(t, 2), "kind": kind, "frustration": round(self.frustration, 2), **info})

    @property
    def gave_up(self) -> bool:
        return self.frustration >= self.patience
