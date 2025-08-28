from .utils import simple_i2c_command
import time
import threading

class UserButton:
    
    USER_BTN_STATE_REG_ADDR = 0x24

    def __init__(self, interval=0.1):
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

    def set_on_click(self, callback):
        self.__on_click__ = callback
    def set_on_press(self, callback):
        self.__on_press__ = callback
    def set_on_release(self, callback):
        self.__on_release__ = callback
    def set_on_press_released(self, callback):
        self.__on_press_released__ = callback
    def set_on_long_press(self, callback, duration=2):
        self.__on_long_press__[duration] = {
            "callback": callback,
            "duration": duration,
            "called": False,
        }
    def set_on_long_press_released(self, callback, duration=2):
        self.__on_long_press_released__[duration] = {
            "callback": callback,
            "duration": duration,
            "called": False,
        }

    def get_state(self):
        result = simple_i2c_command("get", self.USER_BTN_STATE_REG_ADDR, "b")
        return result == 1
    
    def is_pressed(self):
        if self._is_task_running:
            return self.pressed
        return self.get_state()
    
    def get_pressed_for(self):
        if self.is_pressed():
            return time.time() - self.pressed_at
        return self.pressed_for

    def read_loop(self):
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

    def start(self):
        if not self._is_task_running:
            self._is_task_running = True
            self.thread = threading.Thread(target=self.read_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self._is_task_running = False
        if self.thread is not None:
            self.thread.join()

