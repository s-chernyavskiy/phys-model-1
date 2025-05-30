from typing import Optional

import numpy as np
import sounddevice as sd


class AudioHandler:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.playing = False
        self.stream: Optional[sd.OutputStream] = None
        self.phase = 0.0
        self.current_freq = 440
        self.current_voltage = 5.0

    def audio_callback(self, out_data: np.ndarray, frames: int, _: None, status: sd.CallbackFlags) -> None:
        if status:
            print(status)

        t = (self.phase + np.arange(frames)) / self.sample_rate
        amplitude = self.current_voltage / 20.0
        out_data[:, 0] = amplitude * np.sin(2 * np.pi * self.current_freq * t)

        self.phase += frames
        self.phase %= self.sample_rate

    def play(self) -> None:
        if not self.playing:
            self.playing = True
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self.audio_callback
            )
            self.stream.start()

    def stop(self) -> None:
        if self.playing:
            self.playing = False
            if self.stream:
                self.stream.stop()
                self.stream.close()

    def update_frequency(self, frequency: float) -> None:
        self.current_freq = frequency

    def update_voltage(self, voltage: float) -> None:
        self.current_voltage = voltage
