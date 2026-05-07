import numpy as np


class Wall:
    """A line segment obstacle."""
    def __init__(self, x1, y1, x2, y2):
        self.p1 = np.array([x1, y1], dtype=float)
        self.p2 = np.array([x2, y2], dtype=float)


class Arena:
    """
    Bounded square arena with outer walls and configurable inner walls.
    Origin at bottom-left corner.
    """

    def __init__(self, size: float = 200.0):
        self.size = size
        margin = 0.0
        s = size

        # outer boundary — 4 walls
        self.walls: list[Wall] = [
            Wall(0,   0,   s,   0),    # bottom
            Wall(s,   0,   s,   s),    # right
            Wall(s,   s,   0,   s),    # top
            Wall(0,   s,   0,   0),    # left
        ]

        # inner walls — creates an interesting maze-like environment
        self._add_inner_walls()

    def _add_inner_walls(self):
        s = self.size
        inner = [
            # horizontal bar upper-left
            Wall(30,  140,  90,  140),
            # vertical bar upper-right
            Wall(140,  80,  140, 170),
            # short horizontal mid-bottom
            Wall(60,   60,  60,  110),
            # horizontal mid-right
            Wall(100,  60,  160,  60),
            # small block bottom-right
            Wall(155,  20,  155,  55),
            Wall(120,  20,  155,  20),
        ]
        self.walls.extend(inner)

    def ray_cast(self, ox: float, oy: float,
                 angle: float, max_range: float) -> float:
        """
        Cast a ray from (ox, oy) in direction `angle`.
        Returns distance to the nearest wall hit, or max_range if none.

        Uses analytic ray-segment intersection.
        """
        dx = np.cos(angle)
        dy = np.sin(angle)
        # ray: P + t*(dx,dy),  t in [0, max_range]

        nearest = max_range
        for wall in self.walls:
            t = _ray_segment(ox, oy, dx, dy, wall.p1, wall.p2)
            if t is not None and 0 < t < nearest:
                nearest = t
        return nearest

    def clamp_position(self, x: float, y: float,
                       radius: float = 6.0) -> tuple[float, float]:
        """Keep robot inside outer boundary."""
        x = np.clip(x, radius, self.size - radius)
        y = np.clip(y, radius, self.size - radius)
        return x, y


def _ray_segment(ox: float, oy: float,
                 dx: float, dy: float,
                 p1: np.ndarray, p2: np.ndarray):
    """
    Intersect ray (O + t*D) with segment (P1 + s*(P2-P1)).
    Returns t if hit (t>0, 0<=s<=1), else None.
    """
    ax, ay = p1
    bx, by = p2 - p1          # segment direction

    denom = dx * by - dy * bx  # cross(D, B-A)
    if abs(denom) < 1e-10:
        return None            # parallel

    ex, ey = ax - ox, ay - oy  # A - O
    t = (ex * by - ey * bx) / denom
    s = (ex * dy - ey * dx) / denom

    if t > 1e-6 and 0.0 <= s <= 1.0:
        return t
    return None
