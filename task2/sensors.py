import numpy as np
from arena import Arena
from robot import Robot


class ProximitySensor:

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
        angle = robot.heading + self.angle_offset
        d = arena.ray_cast(robot.x, robot.y, angle, self.range_r)
        ex = robot.x + d * np.cos(angle)
        ey = robot.y + d * np.sin(angle)
        return ex, ey
