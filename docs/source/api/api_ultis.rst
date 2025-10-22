

Utility Module
========================================


This module provides utility functions and hardware interface controls for the Fusion HAT+ platform. It includes logging utilities, speaker control, pin control, battery monitoring, and I2C-based device interactions.

**Color Logging**


.. function:: print_color(msg, end='\n', file=sys.stdout, flush=False, color='')

   Print a message in a specified ANSI color.

.. function:: info(msg, end='\n', file=sys.stdout, flush=False)

   Print a white message.

.. function:: debug(msg, end='\n', file=sys.stdout, flush=False)

   Print a gray debug message.

.. function:: warn(msg, end='\n', file=sys.stdout, flush=False)

   Print a yellow warning message.

.. function:: error(msg, end='\n', file=sys.stdout, flush=False)

   Print a red error message.

**System and Command Utilities**


.. function:: set_volume(value)

   Set system audio volume (0–100).

   :param value: Volume level.
   :type value: int

.. function:: run_command(cmd)

   Execute a shell command.

   :param cmd: Command string.
   :type cmd: str
   :returns: Tuple of (status, output).
   :rtype: tuple

.. function:: command_exists(cmd)

   Check if a command is available in the system.

   :param cmd: Command name.
   :type cmd: str
   :returns: True if exists, False otherwise.
   :rtype: bool

.. function:: is_installed(cmd)

   Check if a command is installed using ``which``.

   :param cmd: Command name.
   :type cmd: str
   :returns: True or False.
   :rtype: bool

.. function:: get_username()

   Get the username of the current user (or SUDO user).

   :returns: Username string.
   :rtype: str

.. function:: mapping(x, in_min, in_max, out_min, out_max)

   Map a value from one range to another.

   :returns: Remapped value.
   :rtype: float

**Network Utility**


.. function:: get_ip(ifaces=['wlan0', 'eth0'])

   Get the IPv4 address from a list of interfaces.

   :param ifaces: Network interface names.
   :type ifaces: list or str
   :returns: IP address or False.
   :rtype: str or bool

**MCU and Hardware Controls**


.. function:: get_battery_voltage()

   Read battery voltage via ADC channel A4.

   :returns: Battery voltage in volts.
   :rtype: float

**Speaker Control**


.. function:: enable_speaker()

   Enable the onboard speaker using GPIO or I2C configuration.

.. function:: disable_speaker()

   Disable the onboard speaker using GPIO or I2C configuration.

**Device Input Status**


.. function:: get_usr_btn()

   Read the user button state.

   :returns: True if pressed, False otherwise.
   :rtype: bool

.. function:: get_charge_state()

   Check if the device is charging.

   :returns: True if charging.
   :rtype: bool

.. function:: get_shutdown_request()

   Read the shutdown request status.

   :returns: 
      - 0: No request  
      - 1: Low battery shutdown  
      - 2: Button-initiated shutdown  
   :rtype: int

**User LED Control**


.. function:: set_user_led(state)

   Set the user LED state.

   :param state: 
      - 0: Off  
      - 1: On  
      - 2: Toggle  
   :type state: int

