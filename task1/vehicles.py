import numpy as np
from sensors import LightSensor
from robot import Robot
from light import LightSource


class BraitenbergVehicle:

    def __init__(self, robot: Robot, light: LightSource,
                 gain: float = 3.0,
                 sensor_arm: float = 10.0,
                 sensor_angle: float = np.pi / 4):
        self.robot = robot
        self.light = light
        self.gain = gain
        self.sensor_left = LightSensor(+sensor_angle, arm=sensor_arm)
        self.sensor_right = LightSensor(-sensor_angle, arm=sensor_arm)

    def read_sensors(self) -> tuple[float, float]:
        sl = self.sensor_left.read(self.robot, self.light)
        sr = self.sensor_right.read(self.robot, self.light)
        return sl, sr

    def step(self) -> tuple[float, float]:
        raise NotImplementedError

    def run(self, steps: int = 800) -> list[tuple[float, float]]:
        trajectory = [self.robot.position]
        for _ in range(steps):
            vl, vr = self.step()
            self.robot.update(vl, vr)
            trajectory.append(self.robot.position)
        return trajectory


class Fear(BraitenbergVehicle):

    def step(self) -> tuple[float, float]:
        sl, sr = self.read_sensors()
        vl = self.gain * sl
        vr = self.gain * sr
        return vl, vr


class Aggressor(BraitenbergVehicle):

    def step(self) -> tuple[float, float]:
        sl, sr = self.read_sensors()
        vl = self.gain * sr
        vr = self.gain * sl
        return vl, vr
