# FTDI SPI Flash Utility

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

This utility allows you to read data from a SPI flash memory using an FTDI FT232H USB-to-SPI bridge. It communicates with SPI flash memory and provides features such as reading JEDEC ID, reading flash data, saving the data to binary or text (hex dump) files, and displaying the read data in a structured format.

The project is built using the `pyftdi` library for handling SPI communication. The goal of this project is to facilitate SPI flash memory interaction for debugging and development purposes.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
  - [Reading Data](#reading-data)
  - [Saving Data](#saving-data)
  - [Displaying Data](#displaying-data)
- [Logging](#logging)
- [Example](#example)
- [Supported Hardware](#supported-hardware)
- [Credits](#credits)
- [License](#license)

## Features

- Read JEDEC ID of a SPI flash memory.
- Read and display data from SPI flash memory.
- Save flash data as raw binary or as a hex dump (text file).
- Compatible with FTDI FT232H USB-to-SPI bridges using `pyftdi`.
- Logging for debugging and diagnostics.

## Setup

### Prerequisites

- Python 3.8+
- FTDI FT232H (or compatible) USB-to-SPI device. [Link](https://ftdichip.com/wp-content/uploads/2023/07/DS_C232HM_MPSSE_CABLE-.pdf)
- SPI flash memory chip.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/cmechlin/ftdi-spi-flash-utility.git
   cd ftdi-spi-flash-utility
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   The main dependency is [`pyftdi`](https://eblot.github.io/pyftdi/), a Python library to interact with FTDI chips.

## Usage

### Reading Data

To read data from the SPI flash memory, modify the `main()` function in `flash_reader.py` as needed:

```python
reader.read_data(0x000000, 0x7FFFFF, 256)  # Read 8 MB of data
```

### Saving Data

You can save the flash data either in raw binary format or as a hex dump in a text file:

```python
reader.save("flash_dump.bin", "binary")  # Save data as binary
reader.save("flash_dump.txt", "text")    # Save data as hex dump
```

### Displaying Data

To display the data directly in the terminal in a human-readable format:

```python
reader.show(chunk_size=16)  # Display 16 bytes per line
```

### Logging

Logs are generated automatically in both the console and a `flash_reader.log` file. The logging level is set to `DEBUG` by default for detailed information. You can adjust this in the `logging.basicConfig` call.

Example log output:

```log
2024-09-18 10:45:23,123 - INFO - Initializing FlashReader...
2024-09-18 10:45:24,456 - DEBUG - SPI device configured with frequency 1000000.0Hz and mode 0
2024-09-18 10:45:25,789 - INFO - Reading JEDEC ID from flash memory.
2024-09-18 10:45:26,012 - DEBUG - JEDEC ID received: 9F2017
2024-09-18 10:45:27,345 - INFO - Binary data written to flash_dump.bin
```

## Example

Here's a basic usage example. The following script reads the JEDEC ID from the SPI flash memory and saves the data to both a binary file and a hex dump file:

```python
from flash_reader import FlashReader

def main():
    reader = FlashReader()
    try:
        jedec_id = reader.get_jedec_id()
        print(f"JEDEC ID: {jedec_id.hex()}")

        # Read the first 8MB of the flash memory
        reader.read_data(0x000000, 0x7FFFFF, 256)

        # Save the data to a file
        reader.save("flash_dump.bin", "binary")
        reader.save("flash_dump.txt", "text")

        # Display data in chunks of 16 bytes
        reader.show(chunk_size=16)

    finally:
        reader.close()

if __name__ == "__main__":
    main()
```

## Supported Hardware

- **FTDI FT232H** or other compatible FTDI USB-to-SPI bridge.
- **SPI Flash Memory** (such as Winbond W25Q series).

## Credits

Special thanks to **devttys0** for the inspiration and hints in the original code. This project was built on top of their excellent work on SPI flash memory tools.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
