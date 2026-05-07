import numpy as np
from robot import Robot
from light import LightSource


class LightSensor:
    """
    A point sensor mounted on a robot at angular offset `angle_offset`
    (radians) relative to the robot's heading, at distance `arm` from center.
    """

    def __init__(self, angle_offset: float, arm: float = 10.0):
        self.angle_offset = angle_offset
        self.arm = arm

    def position(self, robot: Robot) -> tuple[float, float]:
        """Absolute world position of this sensor."""
        angle = robot.heading + self.angle_offset
        sx = robot.x + self.arm * np.cos(angle)
        sy = robot.y + self.arm * np.sin(angle)
        return robot.world.wrap(sx, sy)

    def read(self, robot: Robot, light: LightSource) -> float:
        sx, sy = self.position(robot)
        return light.intensity_at(sx, sy)
