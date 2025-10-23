from ..pwm import PWM
from ..pin import Pin
from typing import Union, List, Tuple, Optional
import time


class Buzzer():
    """Buzzer"""

    NOTE = {
        'C0': 16.35, 'C#0': 17.32, 'D0': 18.35, 'Eb0': 19.45, 'E0': 20.60, 'F0': 21.83, 'F#0': 23.12, 'G0': 24.50, 'G#0': 25.96, 'A0': 27.50, 'Bb0': 29.14, 'B0': 30.87,
        'C1': 32.70, 'C#1': 34.65, 'D1': 36.71, 'Eb1': 38.89, 'E1': 41.20, 'F1': 43.65, 'F#1': 46.25, 'G1': 49.00, 'G#1': 51.91, 'A1': 55.00, 'Bb1': 58.27, 'B1': 61.74,
        'C2': 65.41, 'C#2': 69.30, 'D2': 73.42, 'Eb2': 77.78, 'E2': 82.41, 'F2': 87.31, 'F#2': 92.50, 'G2': 98.00, 'G#2': 103.83, 'A2': 110.00, 'Bb2': 116.54, 'B2': 123.47,
        'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'Eb3': 155.56, 'E3': 164.81, 'F3': 174.61, 'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00, 'Bb3': 233.08, 'B3': 246.94,
        'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'Eb4': 311.13, 'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00, 'Bb4': 466.16, 'B4': 493.88,
        'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'Eb5': 622.25, 'E5': 659.26, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61, 'A5': 880.00, 'Bb5': 932.33, 'B5': 987.77,
        'C6': 1046.50, 'C#6': 1108.73, 'D6': 1174.66, 'Eb6': 1244.51, 'E6': 1318.51, 'F6': 1396.91, 'F#6': 1479.98, 'G6': 1567.98, 'G#6': 1661.22, 'A6': 1760.00, 'Bb6': 1864.66, 'B6': 1975.53,
        'C7': 2093.00, 'C#7': 2217.46, 'D7': 2349.32, 'Eb7': 2489.02, 'E7': 2637.02, 'F7': 2793.83, 'F#7': 2959.96, 'G7': 3135.96, 'G#7': 3322.44, 'A7': 3520.00, 'Bb7': 3729.31, 'B7': 3951.07,
        'C8': 4186.01, 'C#8': 4434.92, 'D8': 4698.64, 'Eb8': 4978.03, 'E8': 5274.04, 'F8': 5587.65, 'F#8': 5919.91, 'G8': 6271.93, 'G#8': 6644.88, 'A8': 7040.00, 'Bb8': 7458.62, 'B8': 7902.13
    }


    def __init__(self, buzzer: Union[PWM, Pin]):
        """
        Initialize buzzer

        :param pwm: PWM object for passive buzzer or Pin object for active buzzer
        :type pwm: fusion_hat.PWM/fusion_hat.Pin
        """
        # print(f'buzzer type: {type(buzzer)}')
        if not isinstance(buzzer, (PWM, Pin)):
            raise TypeError(
                "buzzer must be fusion_hat.PWM or fusion_hat.Pin object")
        self.buzzer = buzzer
        self.off()

    def on(self):
        """Turn on buzzer"""
        if isinstance(self.buzzer, PWM):
            self.buzzer.pulse_width_percent(50)
        elif isinstance(self.buzzer, Pin):
            self.buzzer.on()

    def off(self):
        """Turn off buzzer"""
        if isinstance(self.buzzer, PWM):
            self.buzzer.pulse_width_percent(0)
        elif isinstance(self.buzzer, Pin):
            self.buzzer.off()

    def freq(self, freq: float):
        """Set frequency of passive buzzer

        :param freq: frequency of buzzer, use Music.NOTES to get frequency of note
        :type freq: int/float
        :raise TypeError: if set to active buzzer
        """
        if isinstance(self.buzzer, Pin):
            raise TypeError("freq is not supported for active buzzer")
        self.buzzer.freq(freq)

    def play(self, freq: float, duration: float = None):
        """
        Play freq

        :param freq: freq to play, you can use Music.note() to get frequency of note
        :type freq: float
        :param duration: duration of each note, in seconds, None means play continuously
        :type duration: float
        :raise TypeError: if set to active buzzer
        """
        if isinstance(self.buzzer, Pin):
            raise TypeError("play is not supported for active buzzer")
        if isinstance(freq, str):
            freq = self.NOTE[freq]
        self.freq(freq)
        self.on()
        if duration is not None:
            time.sleep(duration/2)
            self.off()
            time.sleep(duration/2)
