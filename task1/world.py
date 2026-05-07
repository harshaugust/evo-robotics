import numpy as np


class World:
    """Toroidal 2D world — positions wrap Pac-Man style."""

    def __init__(self, width: float = 200.0, height: float = 200.0):
        self.width = width
        self.height = height

    def wrap(self, x: float, y: float) -> tuple[float, float]:
        return x % self.width, y % self.height

    def torus_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Shortest distance between two points on the torus."""
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        dx = min(dx, self.width - dx)
        dy = min(dy, self.height - dy)
        return np.sqrt(dx ** 2 + dy ** 2)
