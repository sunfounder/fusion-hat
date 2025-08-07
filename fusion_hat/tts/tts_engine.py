import logging
from distutils.spawn import find_executable

class TTSEngine():
    SUPPORTED_LANGUAUE = [
        'en-US',
        'en-GB',
        'de-DE',
        'es-ES',
        'fr-FR',
        'it-IT',
    ]
    def __init__(self, log=None):
        self.log = log or logging.getLogger(__name__)

    def _check_executable(self, executable):
        executable_path = find_executable(executable)
        found = executable_path is not None
        return found

    def say(self, text):
        """
        Say text.

        :param text: text to say.
        :type text: str
        """
        raise NotImplementedError

    def set(self, **kwargs):
        """
        Set parameters.
        """
        for key, value in kwargs.items():
            if hasattr(self, f'set_{key}'):
                getattr(self, f'set_{key}')(value)
            else:
                self.log.warning(f'No set_{key} method, ignore it')
        self.log.debug(f'Set parameters: {kwargs}')

