#!/usr/bin/env python3
from gpiozero import OutputDevice, DigitalInputDevice, Button
from typing import Callable

class Pin():
    """ Pin manipulation class """

    OUT = 0x01
    """Pin mode output"""
    IN = 0x02
    """Pin mode input"""

    PULL_UP = 0x11
    """Pin internal pull up"""
    PULL_DOWN = 0x12
    """Pin internal pull down"""
    PULL_NONE = None
    """Pin internal pull none"""

    IRQ_FALLING = 0x21
    """Pin interrupt falling"""
    IRQ_RISING = 0x22
    """Pin interrupt falling"""
    IRQ_RISING_FALLING = 0x23
    """Pin interrupt both rising and falling"""

    def __init__(self, pin: int, mode: int = None, pull: int = None, active_state: bool = True, bounce_time: float = None):
        """ Initialize a pin

        Args:
            pin (int): pin number of Raspberry Pi
            mode (int, optional): pin mode(IN/OUT). Defaults to None.
            pull (int, optional): pin pull up/down(PUD_UP/PUD_DOWN/PUD_NONE). Defaults to None.
            active_state (bool, optional): active state of pin,  
                            If True, when the hardware pin state is HIGH, the software pin is HIGH. 
                            If False, the input polarity is reversed. Defaults to None.
            bounce_time (float, optional): bounce time of pin interrupt. Defaults to None.
        """

        # parse pin
        self._pin_num = pin
        
        # setup
        self._value = 0
        self.gpio = None
        self.setup(mode, pull, active_state, bounce_time)

    def close(self) -> None:
        """ Close the pin """
        self.gpio.close()

    def deinit(self) -> None:
        """Deinitialize the pin"""
        self.gpio.close()
        self.gpio.pin_factory.close()

    def setup(self, mode: int = None, pull: int = None, active_state: bool = None, bounce_time: float = None) -> None:
        """ Setup the pin

        Args:
            mode (int, optional): pin mode(IN/OUT). Defaults to None.
            pull (int, optional): pin pull up/down(PUD_UP/PUD_DOWN/PUD_NONE). Defaults to None.
            active_state (bool, optional): active state of pin,  
                            If True, when the hardware pin state is HIGH, the software pin is HIGH. 
                            If False, the input polarity is reversed. Defaults to None.
            bounce_time (float, optional): bounce time of pin interrupt in seconds. Defaults to None.
        """
        # check mode
        if mode in [None, self.OUT, self.IN]:
            self._mode = mode
        else:
            raise ValueError(
                f'mode param error, should be None, Pin.OUT, Pin.IN')
        # check pull
        if pull in [self.PULL_NONE, self.PULL_DOWN, self.PULL_UP]:
            self._pull = pull
        else:
            raise ValueError(
                f'pull param error, should be None, Pin.PULL_NONE, Pin.PULL_DOWN, Pin.PULL_UP'
            )
        #
        if self.gpio != None:
            if self.gpio.pin != None:
                self.gpio.close()
        #
        if mode in [None, self.OUT]:
            self.gpio = OutputDevice(self._pin_num)
        else:
            if pull == self.PULL_UP:
                self.gpio = DigitalInputDevice(self._pin_num, pull_up=True, active_state=None, bounce_time=bounce_time)
            elif pull == self.PULL_DOWN:
                self.gpio = DigitalInputDevice(self._pin_num, pull_up=False, active_state=None, bounce_time=bounce_time)
            else:
                self.gpio = DigitalInputDevice(self._pin_num, pull_up=None, active_state=active_state, bounce_time=bounce_time)

    def __call__(self, value: bool = None) -> int:
        """ Set/get the pin value

        Args:
            value (bool, optional): pin value, leave it empty to get the value(0/1). Defaults to None.

        Returns:
            int: pin value(0/1)
        """
        return self.value(value)

    def value(self, value: bool = None) -> int:
        """ Set/get the pin value

        Args:
            value (bool, optional): pin value, leave it empty to get the value(0/1). Defaults to None.

        Returns:
            int: pin value(0/1)
        """
        if value == None:
            if self._mode in [None, self.OUT]:
                self.setup(self.IN)
            result = self.gpio.value
            return result
        else:
            if self._mode in [self.IN]:
                self.setup(self.OUT)
            if bool(value):
                value = 1
                self.gpio.on()
            else:
                value = 0
                self.gpio.off()
            return value

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
        return self.on()

    def low(self) -> int:
        """ Set pin low(0)

        Returns:
            int: pin value(0)
        """
        return self.off()

    def irq(self, handler: Callable[[], None], trigger: int = None, bouncetime: int = 200, pull: int = None) -> None:
        """ Set the pin interrupt

        Args:
            handler (Callable[[], None]): interrupt handler callback function
            trigger (int, optional): interrupt trigger(RISING, FALLING, RISING_FALLING). Defaults to None.
            bouncetime (int, optional): interrupt bouncetime in miliseconds. Defaults to 200.

        Raises:
            ValueError: if trigger is not valid
        """
        # check trigger
        if trigger not in [
                self.IRQ_FALLING, self.IRQ_RISING, self.IRQ_RISING_FALLING
        ]:
            raise ValueError(
                f'trigger param error, should be None, Pin.IRQ_FALLING, Pin.IRQ_RISING, Pin.IRQ_RISING_FALLING'
            )

        # check pull
        if pull in [self.PULL_NONE, self.PULL_DOWN, self.PULL_UP]:
            self._pull = pull
            if pull == self.PULL_UP:
                _pull_up = True
            else:
                _pull_up = False
        else:
            raise ValueError(
                f'pull param error, should be None, Pin.PULL_NONE, Pin.PULL_DOWN, Pin.PULL_UP'
            )

        pressed_handler = None
        released_handler = None

        if not isinstance(self.gpio, Button):
            if self.gpio != None:
                self.gpio.close()
            self.gpio = Button(pin=self._pin_num,
                               pull_up=_pull_up,
                               bounce_time=float(bouncetime / 1000))
            self._bouncetime = bouncetime
        else:
            if bouncetime != self._bouncetime:
                pressed_handler = self.gpio.when_pressed
                released_handler = self.gpio.when_released
                self.gpio.close()
                self.gpio = Button(pin=self._pin_num,
                                   pull_up=_pull_up,
                                   bounce_time=float(bouncetime / 1000))
                self._bouncetime = bouncetime

        if trigger in [None, self.IRQ_FALLING]:
            pressed_handler = handler
        elif trigger in [self.IRQ_RISING]:
            released_handler = handler
        elif trigger in [self.IRQ_RISING_FALLING]:
            pressed_handler = handler
            released_handler = handler

        if pressed_handler is not None:
            self.gpio.when_pressed = pressed_handler
        if released_handler is not None:
            self.gpio.when_released = released_handler


    @property
    def when_activated(self) -> Callable[[], None]:
        """ Get the pressed handler

        Returns:
            Callable[[], None]: pressed handler
        """

        return self.gpio.when_activated
    
    @when_activated.setter
    def when_activated(self, handler: Callable[[], None]) -> None:
        """ Set the pressed handler

        Args:
            handler (Callable[[], None]): pressed handler
        """
        self.gpio.when_activated = handler
        

    @property
    def when_deactivated(self) -> Callable[[], None]:
        """ Get the released handler

        Returns:
            Callable[[], None]: released handler
        """
        return self.gpio.when_deactivated

    @when_deactivated.setter
    def when_deactivated(self, handler: Callable[[], None]) -> None:
        """ Set the released handler

        Args:
            handler (Callable[[], None]): released handler
        """
        self.gpio.when_deactivated = handler
