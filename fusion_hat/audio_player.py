""" Audio playback using ffplay.
Original from piper: https://github.com/OHF-Voice/piper1-gpl/blob/main/src/piper/audio_playback.py
"""

import shutil
import subprocess
from typing import Optional


class AudioPlayer:
    """Plays raw audio using ffplay."""

    def __init__(self, sample_rate: int, timeout: Optional[float] = None) -> None:
        """
        Initializes audio player.
        
        :param sample_rate: Sample rate of audio in Hz.
        :type sample_rate: int
        
        :param timeout: Timeout in seconds for ffplay subprocess.
        :type timeout: Optional[float]  
        """
        self.sample_rate = sample_rate
        self._proc: Optional[subprocess.Popen] = None
        self._timeout = timeout

    def __enter__(self):
        """Starts ffplay subprocess and returns player."""
        self._proc = subprocess.Popen(
            [
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-f",
                "s16le",
                "-ar",
                str(self.sample_rate),
                "-ac",
                "1",
                "-",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb) -> None:
        """Stops ffplay subprocess.
        
        :param exc_type: Exception type.
        :type exc_type: type
        
        :param exc_val: Exception value.
        :type exc_val: Exception
        
        :param exc_tb: Exception traceback.
        :type exc_tb: traceback
        """
        if self._proc:
            try:
                if self._proc.stdin:
                    self._proc.stdin.close()
            except Exception:
                pass
            self._proc.wait(timeout=self._timeout)

    def play(self, audio_bytes: bytes) -> None:
        """
        Plays raw audio using ffplay.
        
        :param audio_bytes: Raw audio bytes to play.
        :type audio_bytes: bytes
        """
        assert self._proc is not None
        assert self._proc.stdin is not None

        self._proc.stdin.write(audio_bytes)
        self._proc.stdin.flush()

    @staticmethod
    def is_available() -> bool:
        """
        Returns true if ffplay is available.
        
        :return: True if ffplay is available, False otherwise.
        :rtype: bool
        """
        return bool(shutil.which("ffplay"))