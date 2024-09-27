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
from pyftdi.spi import SpiController


class FlashReader:
    """
    Flash reader class for SPI flash chips.
    """

    COMMANDS = {
        "READ": 0x03,
        "FAST_READ": 0x0B,
        "DUAL_OUTPUT_FAST_READ": 0x3B,
        "QUAD_OUTPUT_FAST_READ": 0x6B,
        "DUAL_IO_FAST_READ": 0xBB,
        "QUAD_IO_FAST_READ": 0xEB,
        "READ_STATUS_REGISTER": 0x05,
        "WRITE_STATUS_REGISTER": 0x01,
        "WRITE_ENABLE": 0x06,
        "WRITE_DISABLE": 0x04,
        "ERASE_SECTOR": 0x20,
        "ERASE_BLOCK": 0xD8,
        "ERASE_CHIP": 0xC7,
        "POWER_DOWN": 0xB9,
        "RELEASE_POWER_DOWN": 0xAB,
        "READ_MANUFACTURER_DEVICE_ID": 0x90,
        "READ_UNIQUE_ID": 0x4B,
        "READ_JEDEC_ID": 0x9F,
    }

    def __init__(self, frequency: int = 1e6, mode: int = 0) -> None:
        logging.info("Initializing FlashReader")
        self.frequency = frequency
        self.mode = mode
        self.data = None
        # Initialize SPI controller and configure
        self.spi = SpiController()
        self.spi.configure("ftdi://ftdi:232h:FTXLTVFX/1")

        # Get SPI device
        self.device = self.get_spi_device()

    def __str__(self) -> str:
        # User-friendly string representation
        return f"FlashReader(frequency={self.frequency}Hz, mode={self.mode})"

    def __repr__(self) -> str:
        # Developer-friendly string representation (usually used in debugging)
        return f"FlashReader(frequency={self.frequency}, mode={self.mode})"

    def close(self) -> None:
        """Close SPI controller if configured."""

        if self.spi.configured:
            self.spi.close()
            logging.info("SPI controller closed.")

    def get_spi_device(self) -> object:
        """Get SPI device with default chip select 0."""
        logging.info("Getting SPI device.")
        logging.debug(
            "Chip Select: %s, Frequency: %sHz, Mode: %s", 0, self.frequency, self.mode
        )
        return self.spi.get_port(cs=0, freq=self.frequency, mode=self.mode)

    def get_jedec_id(self) -> bytearray:
        """Get JEDEC ID from flash memory."""
        logging.info("Reading JEDEC ID from flash memory.")
        data = self.device.exchange(bytes([self.COMMANDS["READ_JEDEC_ID"]]), 3)
        hex_data = "0x" + "".join(f"{byte:02X}" for byte in data)
        logging.debug("JEDEC ID Value: %s", hex_data)
        return data

    def read_data(
        self,
        address: int = 0x000000,
        size: int = 0x100000,
        chunk_size: int = 16,
        endianess: str = "big",
    ) -> None:
        """
        Read data from the SPI flash memory

        :param address: Starting address to read from (default: 0x000000)
        :param size: Total size of data to read (default: 0x100000 (1MB))
        :param chunk_size: Size of each chunk to read in one go (default: 16 bytes)
        :param endianess: Byte order for the address (default: 'big')
        :return: bytearray of read data
        """

        address_str = f"0x{address:08X}"
        size_str = f"0x{size:08X}"

        logging.info(
            "Reading data from address %s, size %s, chunk size %s bytes, endianess %s",
            address_str,
            size_str,
            chunk_size,
            endianess,
        )
        # Read command
        read_cmd = bytes([self.COMMANDS["READ"]])
        self.data = bytearray()

        # Read data
        for addr in range(address, address + size, chunk_size):
            # Build full read command including address and chunk size
            command = read_cmd + addr.to_bytes(3, byteorder=endianess)
            chunk = self.device.exchange(command, chunk_size)
            self.data.extend(chunk)

    def save(self, filename: str, filetype: str = "binary") -> None:
        """
        Write flash data to a file, either as raw binary or a hex string dump.

        :param filename: The name of the output file
        :param filetype: The type of file to write ("binary" or "text")
        :raises ValueError: If the filetype is invalid
        """
        if not self.data:
            logging.warning("No data to write.")
            return

        if filetype not in {"binary", "text"}:
            raise ValueError("filetype must be 'binary' or 'text'")

        # Ensure the file has the right extension based on the type
        file_extension = ".bin" if filetype == "binary" else ".txt"
        if not filename.endswith(file_extension):
            filename += file_extension

        # Write binary data
        if filetype == "binary":
            with open(filename, "wb") as bin_file:
                bin_file.write(self.data)
            logging.info("Binary data written to %s", filename)

        # Write hex string dump to text file
        elif filetype == "text":
            with open(filename, "w", encoding="utf-8") as text_file:
                for i in range(0, len(self.data), 16):
                    chunk = self.data[i : i + 16]
                    hex_data = " ".join(f"{byte:02X}" for byte in chunk)
                    text_file.write(f"0x{i:08X}: {hex_data}\n")
            logging.info("Hex dump written to %s", filename)

    def show(self, chunk_size=16) -> None:
        """
        Display data in hexadecimal format.

        :param chunk_size: Number of bytes to display per line
        """
        logging.info("Displaying data.")
        if self.data:
            for i in range(0, len(self.data), chunk_size):
                chunk = self.data[i : i + chunk_size]
                hex_data = " ".join(f"{byte:02X}" for byte in chunk)
                address_str = f"{i:08X}:"
                print("%s: %s", address_str, hex_data)
        else:
            logging.warning("No data to display.")


def main():
    pass


if __name__ == "__main__":
    main()
