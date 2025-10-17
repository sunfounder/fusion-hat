from .utils import simple_i2c_command
import time
import threading
from typing import Optional, function

class UserButton:
    """User button class"""
    USER_BTN_STATE_REG_ADDR = 0x24

    def __init__(self, interval: float=0.1) -> None:
        """
        Initialize the user button class

        :param interval: interval time(0.1~1.0), leave it None to use default interval time, defaults to 0.1
        :type interval: float
        """
        self.pressed = False
        self.pressed_for = 0
        self.pressed_at = 0
        self.interval = interval
        self._is_long_pressed = False
        self._is_task_running = False

        self.__on_click__ = None
        self.__on_press__ = None
        self.__on_release__ = None
        self.__on_press_released__ = None
        self.__on_long_press__ = {}
        self.__on_long_press_released__ = {}

        self.thread = None

    def set_on_click(self, callback: function) -> None:
        """
        Set the callback function when the user button is clicked

        :param callback: callback function
        :type callback: function
        """
        self.__on_click__ = callback

    def set_on_press(self, callback: function) -> None:
        """
        Set the callback function when the user button is pressed

        :param callback: callback function
        :type callback: function
        """
        self.__on_press__ = callback

    def set_on_release(self, callback: function) -> None:
        """
        Set the callback function when the user button is released

        :param callback: callback function
        :type callback: function
        """
        self.__on_release__ = callback

    def set_on_press_released(self, callback: function) -> None:
        """
        Set the callback function when the user button is pressed and released

        :param callback: callback function
        :type callback: function
        """
        self.__on_press_released__ = callback

    def set_on_long_press(self, callback: function, duration: float=2.0) -> None:
        """
        Set the callback function when the user button is long pressed

        :param callback: callback function
        :type callback: function

        :param duration: long press duration(2.0~5.0), leave it None to use default duration, defaults to 2.0
        :type duration: float, optional
        """
        self.__on_long_press__[duration] = {
            "callback": callback,
            "duration": duration,
            "called": False,
        }

    def set_on_long_press_released(self, callback: function, duration: float=2.0) -> None:
        """
        Set the callback function when the user button is long pressed and released

        :param callback: callback function
        :type callback: function

        :param duration: long press duration(2.0~5.0), leave it None to use default duration, defaults to 2.0
        :type duration: float, optional
        """
        self.__on_long_press_released__[duration] = {
            "callback": callback,
            "duration": duration,
            "called": False,
        }

    def get_state(self) -> bool:
        """
        Get the state of the user button

        :return: True if pressed, False if released
        :rtype: bool
        """
        result = simple_i2c_command("get", self.USER_BTN_STATE_REG_ADDR, "b")
        return result == 1
    
    def is_pressed(self) -> bool:
        """
        Check if the user button is pressed

        :return: True if pressed, False if released
        :rtype: bool
        """
        if self._is_task_running:
            return self.pressed
        return self.get_state()
    
    def get_pressed_for(self) -> float:
        """
        Get the time the user button has been pressed for

        :return: time in seconds
        :rtype: float
        """ 
        if self.is_pressed():
            return time.time() - self.pressed_at
        return self.pressed_for

    def read_loop(self) -> None:
        """
        Read the user button state in a loop
        """
        while self._is_task_running:
            pressed = self.get_state()
            if pressed:
                if self.pressed == False:
                    self.pressed = True
                    self.pressed_for = 0
                    self.pressed_at = time.time()
                    if self.__on_press__ is not None:
                        self.__on_press__()
                    if self.__on_press_released__ is not None:
                        self.__on_press_released__(True)
                else:
                    self.pressed_for = time.time() - self.pressed_at
                    if self.pressed_for >= 1:
                        self._is_long_pressed = True
                        for duration, data in self.__on_long_press__.items():
                            if self.pressed_for >= duration and not data["called"]:
                                print(f"User button long pressed for {duration}")
                                data["callback"]()
                                data["called"] = True
                                break
            else:
                if self.pressed == True:
                    self.pressed = False
                    if self.__on_release__ is not None:
                        self.__on_release__()
                    if self.__on_press_released__ is not None:
                        self.__on_press_released__(False)
                    if self._is_long_pressed:
                        self._is_long_pressed = False
                        for duration, data in self.__on_long_press_released__.items():
                            if self.pressed_for >= duration and not data["called"]:
                                data["callback"]()
                                data["called"] = True
                                break
                    else:
                        if self.__on_click__ is not None:
                            self.__on_click__()

            time.sleep(self.interval)

    def start(self) -> None:
        """
        Start the user button read loop
        """
        if not self._is_task_running:
            self._is_task_running = True
            self.thread = threading.Thread(target=self.read_loop, daemon=True)
            self.thread.start()

    def stop(self) -> None:
        """
        Stop the user button read loop
        """
        self._is_task_running = False
        if self.thread is not None:
            self.thread.join()
