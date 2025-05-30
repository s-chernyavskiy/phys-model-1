from dataclasses import dataclass
from typing import Tuple

import numpy as np
from matplotlib.patches import Circle, Rectangle, Polygon


@dataclass
class SpeakerDimensions:
    coil_radius: float = 0.02
    coil_height: float = 0.01
    diaphragm_radius: float = 0.1
    magnet_width: float = 0.1
    magnet_height: float = 0.03
    frame_width: float = 0.24
    frame_height: float = 0.01


class Speaker:
    def __init__(self, dimensions: SpeakerDimensions = SpeakerDimensions()):
        self.dimensions = dimensions
        self._create_components()

    def _create_components(self):
        self.magnet = Rectangle(
            (-self.dimensions.magnet_width / 2, 0),
            self.dimensions.magnet_width,
            self.dimensions.magnet_height,
            color='red',
            alpha=0.8
        )

        self.frame_top = Rectangle(
            (-self.dimensions.frame_width / 2, self.dimensions.magnet_height),
            self.dimensions.frame_width,
            self.dimensions.frame_height,
            color='gray',
            alpha=0.8
        )
        self.frame_bottom = Rectangle(
            (-self.dimensions.frame_width / 2, -self.dimensions.frame_height),
            self.dimensions.frame_width,
            self.dimensions.frame_height,
            color='gray',
            alpha=0.8
        )

        self.suspension = Polygon(
            [[-self.dimensions.magnet_width / 2, self.dimensions.magnet_height],
             [-self.dimensions.magnet_width / 2, 0.1],
             [self.dimensions.magnet_width / 2, 0.1],
             [self.dimensions.magnet_width / 2, self.dimensions.magnet_height]],
            color='beige',
            alpha=0.5
        )

        self.coil = Circle(
            (0, self.dimensions.coil_height / 2),
            self.dimensions.coil_radius,
            color='gold',
            ec='black',
            zorder=10
        )

        self.diaphragm = Polygon(
            [[-self.dimensions.diaphragm_radius, self.dimensions.coil_height / 2],
             [0, 0.15],
             [self.dimensions.diaphragm_radius, self.dimensions.coil_height / 2]],
            color='lightblue',
            alpha=0.7
        )

    def update_position(self, amplitude: float, frequency: float, time: float) -> Tuple[Circle, Polygon]:
        y_coil = self.dimensions.coil_height / 2 + amplitude * np.sin(2 * np.pi * frequency * time)
        self.coil.center = (0, y_coil)

        self.diaphragm.set_xy([
            [-self.dimensions.diaphragm_radius, y_coil],
            [0, 0.15 + 2 * amplitude * np.sin(2 * np.pi * frequency * time)],
            [self.dimensions.diaphragm_radius, y_coil]
        ])

        return self.coil, self.diaphragm
