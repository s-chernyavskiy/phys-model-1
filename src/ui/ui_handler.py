import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button

from src.audio.audio_handler import AudioHandler
from src.models.speaker import Speaker


class UIHandler:
    def __init__(self):
        self.fig = plt.figure(figsize=(12, 8))
        self._setup_plots()
        self._setup_controls()

        self.speaker = Speaker()
        self.audio_handler = AudioHandler()

        self._add_speaker_components()
        self._setup_animation()

    def _setup_plots(self):
        self.ax = self.fig.add_subplot(2, 1, 1)
        self.ax.set_xlim(-0.15, 0.15)
        self.ax.set_ylim(-0.02, 0.25)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        plt.subplots_adjust(bottom=0.3)

        self.ax_wave = self.fig.add_subplot(2, 1, 2)
        self.wave_plot, = self.ax_wave.plot([], [], 'b-', lw=1.5)
        self.ax_wave.set_xlim(0, 0.02)
        self.ax_wave.set_ylim(-1.2, 1.2)
        self.ax_wave.set_xlabel('Время (с)')
        self.ax_wave.set_ylabel('Амплитуда')
        self.ax_wave.grid(True)
        self.ax_wave.set_title('Форма звуковой волны')

    def _setup_controls(self):
        self.ax_freq = plt.axes([0.25, 0.2, 0.65, 0.03])
        self.freq_slider = Slider(
            ax=self.ax_freq,
            label='Частота (Гц)',
            valmin=50,
            valmax=2000,
            valinit=440,
            valstep=10
        )

        self.ax_voltage = plt.axes([0.25, 0.15, 0.65, 0.03])
        self.voltage_slider = Slider(
            ax=self.ax_voltage,
            label='Напряжение (В)',
            valmin=0.1,
            valmax=20.0,
            valinit=5.0,
            valstep=0.1
        )

        self.ax_play = plt.axes([0.8, 0.05, 0.1, 0.04])
        self.play_button = Button(self.ax_play, 'Воспроизвести', color='lightgreen')
        self.ax_stop = plt.axes([0.65, 0.05, 0.1, 0.04])
        self.stop_button = Button(self.ax_stop, 'Стоп', color='lightcoral')

        self.freq_slider.on_changed(self._update_freq)
        self.voltage_slider.on_changed(self._update_voltage)
        self.play_button.on_clicked(self._play_button_click)
        self.stop_button.on_clicked(self._stop_button_click)

    def _add_speaker_components(self):
        self.ax.add_patch(self.speaker.magnet)
        self.ax.add_patch(self.speaker.frame_top)
        self.ax.add_patch(self.speaker.frame_bottom)
        self.ax.add_patch(self.speaker.suspension)
        self.ax.add_patch(self.speaker.coil)
        self.ax.add_patch(self.speaker.diaphragm)

    def _setup_animation(self):
        self.ani = FuncAnimation(
            self.fig,
            self._update,
            frames=200,
            interval=50,
            blit=True
        )

    def _update(self, frame: int) -> tuple:
        t = frame / 20
        amplitude = 0.005 * (self.voltage_slider.val / 5.0)
        speed_factor = max(1.0, self.freq_slider.val / 100)

        coil, diaphragm = self.speaker.update_position(
            amplitude,
            self.freq_slider.val * speed_factor / 50,
            t
        )

        wave_time = np.linspace(0, 0.02, 500)
        wave_amp = (self.voltage_slider.val / 5.0) * np.sin(
            2 * np.pi * self.freq_slider.val * (wave_time - 0.1 * t)
        )
        self.wave_plot.set_data(wave_time, wave_amp)

        return coil, diaphragm, self.wave_plot

    def _update_freq(self, _: float) -> None:
        self.audio_handler.update_frequency(self.freq_slider.val)

    def _update_voltage(self, _: float) -> None:
        self.audio_handler.update_voltage(self.voltage_slider.val)

    def _play_button_click(self, _) -> None:
        self.audio_handler.play()

    def _stop_button_click(self, _) -> None:
        self.audio_handler.stop()

    def show(self):
        plt.show()
