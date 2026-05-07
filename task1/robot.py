import numpy as np
from world import World


class Robot:
    """
    Differential-drive robot on a torus world.

    State: position (x, y), heading (radians), speed scalar.
    update(vl, vr) advances the robot by one time step.
    """

    def __init__(self, x: float, y: float, heading: float,
                 world: World,
                 max_speed: float = 3.0,
                 max_turn: float = np.pi / 8,
                 turn_gain: float = 0.5):
        self.x = x
        self.y = y
        self.heading = heading
        self.world = world

        self.max_speed = max_speed   # max distance per step
        self.max_turn = max_turn     # max heading change per step (radians)
        self.turn_gain = turn_gain   # c in Δφ = c*(vr - vl)

    def update(self, vl: float, vr: float) -> None:
        # Heading change — clamp to max turn angle
        delta_phi = self.turn_gain * (vr - vl)
        delta_phi = np.clip(delta_phi, -self.max_turn, self.max_turn)
        self.heading = (self.heading + delta_phi) % (2 * np.pi)

        # Forward distance — use mean wheel speed, clamp to max_speed
        speed = np.clip((vl + vr) / 2.0, 0.0, self.max_speed)

        dx = speed * np.cos(self.heading)
        dy = speed * np.sin(self.heading)

        self.x, self.y = self.world.wrap(self.x + dx, self.y + dy)

    @property
    def position(self) -> tuple[float, float]:
        return self.x, self.y
    

    
