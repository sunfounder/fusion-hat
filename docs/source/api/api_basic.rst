_Basic_class
============

The ``_Basic_class`` is a base utility class providing logging and debug functionality to derived classes. It standardizes logging output using Python’s ``logging`` module and supports runtime configuration of debug levels.

**Initialization**

.. method:: __init__(debug_level='warning')

   Initialize the class and configure logging.

   :param debug_level: Initial debug level. Accepts:

      - Integer: 0 (critical), 1 (error), 2 (warning), 3 (info), 4 (debug)
      - String: "critical", "error", "warning", "info", or "debug"
      
   :type debug_level: int or str
   :raises ValueError: If an unsupported debug level is provided.

**Logging Attributes**

.. attribute:: _debug

   Shortcut to ``logger.debug`` – log a debug-level message.

.. attribute:: _info

   Shortcut to ``logger.info`` – log an info-level message.

.. attribute:: _warning

   Shortcut to ``logger.warning`` – log a warning-level message.

.. attribute:: _error

   Shortcut to ``logger.error`` – log an error-level message.

.. attribute:: _critical

   Shortcut to ``logger.critical`` – log a critical-level message.

**Debug Configuration**

.. attribute:: debug_level

   Get or set the debug level.

   :getter: Returns the current debug level as a string.
   :setter: Accepts either string or integer level. Updates logger configuration.

   :type: str or int

**Constants**

.. data:: DEBUG_LEVELS

   Mapping of debug level names to ``logging`` module constants.

   :type: dict

.. data:: DEBUG_NAMES

   List of debug level names in increasing verbosity:
   ``['critical', 'error', 'warning', 'info', 'debug']``

   :type: list

**Usage Example**

.. code-block:: python

   from fusion_hat import _Basic_class

   class MyComponent(_Basic_class):
       def __init__(self):
           super().__init__(debug_level='debug')
           self._info("Component initialized")
           self._debug("Debugging message")

   component = MyComponent()
   component.debug_level = 2  # Set to 'warning'
