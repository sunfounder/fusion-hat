RC522 Class
==================

The ``RC522`` class allows low-level control over RC522 RFID hardware for reading and writing MIFARE-compatible cards. It supports initialization, authentication, block data reading and writing, and card identification.


**Class: RC522**


.. class:: RC522()

    Initializes SPI connection and sets up internal buffers for card interaction.

**Methods**


.. method:: Pcd_start()

    Initializes the RC522 and configures the ISO type for card communication.


.. method:: read(addr, max_retries=3)

    Read and reconstruct block data from card with retry logic.

    :param addr: Block address.
    :param max_retries: Number of retry attempts.
    :return: Tuple (UID string, data string)

.. method:: write(addr, data)

    Write data to a card block with retry until success.

    :param addr: Block address.
    :param data: List of bytes.
    :return: None

**Constants**


This class defines numerous constants for RC522 commands, registers, and PICC operations, including:

- ``PCD_IDLE``, ``PCD_AUTHENT``, ``PCD_TRANSCEIVE``, ...
- ``PICC_REQIDL``, ``PICC_AUTHENT1A``, ``PICC_READ``, ``PICC_WRITE``, ...
- ``CommandReg``, ``Status1Reg``, ``FIFODataReg``, ...

Refer to the RC522 datasheet for detailed descriptions.


**Example Usage**


.. code-block:: python

   from fusion_hat import RC522

   rc = RC522()
   rc.Pcd_start()
   x = input("Please enter the data to be written:")
   print("Reading...Please place the card...")
   data = [ord(x[i]) for i in range(len(x))]

   try:
      rc.write(2,data)
      uid,message = rc.read(2)
      print("UID:", uid)
      print("Successfully retrieved data block:", message)
      input("Press enter to exit...")
   except:
      print("Error")