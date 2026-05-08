import numpy as np


class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.p1 = np.array([x1, y1], dtype=float)
        self.p2 = np.array([x2, y2], dtype=float)


class Arena:
    def __init__(self, size: float = 200.0):
        self.size = size
        s = size

        self.walls: list[Wall] = [
            Wall(0,   0,   s,   0),
            Wall(s,   0,   s,   s),
            Wall(s,   s,   0,   s),
            Wall(0,   s,   0,   0),
        ]

        self._add_inner_walls()

    def _add_inner_walls(self):
        s = self.size
        inner = [
            Wall(30,  140,  90,  140),
            Wall(140,  80,  140, 170),
            Wall(60,   60,  60,  110),
            Wall(100,  60,  160,  60),
            Wall(155,  20,  155,  55),
            Wall(120,  20,  155,  20),
        ]
        self.walls.extend(inner)

    def ray_cast(self, ox: float, oy: float,
                 angle: float, max_range: float) -> float:
        dx = np.cos(angle)
        dy = np.sin(angle)

        nearest = max_range
        for wall in self.walls:
            t = _ray_segment(ox, oy, dx, dy, wall.p1, wall.p2)
            if t is not None and 0 < t < nearest:
                nearest = t
        return nearest

    def clamp_position(self, x: float, y: float,
                       radius: float = 6.0) -> tuple[float, float]:
        x = np.clip(x, radius, self.size - radius)
        y = np.clip(y, radius, self.size - radius)
        return x, y


def _ray_segment(ox: float, oy: float,
                 dx: float, dy: float,
                 p1: np.ndarray, p2: np.ndarray):

    ax, ay = p1
    bx, by = p2 - p1

    denom = dx * by - dy * bx
    if abs(denom) < 1e-10:
        return None

    ex, ey = ax - ox, ay - oy
    t = (ex * by - ey * bx) / denom
    s = (ex * dy - ey * dx) / denom

    if t > 1e-6 and 0.0 <= s <= 1.0:
        return t
    return None
