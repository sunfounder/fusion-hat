fileDB Class
============

The ``fileDB`` class implements a lightweight file-based key-value database using plain text files. It provides simple methods to persist and retrieve configuration or calibration data in a structured format.

**Overview**

This class is ideal for storing small configuration settings where a full database solution is not required.


**Initialization**

.. method:: __init__(db, mode=None, owner=None)

   Initialize the database file. If the file does not exist, it will be created.

   :param db: Path to the database file.
   :type db: str
   :param mode: Optional file permissions to apply (e.g., ``'644'``).
   :type mode: str or None
   :param owner: Optional file owner (e.g., ``'pi'``).
   :type owner: str or None
   :raises ValueError: If ``db`` is not provided.

**Methods**

.. method:: file_check_create(file_path, mode=None, owner=None)

   Check if the file exists; if not, create the directory and file. Also applies optional permissions and ownership.

   :param file_path: Full path to the file to check or create.
   :type file_path: str
   :param mode: Optional file permission (e.g., ``'755'``).
   :type mode: str or None
   :param owner: Optional user to set as owner.
   :type owner: str or None

.. method:: get(name, default_value=None)

   Get a value from the database by key.

   :param name: Key name to retrieve.
   :type name: str
   :param default_value: Value to return if key is not found.
   :type default_value: str
   :return: Value associated with the key, or default if key is not found.
   :rtype: str

.. method:: set(name, value)

   Set or update a key-value pair in the database.

   :param name: Key name to set.
   :type name: str
   :param value: Value to store.
   :type value: str

**Usage Example**

.. code-block:: python

   from fusion_hat import fileDB

   # Initialize database
   db = fileDB('/opt/robot-hat/config.ini')

   # Set values
   db.set('speed', '120')
   db.set('mode', 'auto')

   # Get values
   print(db.get('speed'))         # Output: '120'
   print(db.get('missing_key'))   # Output: None (or specified default)

**File Format**

The file is a simple key-value format, allowing comments:

.. code-block:: ini

   # robot-hat config and calibration value of robots

   speed = 120
   mode = auto

**Notes**

- Comments starting with ``#`` are ignored.
- Keys and values are stored as strings.
- Missing keys return ``None`` or the provided ``default_value``.

