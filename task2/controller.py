import numpy as np
from robot import Robot
from sensors import ProximitySensor
from arena import Arena


class ProximityController:

    EMERGENCY = 0.70
    HIGH      = 0.45
    MEDIUM    = 0.20

    CRUISE    = 1.2
    SLOW      = 0.6
    STOP      = 0.0

    DRIFT     = 0.06

    def __init__(self, robot: Robot, arena: Arena, range_r: float):
        self.robot = robot
        self.arena = arena
        angle = np.pi / 4
        self.sensor_fl = ProximitySensor(+angle, range_r)
        self.sensor_f  = ProximitySensor(  0.0,  range_r)
        self.sensor_fr = ProximitySensor(-angle, range_r)

    def read_sensors(self) -> tuple[float, float, float]:
        fl = self.sensor_fl.read(self.robot, self.arena)
        f  = self.sensor_f .read(self.robot, self.arena)
        fr = self.sensor_fr.read(self.robot, self.arena)
        return fl, f, fr

    def step(self) -> tuple[float, float]:
        fl, f, fr = self.read_sensors()

        if f >= self.EMERGENCY:
            sign = 1 if fl <= fr else -1
            angle = sign * (np.pi / 2 + np.random.uniform(0, np.pi / 6))
            self.robot.turn_in_place(angle)
            return -0.5, -0.5

        if f >= self.HIGH:
            sign = 1 if fl <= fr else -1
            self.robot.turn_in_place(sign * np.pi / 3)
            return self.SLOW, self.SLOW

        if fl >= self.HIGH:
            self.robot.turn_in_place(-np.pi / 4)
            return self.SLOW, self.SLOW

        if fr >= self.HIGH:
            self.robot.turn_in_place(+np.pi / 4)
            return self.SLOW, self.SLOW

        if fl >= self.MEDIUM:
            self.robot.turn_in_place(-np.pi / 12)
            return self.CRUISE, self.CRUISE

        if fr >= self.MEDIUM:
            self.robot.turn_in_place(+np.pi / 12)
            return self.CRUISE, self.CRUISE

        self.robot.turn_in_place(np.random.uniform(-self.DRIFT, self.DRIFT))
        return self.CRUISE, self.CRUISE

    def run(self, steps: int = 5000) -> list[tuple[float, float]]:
        trajectory = [self.robot.position]
        for _ in range(steps):
            vl, vr = self.step()
            self.robot.update(vl, vr)
            trajectory.append(self.robot.position)
        return trajectory
