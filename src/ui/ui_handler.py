import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button

from src.audio.audio_handler import AudioHandler
from src.models.speaker import Speaker


class UIHandler:
    def __init__(self):
        self.fig = plt.figure(figsize=(14, 8))
        self._setup_plots()
        self._setup_controls()

        self.speaker = Speaker()
        self.audio_handler = AudioHandler()
        self.is_playing = False

        self._add_speaker_components()
        self._setup_animation()

    def _setup_plots(self):
        self.ax_dynamic = self.fig.add_subplot(2, 2, 1)
        self.ax_dynamic.set_xlim(-0.15, 0.15)
        self.ax_dynamic.set_ylim(-0.02, 0.25)
        self.ax_dynamic.set_aspect('equal')
        self.ax_dynamic.axis('off')
        plt.subplots_adjust(bottom=0.3)

        self.ax_wave = self.fig.add_subplot(2, 2, 3)
        self.wave_plot, = self.ax_wave.plot([], [], 'b-', lw=1.5)
        self.ax_wave.set_xlim(0, 0.02)
        self.ax_wave.set_ylim(-1.2, 1.2)
        self.ax_wave.set_xlabel('Время (с)')
        self.ax_wave.set_ylabel('Амплитуда')
        self.ax_wave.grid(True)
        self.ax_wave.set_title('Форма звуковой волны')

        self.ax_field = self.fig.add_subplot(1, 2, 2)
        self.field_plot, = self.ax_field.plot([], [], 'r-', lw=2)
        self.ax_field.set_xlim(-0.1, 0.1)
        self.ax_field.set_ylim(-2, 2)
        self.ax_field.set_ylabel('Значение (Тл)')
        self.ax_field.grid(True)
        self.ax_field.set_title('Магнитное поле в динамике')
        self.ax_field.axhline(0, color='k', linestyle='--', alpha=0.5)

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

        self.ax_toggle = plt.axes([0.8, 0.05, 0.1, 0.04])
        self.toggle_button = Button(self.ax_toggle, 'Воспроизвести', color='lightgreen')

        self.freq_slider.on_changed(self._update_freq)
        self.voltage_slider.on_changed(self._update_voltage)
        self.toggle_button.on_clicked(self._toggle_button_click)

    def _add_speaker_components(self):
        self.ax_dynamic.add_patch(self.speaker.magnet)
        self.ax_dynamic.add_patch(self.speaker.frame_top)
        self.ax_dynamic.add_patch(self.speaker.frame_bottom)
        self.ax_dynamic.add_patch(self.speaker.suspension)
        self.ax_dynamic.add_patch(self.speaker.coil)
        self.ax_dynamic.add_patch(self.speaker.diaphragm)

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
        speed_factor = max(1.0, self.freq_slider.val) # / 100), [Раскомментировать для коэффициента k]

        coil, diaphragm, field_data = self.speaker.update_position(
            amplitude,
            self.freq_slider.val * speed_factor / 50,
            t,
            self.voltage_slider.val
        )

        wave_time = np.linspace(0, 0.02, 500)
        wave_amp = (self.voltage_slider.val / 5.0) * np.sin(
            2 * np.pi * self.freq_slider.val * (wave_time - 0.1 * t))

        self.wave_plot.set_data(wave_time, wave_amp)
        self.field_plot.set_data(field_data[0], field_data[1])

        return coil, diaphragm, self.wave_plot, self.field_plot

    def _update_freq(self, _: float) -> None:
        self.audio_handler.update_frequency(self.freq_slider.val)

    def _update_voltage(self, _: float) -> None:
        self.audio_handler.update_voltage(self.voltage_slider.val)

    def _toggle_button_click(self, _) -> None:
        if self.is_playing:
            self.audio_handler.stop()
            self.toggle_button.label.set_text('Воспроизвести')
            self.toggle_button.color = 'lightgreen'
        else:
            self.audio_handler.play()
            self.toggle_button.label.set_text('Стоп')
            self.toggle_button.color = 'lightcoral'
        self.is_playing = not self.is_playing
        self.fig.canvas.draw_idle()

    def show(self):
        plt.show()
