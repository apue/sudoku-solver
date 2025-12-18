"""Tracer placeholder used by the backtracking solver in future versions."""

class Tracer:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.steps = []

