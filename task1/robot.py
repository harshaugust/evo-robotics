import numpy as np
from world import World


class Robot:
    def __init__(self, x: float, y: float, heading: float,
                 world: World,
                 max_speed: float = 3.0,
                 max_turn: float = np.pi / 8,
                 turn_gain: float = 0.5):
        self.x = x
        self.y = y
        self.heading = heading
        self.world = world

        self.max_speed = max_speed
        self.max_turn = max_turn
        self.turn_gain = turn_gain

    def update(self, vl: float, vr: float) -> None:
        delta_phi = self.turn_gain * (vr - vl)
        delta_phi = np.clip(delta_phi, -self.max_turn, self.max_turn)
        self.heading = (self.heading + delta_phi) % (2 * np.pi)

        speed = np.clip((vl + vr) / 2.0, 0.0, self.max_speed)

        dx = speed * np.cos(self.heading)
        dy = speed * np.sin(self.heading)

        self.x, self.y = self.world.wrap(self.x + dx, self.y + dy)

    @property
    def position(self) -> tuple[float, float]:
        return self.x, self.y
