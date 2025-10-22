import logging
from logging.handlers import RotatingFileHandler

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

class Logger(logging.Logger):
    """ Logger class """
    def __init__(self, name='logger', level=logging.INFO, file:str=None, maxBytes=10*1024*1024, backupCount=10):
        """ Initialize Logger

        Args:
            name (str, optional): Logger name, default is 'logger'
            level (int, optional): Log level, default is 0
            file (str, optional): Log file path, default is None, no log file will be created
            maxBytes (int, optional): Maximum log file size, default is 10MB
            backupCount (int, optional): Maximum number of backup log files, default is 10
        """
        self.log_path = file
        super().__init__(name, level=level)
        # Define the output format of handler
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', datefmt='%y/%m/%d %H:%M:%S')

        # Create a handler, used for output to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)

        if file is not None:
            # Create a handler, used for output to a file
            file_handler = RotatingFileHandler(self.log_path, maxBytes=maxBytes, backupCount=backupCount)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)

    def setLevel(self, level):
        """ Set log level

        Args:
            level (int): Log level
        """
        super().setLevel(level)
        for handler in self.handlers:
            handler.setLevel(level)
