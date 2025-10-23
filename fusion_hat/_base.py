import logging
from ._logger import Logger

class _Base:
    """ Base class for Fusion Hat

    To implement for all class

    - log: Logger object for logging

    Args:
        log (logging.Logger): Logger, default is None
        log_level (int, str, optional): Log level, default is logging.INFO
    """
    def __init__(self, *args, log: logging.Logger = Logger(__name__), log_level: [int, str] = logging.INFO, **kwargs):
        self.log = log
        self.log.setLevel(log_level)
