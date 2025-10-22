import logging

class Base:
    """ Base class for Fusion Hat """
    def __init__(self, log: logging.Logger = logging.getLogger(__name__)):
        """ Initialize Fusion Hat

        Args:
            log (logging.Logger): Logger, default is None
        """
        self.log = log
