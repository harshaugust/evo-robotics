import numpy as np
from robot import Robot
from sensors import ProximitySensor
from arena import Arena


class ProximityController:
    """
    Rule-based wall avoidance + exploration controller.

    Per the task spec: sensor conditions directly change the robot's heading.
    Forward speed is set separately as a constant (differential-drive abstraction).

    Three sensors:
      front-left  (+45°)
      front       (  0°)
      front-right (-45°)

    Rules (priority order):
      1. Emergency: front very close  → rotate 90°+ toward open side, back up
      2. Front blocked               → rotate 60° toward open side, slow
      3. Front-left blocked          → rotate right 40°
      4. Front-right blocked         → rotate left 40°
      5. Mild left obstacle          → rotate right 15°
      6. Mild right obstacle         → rotate left 15°
      7. Free space                  → cruise, add random drift for exploration
    """

    EMERGENCY = 0.70
    HIGH      = 0.45
    MEDIUM    = 0.20

    CRUISE    = 1.2
    SLOW      = 0.6
    STOP      = 0.0

    DRIFT     = 0.06    # random heading drift in free space

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

        # ── Rule 1: Emergency ────────────────────────────────────────────────
        if f >= self.EMERGENCY:
            sign = 1 if fl <= fr else -1   # turn toward less-blocked side
            angle = sign * (np.pi / 2 + np.random.uniform(0, np.pi / 6))
            self.robot.turn_in_place(angle)
            # back up a tiny bit
            return -0.5, -0.5

        # ── Rule 2: Front high ───────────────────────────────────────────────
        if f >= self.HIGH:
            sign = 1 if fl <= fr else -1
            self.robot.turn_in_place(sign * np.pi / 3)
            return self.SLOW, self.SLOW

        # ── Rule 3: Front-left high ──────────────────────────────────────────
        if fl >= self.HIGH:
            self.robot.turn_in_place(-np.pi / 4)
            return self.SLOW, self.SLOW

        # ── Rule 4: Front-right high ─────────────────────────────────────────
        if fr >= self.HIGH:
            self.robot.turn_in_place(+np.pi / 4)
            return self.SLOW, self.SLOW

        # ── Rule 5: Mild left ────────────────────────────────────────────────
        if fl >= self.MEDIUM:
            self.robot.turn_in_place(-np.pi / 12)
            return self.CRUISE, self.CRUISE

        # ── Rule 6: Mild right ───────────────────────────────────────────────
        if fr >= self.MEDIUM:
            self.robot.turn_in_place(+np.pi / 12)
            return self.CRUISE, self.CRUISE

        # ── Rule 7: Free — cruise with random drift ──────────────────────────
        self.robot.turn_in_place(np.random.uniform(-self.DRIFT, self.DRIFT))
        return self.CRUISE, self.CRUISE

    def run(self, steps: int = 5000) -> list[tuple[float, float]]:
        trajectory = [self.robot.position]
        for _ in range(steps):
            vl, vr = self.step()
            self.robot.update(vl, vr)
            trajectory.append(self.robot.position)
        return trajectory
