import logging
from logging.handlers import RotatingFileHandler

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

class ColoredFormatter(logging.Formatter):
    COLOR_CODES = {
        'DEBUG': '\033[94m',    # 蓝色
        'INFO': '\033[92m',     # 绿色
        'WARNING': '\033[93m',  # 黄色
        'ERROR': '\033[91m',    # 红色
        'CRITICAL': '\033[95m'  # 紫色
    }
    RESET_CODE = '\033[0m'     # 重置颜色

    def format(self, record):
        levelname = record.levelname
        color_code = self.COLOR_CODES.get(levelname, '')
        reset_code = self.RESET_CODE if color_code else ''
        # 添加颜色代码并保留原始格式
        record.levelname = f'{color_code}{levelname}{reset_code}'
        return super().format(record)

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

        # Create a handler, used for output to the console
        console_formatter = ColoredFormatter('[%(levelname)s] %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        self.addHandler(console_handler)

        if file is not None:
            # Create a handler, used for output to a file
            file_formatter = logging.Formatter('%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', datefmt='%y/%m/%d %H:%M:%S')
            file_handler = RotatingFileHandler(self.log_path, maxBytes=maxBytes, backupCount=backupCount)
            file_handler.setLevel(level)
            file_handler.setFormatter(file_formatter)
            self.addHandler(file_handler)

    def setLevel(self, level: [int, str]):
        """ Set log level

        Args:
            level (int or str): Log level
        """
        if isinstance(level, str):
            level = level.upper()
        super().setLevel(level)
        for handler in self.handlers:
            handler.setLevel(level)
