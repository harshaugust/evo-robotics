import numpy as np
from arena import Arena


class Robot:
    """
    Differential-drive robot in a bounded arena.
    No torus wrap — position is clamped to arena boundaries.
    """

    def __init__(self, x: float, y: float, heading: float,
                 arena: Arena,
                 max_speed: float = 2.5,
                 max_turn: float = np.pi / 6,
                 turn_gain: float = 0.6,
                 radius: float = 6.0):
        self.x = x
        self.y = y
        self.heading = heading % (2 * np.pi)
        self.arena = arena

        self.max_speed = max_speed
        self.max_turn = max_turn
        self.turn_gain = turn_gain
        self.radius = radius          # physical robot radius (for clamping)

    def update(self, vl: float, vr: float) -> None:
        delta_phi = self.turn_gain * (vr - vl)
        delta_phi = np.clip(delta_phi, -self.max_turn, self.max_turn)
        self.heading = (self.heading + delta_phi) % (2 * np.pi)

        # allow small negative speed so emergency reverse works
        speed = np.clip((vl + vr) / 2.0, -self.max_speed * 0.4, self.max_speed)
        nx = self.x + speed * np.cos(self.heading)
        ny = self.y + speed * np.sin(self.heading)

        self.x, self.y = self.arena.clamp_position(nx, ny, self.radius)

    def turn_in_place(self, delta: float) -> None:
        self.heading = (self.heading + delta) % (2 * np.pi)

    @property
    def position(self) -> tuple[float, float]:
        return self.x, self.y
