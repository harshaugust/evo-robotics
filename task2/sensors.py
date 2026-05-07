import numpy as np
from arena import Arena
from robot import Robot


class ProximitySensor:
    """
    Infrared-style proximity sensor modelled as a ray.

    angle_offset : radians relative to robot heading
    range_r      : max detection range (≈15% of arena size)

    Returns 1 - d/r  when obstacle at distance d <= r,
            0        when nothing in range.
    """

    def __init__(self, angle_offset: float, range_r: float):
        self.angle_offset = angle_offset
        self.range_r = range_r

    def read(self, robot: Robot, arena: Arena) -> float:
        angle = robot.heading + self.angle_offset
        d = arena.ray_cast(robot.x, robot.y, angle, self.range_r)
        if d < self.range_r:
            return 1.0 - d / self.range_r
        return 0.0

    def ray_endpoint(self, robot: Robot, arena: Arena) -> tuple[float, float]:
        """Returns the world-position where the ray hits (for drawing)."""
        angle = robot.heading + self.angle_offset
        d = arena.ray_cast(robot.x, robot.y, angle, self.range_r)
        ex = robot.x + d * np.cos(angle)
        ey = robot.y + d * np.sin(angle)
        return ex, ey
