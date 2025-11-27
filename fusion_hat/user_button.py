import time
import threading
import warnings
from typing import Callable, Optional
import evdev
from evdev import InputDevice, ecodes
from .device import raise_if_fusion_hat_not_ready

class UserButton:
    """ User button class using evdev for Linux input events
    """

    def __init__(self) -> None:
        raise_if_fusion_hat_not_ready()

        self.pressed = False
        self.pressed_for = 0
        self.pressed_at = time.time()
        self._device: Optional[InputDevice] = None
        self._device_path: Optional[str] = None

        self.__on_click__ = None
        self.__on_press__ = None
        self.__on_release__ = None
        self.__on_press_released__ = None

        # 尝试自动查找按钮设备
        self._find_button_device()
        
        # 如果找到设备，设置事件监听
        if self._device_path:
            self._setup_event_listener()

    def set_on_click(self, callback: Callable[[], None]) -> None:
        """ Set the callback function when the user button is clicked

        Args:
            callback (Callable[[], None]): callback function
        """
        self.__on_click__ = callback

    def set_on_press(self, callback: Callable[[], None]) -> None:
        """ Set the callback function when the user button is pressed

        Args:
            callback (Callable[[], None]): callback function
        """
        self.__on_press__ = callback

    def set_on_release(self, callback: Callable[[], None]) -> None:
        """ Set the callback function when the user button is released

        Args:
            callback (Callable[[], None]): callback function
        """
        self.__on_release__ = callback

    def set_on_press_released(self, callback: Callable[[], None]) -> None:
        """ Set the callback function when the user button is pressed and released

        Args:
            callback (Callable[[], None]): callback function
        """
        self.__on_press_released__ = callback

    def set_on_long_press(self, callback: Callable[[], None], duration: float=2.0) -> None:
        """ [Deprecated] Set the callback function when the user button is pressed for a long time

        Args:
            callback (Callable[[], None]): callback function
        """
        pass

    def set_on_long_press_released(self, callback: Callable[[], None], duration: float=2.0) -> None:
        """ [Deprecated] Set the callback function when the user button is pressed for a long time and released

        Args:
            callback (Callable[[], None]): callback function
            duration (float, optional): long press duration(2.0~5.0)
        """
        pass
    
    def _find_button_device(self) -> None:
        """ Find the Fusion HAT USR button device """
        try:
            # 查找名称包含"Fusion HAT USR"的输入设备
            devices = [InputDevice(path) for path in evdev.list_devices()]
            for device in devices:
                if "Fusion HAT USR" in device.name:
                    self._device = device
                    self._device_path = device.path
                    break
        except Exception:
            # 如果找不到设备，后续通过get_state时会尝试再次查找
            pass

    def get_state(self) -> bool:
        """ Get the state of the user button

        Returns:
            bool: True if pressed, False if released
        """
        # 如果设备未找到，尝试再次查找
        if not self._device and not self._device_path:
            self._find_button_device()
        
        # 如果仍然没有设备，返回默认状态（未按下）
        if not self._device and not self._device_path:
            return False
        
        try:
            # 如果设备已经初始化，直接返回当前状态
            if self._is_task_running:
                return self.pressed
            
            # 否则尝试通过sysfs文件直接读取状态
            # 通常在/sys/class/input下可以找到对应的event设备
            # 这里我们尝试读取sysfs接口（如果可用）
            # 作为备选方案，我们使用轮询检查最新状态
            # 临时打开设备并读取最新事件
            if self._device_path:
                temp_device = InputDevice(self._device_path)
                # 非阻塞方式检查是否有新事件
                for event in temp_device.read_loop():
                    if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_0:
                        return event.value == 1
                    # 只读取少量事件就退出
                    break
                temp_device.close()
            
            return self.pressed
        except Exception:
            return False
    
    def is_pressed(self) -> bool:
        """
        Check if the user button is pressed

        Returns:
            bool: True if pressed, False if released
        """
        if self._is_task_running:
            return self.pressed
        return self.get_state()
    
    def get_pressed_for(self) -> float:
        """
        Get the time the user button has been pressed for

        Returns:
            float: time in seconds
        """ 
        if self.is_pressed():
            return time.time() - self.pressed_at
        return self.pressed_for

    def _setup_event_listener(self) -> None:
        """ 设置事件监听器，在独立线程中处理输入事件 """
        def event_handler():
            while True:
                try:
                    # 确保设备已打开
                    if not self._device and self._device_path:
                        self._device = InputDevice(self._device_path)
                    
                    # 读取输入事件 - 这是一个阻塞调用，直到有事件发生
                    for event in self._device.read_loop():
                        # 处理按键事件
                        if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_0:
                            pressed = event.value == 1
                            
                            if pressed:
                                if not self.pressed:
                                    self.pressed = True
                                    self.pressed_at = time.time()
                                    # 触发按下回调
                                    if self.__on_press__ is not None:
                                        try:
                                            self.__on_press__()
                                        except Exception:
                                            pass
                                    # 触发press_released回调（按下状态）
                                    if self.__on_press_released__ is not None:
                                        try:
                                            self.__on_press_released__(True)
                                        except Exception:
                                            pass
                            else:
                                if self.pressed:
                                    self.pressed = False
                                    self.pressed_for = time.time() - self.pressed_at
                                    # 触发释放回调
                                    if self.__on_release__ is not None:
                                        try:
                                            self.__on_release__()
                                        except Exception:
                                            pass
                                    # 触发press_released回调（释放状态）
                                    if self.__on_press_released__ is not None:
                                        try:
                                            self.__on_press_released__(False)
                                        except Exception:
                                            pass
                                    # 触发点击回调
                                    if self.__on_click__ is not None:
                                        try:
                                            self.__on_click__()
                                        except Exception:
                                            pass
                except Exception:
                    # 如果发生错误，关闭设备并尝试重新打开
                    if self._device:
                        try:
                            self._device.close()
                        except Exception:
                            pass
                        self._device = None
                    # 短暂等待后重试
                    time.sleep(0.1)
        
        # 在守护线程中启动事件处理器
        listener_thread = threading.Thread(target=event_handler, daemon=True)
        listener_thread.start()

    def start(self) -> None:
        """ 此方法已弃用，不再需要调用 
        
        由于使用了Linux输入事件系统，按钮事件会自动被监听和处理，无需手动启动轮询循环。
        """
        warnings.warn(
            "UserButton.start() 方法已弃用。由于使用了Linux输入事件系统，按钮事件会自动被监听和处理。",
            DeprecationWarning,
            stacklevel=2
        )

    def stop(self) -> None:
        """ 关闭按钮设备连接 """
        # 关闭设备
        if self._device:
            try:
                self._device.close()
            except Exception:
                pass
            self._device = None
