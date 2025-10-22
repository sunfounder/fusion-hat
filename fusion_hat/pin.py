#!/usr/bin/env python3
from RPi import GPIO
from typing import Callable
from enum import Enum

from ._base import _Base

class Mode(Enum):
    """ Pin direction """
    AUTO = None
    """Pin direction auto"""
    IN = GPIO.IN
    """Pin direction input"""
    OUT = GPIO.OUT
    """Pin direction output"""

class Pull(Enum):
    """ Pin pull up/down """
    UP = GPIO.PUD_UP
    """Pin internal pull up"""
    DOWN = GPIO.PUD_DOWN
    """Pin internal pull down"""
    NONE = GPIO.PUD_OFF
    """Pin internal pull none"""

class Active(Enum):
    """ Pin active state """
    HIGH = True
    """Pin active state high"""
    LOW = False
    """Pin active state low"""

class Trigger(Enum):
    """ Pin interrupt """
    FALLING = GPIO.FALLING
    """Pin interrupt falling"""
    RISING = GPIO.RISING
    """Pin interrupt rising"""
    BOTH = GPIO.BOTH
    """Pin interrupt both rising and falling"""

class Pin(_Base):
    """ Pin manipulation class """

    OUT = Mode.OUT
    """Pin mode output"""
    IN = Mode.IN
    """Pin mode input"""
    AUTO = Mode.AUTO
    """Pin mode auto"""

    PULL_UP = Pull.UP
    """Pin internal pull up"""
    PULL_DOWN = Pull.DOWN
    """Pin internal pull down"""
    PULL_NONE = Pull.NONE
    """Pin internal pull none"""

    IRQ_FALLING = Trigger.FALLING
    """Pin interrupt falling"""
    IRQ_RISING = Trigger.RISING
    """Pin interrupt rising"""
    IRQ_RISING_FALLING = Trigger.BOTH
    """Pin interrupt both rising and falling"""

    def __init__(self, pin: int, *args, mode: Mode = Mode.AUTO, pull: Pull = Pull.NONE, active_state: Active = Active.HIGH, bounce_time: float = None, **kwargs):
        """ Initialize a pin

        Args:
            pin (int): pin number of Raspberry Pi
            mode (Mode, optional): pin mode(IN/OUT/AUTO). Defaults to Mode.AUTO.
            pull (Pull, optional): pin pull (Pull.UP/Pull.DOWN/Pull.NONE). Defaults to Pull.NONE.
            active_state (Active, optional): active state of pin,  
                            If True, when the hardware pin state is HIGH, the software pin is HIGH. 
                            If False, the input polarity is reversed. Defaults to Active.HIGH.
            bounce_time (float, optional): bounce time of pin interrupt. Defaults to None.
        """
        super().__init__(*args, **kwargs)

        GPIO.setmode(GPIO.BCM)
        self._pin_num = pin
        self._value = 0
        self._initialized = False
        self._irq_inited = False
        self._on_activated = None
        self._on_deactivated = None
        self.setup(mode, pull, active_state, bounce_time)

    def close(self) -> None:
        """ Close the pin """
        self.log.debug("Close pin %d", self._pin_num)
        GPIO.cleanup(self._pin_num)

    def deinit(self) -> None:
        """Deinitialize the pin"""
        self.log.debug("Deinitialize pin %d", self._pin_num)
        GPIO.cleanup(self._pin_num)
        
    def setup(self, mode: Mode = Mode.AUTO, pull: Pull = Pull.NONE, active_state: Active = Active.HIGH, bounce_time: float = None) -> None:
        """ Setup the pin

        Args:
            mode (Mode, optional): pin mode(IN/OUT/AUTO). Defaults to Mode.AUTO.
            pull (Pull, optional): pin pull (Pull.UP/Pull.DOWN/Pull.NONE). Defaults to Pull.NONE.
            active_state (Active, optional): active state of pin,
                            If True, when the hardware pin state is HIGH, the software pin is HIGH. 
                            If False, the input polarity is reversed. Defaults to Active.HIGH.
            bounce_time (float, optional): bounce time of pin interrupt in seconds. Defaults to None.
        """
        self.log.debug("Setup pin %d, mode %s, pull %s, active_state %s, bounce_time %s", self._pin_num, mode, pull, active_state, bounce_time)
        self._mode = mode
        self._pull = pull
        self._active_state = active_state
        self._bounce_time = bounce_time

        if self._initialized:
            self.log.warning("Pin %d already initialized, deinitializing", self._pin_num)
            self.deinit()

        if self._mode != Mode.AUTO:
            GPIO.setup(self._pin_num, self._mode.value, pull_up_down=self._pull.value)
        self._initialized = True

    def __call__(self, value: [bool, int] = None) -> int:
        """ Set/get the pin value

        Args:
            value (bool/int, optional): pin value, leave it empty to get the value(0/1). Defaults to None.

        Returns:
            int: pin value(0/1)
        """
        return self.value(value)

    def raw(self, value: [bool, int] = None) -> int:
        """ Set/get the pin raw value

        Args:
            value (bool/int, optional): pin value, leave it empty to get the value(0/1). Defaults to None.

        Returns:
            int: pin value(0/1)

        Raises:
            ValueError: if pin mode is IN
        """
        if value == None:
            if self._mode == Mode.AUTO:
                GPIO.setup(self._pin_num, self.IN.value, pull_up_down=self._pull.value)
                result = GPIO.input(self._pin_num)
            else:
                result = self._value
            return result
        else:
            if self._mode == Mode.IN:
                raise ValueError("Input pin cannot set value")
            elif self._mode == Mode.AUTO:
                GPIO.setup(self._pin_num, self.OUT.value, pull_up_down=self._pull.value)
            self._value = 1 if bool(value) else 0
            GPIO.output(self._pin_num, self._value)
            return self._value

    def value(self, value: [bool, int] = None) -> int:
        """ Set/get the pin value

        Args:
            value (bool/int, optional): pin value, leave it empty to get the value(0/1). Defaults to None.

        Returns:
            int: pin value(0/1)

        Raises:
            ValueError: if pin mode is IN
        """
        if value == None:
            value = self.raw()
            if self._active_state == Active.HIGH:
                return value
            else:
                return value + 1 & 1
        else:
            if self._active_state == Active.HIGH:
                self.raw(value)
            else:
                self.raw(value + 1 & 1)

    def on(self) -> int:
        """ Set pin on(high)

        Returns:
            int: pin value(1)
        """
        return self.value(1)

    def off(self) -> int:
        """ Set pin off(low)

        Returns:
            int: pin value(0)
        """
        return self.value(0)

    def high(self) -> int:
        """ Set pin high(1)

        Returns:
            int: pin value(1)
        """
        return self.raw(1)

    def low(self) -> int:
        """ Set pin low(0)

        Returns:
            int: pin value(0)
        """
        return self.raw(0)

    def irq(self, handler: Callable[[], None], trigger: Trigger = Trigger.BOTH) -> None:
        """ Set the pin interrupt

        Args:
            handler (Callable[[], None]): interrupt handler callback function
            trigger (Trigger, optional): interrupt trigger(RISING, FALLING, RISING_FALLING). Defaults to Trigger.BOTH.

        Raises:
            ValueError: if trigger is not valid
        """
        GPIO.add_event_detect(self._pin_num, trigger.value, handler, bouncetime=self._bounce_time*1000)
        self._irq_inited = True

    def init_irq(self) -> None:
        """ Initialize the pin interrupt
        """
        if self._irq_inited:
            return
        self.log.debug("Setting up IRQ for pin %d", self._pin_num)
        GPIO.add_event_detect(self._pin_num, Trigger.BOTH.value, self.irq_handler, bouncetime=int(self._bounce_time*1000))
        self._irq_inited = True

    def irq_handler(self, channel: int) -> None:
        """ Handle the pin interrupt

        Args:
            channel (int): pin number
        """
        if self._on_activated and self.value() == 1:
            self.log.debug("Pin %d activated", self._pin_num)
            self._on_activated()
        elif self._on_deactivated and self.value() == 0:
            self.log.debug("Pin %d deactivated", self._pin_num)
            self._on_deactivated()

    @property
    def when_activated(self) -> Callable[[], None]:
        """ Get the pressed handler

        Returns:
            Callable[[], None]: pressed handler
        """
        return self._on_activated
    
    @when_activated.setter
    def when_activated(self, handler: Callable[[], None]) -> None:
        """ Set the pressed handler

        Args:
            handler (Callable[[], None]): pressed handler
        """
        self.init_irq()
        self._on_activated = handler

    @property
    def when_deactivated(self) -> Callable[[], None]:
        """ Get the released handler

        Returns:
            Callable[[], None]: released handler
        """
        return self._on_deactivated

    @when_deactivated.setter
    def when_deactivated(self, handler: Callable[[], None]) -> None:
        """ Set the released handler

        Args:
            handler (Callable[[], None]): released handler
        """
        self.init_irq()
        self._on_deactivated = handler
