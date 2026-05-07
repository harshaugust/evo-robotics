import numpy as np
from world import World


class LightSource:
    """
    Cone-shaped (linear falloff) light source on a torus world.
    intensity(d) = max(0, I_max - k * d)
    """

    def __init__(self, x: float, y: float, world: World,
                 I_max: float = 1.0, k: float = 0.008):
        self.x = x
        self.y = y
        self.world = world
        self.I_max = I_max
        self.k = k

    def intensity_at(self, x: float, y: float) -> float:
        d = self.world.torus_distance(self.x, self.y, x, y)
        return max(0.0, self.I_max - self.k * d)

    def intensity_field(self, resolution: int = 200) -> np.ndarray:
        """Return a 2-D array of light intensities for plotting."""
        xs = np.linspace(0, self.world.width, resolution)
        ys = np.linspace(0, self.world.height, resolution)
        field = np.zeros((resolution, resolution))
        for i, y in enumerate(ys):
            for j, x in enumerate(xs):
                field[i, j] = self.intensity_at(x, y)
        return field
