#!/usr/bin/env python3
"""
A serial monitor that allows arbitrary baud rates

I've had issues with baud rates like 1e6 on screen on MacOs, but this script
alleviates that issue. It's also a bit simpler than installing and configuring
minicom on Linux if you only need a monitor interface. If you need to send text
over the wire, use an actual terminal program like minicom.

Usage:
  ./sermon.py [-h] device_path baud_rate

Future Work:
 [ ] Make it possible to load device paths and baud rates from a YAML config
     file like the fpgds-cfg tool can do with deployment paths and interfaces

(C) 2024 Kyle Botteon
This file is part of HERMIT. Refer to the LICENSE in that repository.
"""

import argparse as libArgparse
import sys as libSys
import serial as libSerial
import os as libOs
import errno as libErrno
import shutil as libShutil

from serial import SerialException
from collections import deque

# Align all possible messages
STR_DEVICE = "> Device"
STR_PATH = ">   Path"
STR_BAUD = ">   Baud"
STR_NOTE = "> Ctrl+c to Exit"

# Maximum line number to count to before repeating, so half your terminal isn't
# taken up printing that you're on line 123093502394 of serial output
LINE_MAX = 10000

################################################################################


class QuietArgumentParser(libArgparse.ArgumentParser):
    """
    Gets rid of the confusing traceback when a parsing error occurs
    """

    def error(self, message):
        libSys.stderr.write(f"{message}\n")
        libSys.exit(libErrno.EINVAL)


################################################################################


def ap_validate_path(proposed):
    """
    Verifies the proposed path to a serial device exists
    """
    full_path = libOs.path.abspath(proposed)

    if libOs.path.exists(full_path):
        return full_path
    else:
        raise libArgparse.ArgumentTypeError(
            f"Requested device {proposed} does not exist"
        )


################################################################################


def create_parser():
    ap = QuietArgumentParser(
        prog="sermon",
        description="Monitors a serial port and prints all characters received",
    )

    ap.add_argument(
        "device_path",
        type=ap_validate_path,
        help="Serial device path (e.g. /dev/ttyUSB0)",
    )

    ap.add_argument("baud_rate", type=int, help="Baud rate (e.g. 115200)")

    return ap


################################################################################


def print_banner(device, baud):
    """
    Print a banner message at the top of the monitor
    """
    # Clear the terminal
    libSys.stdout.write("\033c")

    print(f"{STR_DEVICE}: {device}")

    # If it's a symlink, get the actual path for display
    abs_path = libOs.path.realpath(device)
    if abs_path != device:
        print(f"{STR_PATH}: {abs_path}")

    print(f"{STR_BAUD}: {baud}")
    print(f">")
    print(f"{STR_NOTE}")
    print(f"")


################################################################################


def main(args):
    device = args.device_path
    baud = args.baud_rate

    # Keep a record of the last 20 lines, because we need to reprint for every
    # new line in order to maintain the title banner
    line_buffer = deque(maxlen=20)
    print_banner(device, baud)

    # Get active terminal size for trimming
    term_width = libShutil.get_terminal_size().columns

    # Open the device
    try:
        serial_handle = libSerial.Serial(device, baud, timeout=1)
    except SerialException as error:
        print(f"Error opening {device} with {error}")
        libSys.exit(libErrno.ENODEV)

    # The actual main() loop
    # Monitor the input until KeyboardInterrupt
    line_index = 1
    while True:
        try:
            data = serial_handle.readline()
            if data:
                # See if there's a line to be had
                try:
                    decoded_data = data.decode().strip()
                except UnicodeDecodeError as error:
                    print(f"> {error}")
                    continue

                # Serial can return with nothing after one second; or something
                if decoded_data:
                    # Add a line number
                    line_idx_stn = f"{line_index:0{len(str(LINE_MAX))}}"
                    line_index = line_index + 1
                    if line_index >= LINE_MAX:
                        line_index = 0
                    # Add the character data
                    trimmed = decoded_data[:term_width]
                    line_buffer.append(f"{line_idx_stn}: {trimmed}")
                    # Reprint the screen
                    print_banner(device, baud)
                    for line in line_buffer:
                        print(line)

        except KeyboardInterrupt:
            if serial_handle.is_open:
                serial_handle.close()
            break


################################################################################

if __name__ == "__main__":
    # Get command line arguments
    args = create_parser().parse_args()
    # Start program
    main(args)
