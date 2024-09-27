"""
program: FTDI SPI Flash Utility
author: curtis mechling <cmechlin@gmail.com>
date: 2024-09-18
version: 1.0

description:
This script reads data from a SPI flash memory using an FTDI FT232H USB to SPI bridge.
The script uses the pyftdi library to communicate with the FTDI chip and read data
 from the SPI flash memory.
 https://github.com/eblot/pyftdi
 https://eblot.github.io/pyftdi/api/spi.html

The script is designed to read data from a SPI flash memory connected
 to the FTDI chip using the following pinout:
--------------------------------------------------------------------
| Description | SPI Flash Pin | FTDI Pin | C232HM Cable Color Code |
--------------------------------------------------------------------
| CS          | 1             | ADBUS3   | Brown                   |
| MISO/DO     | 2             | ADBUS2   | Green                   |
| WP          | 3             | ADBUS4   | Grey                    |
| GND         | 4             | N/A      | Black                   |
| MOSI/DI     | 5             | ADBUS1   | Yellow                  |
| CLK         | 6             | ADBUS0   | Orange                  |
| HOLD        | 7             | ADBUS5   | Purple                  |
| Vcc         | 8             | N/A      | Red                     |
--------------------------------------------------------------------

credits:
Thanks devttys0 for the inspiration and hints in the original code

jedec identification
http://www.idhw.com/

"""

import logging
from pyftdi.spi import SpiIOError
from pyftdi.usbtools import UsbToolsError
from flashreader import FlashReader

# Configure the logging
logging.basicConfig(
    level=logging.DEBUG,  # Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
    handlers=[
        logging.FileHandler("flash_reader.log"),  # Log to file
        logging.StreamHandler(),  # Also log to console
    ],
)


def main():
    """Main function"""
    reader = None
    try:
        reader = FlashReader()
        jedec_id = reader.get_jedec_id()
        logging.info("JEDEC ID: 0x%s", jedec_id.hex())

        # reader.read_data(0, 0x7FFFFF, 256)
        # reader.show()
        # reader.save("flash_dump.bin", "binary")
        # reader.save("flash_dump.txt", "text")

    except UsbToolsError as e:
        logging.error("USB Error: %s", e)
    except SpiIOError as e:
        logging.error("SPI Error: %s", e)
    except ValueError as e:
        logging.error("Value Error:%s", e)
    except FileNotFoundError as e:
        logging.error("File not found: %s", e)
    except PermissionError as e:
        logging.error("Permission Error: %s", e)
    except OSError as e:
        logging.error("OS Error: %s", e)

    finally:
        if reader:
            reader.close()


if __name__ == "__main__":
    main()
