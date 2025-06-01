from dataclasses import dataclass
from typing import Tuple

import numpy as np
from matplotlib.patches import Circle, Rectangle, Polygon


@dataclass
class SpeakerDimensions:
    coil_radius: float = 0.02
    coil_height: float = 0.03
    diaphragm_radius: float = 0.1
    magnet_width: float = 0.1
    magnet_height: float = 0.03
    frame_width: float = 0.24
    frame_height: float = 0.01

    b_init: float = 1.0
    alpha: float = 100
    beta: float = 100
    N: int = 50
    w: float = 0.005
    R: float = 8.0
    L: float = 0.001
    mu0: float = 4 * np.pi * 1e-7


class Speaker:
    def __init__(self, dimensions: SpeakerDimensions = SpeakerDimensions()):
        self.dimensions = dimensions
        self._create_components()
        self._create_magnetic_field()

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

    def _create_magnetic_field(self):
        self.field_x = np.linspace(-0.1, 0.1, 100)
        self.B_perm = self.dimensions.b_init * np.exp(-self.dimensions.alpha * self.field_x ** 2)

    def _calculate_coil_field(self, voltage: float, frequency: float, coil_position: float) -> np.ndarray:
        omega = 2 * np.pi * frequency
        Z = self.dimensions.R + 1j * omega * self.dimensions.L
        
        I = (voltage / abs(Z)) * (voltage / 5.0)
        
        B_coil = (self.dimensions.mu0 * self.dimensions.N * I /
                 (2 * self.dimensions.w)) * np.exp(-self.dimensions.beta * (self.field_x - coil_position) ** 2)
        
        return B_coil

    def get_field_data(self, coil_position: float, voltage: float, frequency: float) -> Tuple[np.ndarray, np.ndarray]:
        direction = -1 if coil_position > self.dimensions.coil_height / 2 else 1
        b_const = self.B_perm * direction
        
        b_changing = self._calculate_coil_field(voltage, frequency, coil_position)
        
        b_total = b_const + b_changing * (voltage / 5.0)
        
        return self.field_x, b_total

    def update_position(self, amplitude: float, frequency: float, time: float, voltage: float = 5.0) -> Tuple[Circle, Polygon, Tuple[np.ndarray, np.ndarray]]:
        y_coil = self.dimensions.coil_height / 2 + amplitude * np.sin(2 * np.pi * frequency * time)
        self.coil.center = (0, y_coil)

        self.diaphragm.set_xy([
            [-self.dimensions.diaphragm_radius, y_coil],
            [0, 0.15 + amplitude * np.sin(2 * np.pi * frequency * time)],
            [self.dimensions.diaphragm_radius, y_coil]
        ])

        field_data = self.get_field_data(y_coil, voltage, frequency)
        return self.coil, self.diaphragm, field_data
