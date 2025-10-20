from ..utils import is_installed, run_command, check_executable, enable_speaker
import logging

class Espeak():
    """ Espeak TTS engine """
    ESPEAK = 'espeak'

    def __init__(self, log: logging.Logger=None) -> None:
        """ Initialize espeak TTS engine """
        self.log = log or logging.getLogger(__name__)
        enable_speaker()

        if not is_installed("espeak"):
            raise Exception("TTS engine: espeak is not installed.")
        self._amp = 100
        self._speed = 175
        self._gap = 5
        self._pitch = 50
        self._lang = 'en-US'

    def say(self, words: str) -> None:
        """ Say words with espeak

        Args:
            words (str): Words to say
        """
        self.log.debug(f'espeak: [{words}]')
        if not check_executable('espeak'):
            self.log.debug('espeak is busy. Pass')

        cmd = f'espeak -a{self._amp} -s{self._speed} -g{self._gap} -p{self._pitch} "{words}" --stdout | aplay 2>/dev/null & '
        _, result = run_command(cmd)
        if len(result) != 0:
            raise (f'tts-espeak:\n\t{result}')
        self.log.debug(f'command: {cmd}')

    def set_amp(self, amp: int) -> None:
        """ Set amplitude

        Args:
            amp (int): Amplitude (0-200)
        """
        if amp not in range(0, 200):
            raise ValueError(f'Amp should be in 0 to 200, not "{amp}"')
        self._amp = amp

    def set_speed(self, speed: int) -> None:
        """ Set speed

        Args:
            speed (int): Speed (80-260)
        """
        if speed not in range(80, 260):
            raise ValueError(f'speed should be in 80 to 260, not "{speed}"')
        self._speed = speed

    def set_gap(self, gap: int) -> None:
        """ Set gap

        Args:
            gap (int): Gap (0-200)
        """
        if gap not in range(0, 200):
            raise ValueError(f'gap should be in 0 to 200, not "{gap}"')
        self._gap = gap

    def set_pitch(self, pitch: int) -> None:
        """ Set pitch

        Args:
            pitch (int): Pitch (0-99)
        """
        if pitch not in range(0, 99):
            raise ValueError(f'pitch should be in 0 to 99, not "{pitch}"')
        self._pitch = pitch

