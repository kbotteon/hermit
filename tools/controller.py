#!/usr/bin/env python3
"""
Controller for a HERMIT instance

At the moment, this just enables data downlink from the HERMIT logging core.

(C) 2024 Kyle Botteon
"""

import socket as libSocket
import struct as libStruct
import time as libTime
import multiprocessing as libMp
import argparse as libAp
import re as libRe
import os as libOs

################################################################################

total_bytes_received = 0
last_seq_no = None
expected_seq_no = 1
seq_gap = False

################################################################################

class TextLogger:

    def __init__(self, file):
        self.file_handle = open(file, 'w')

    def __del__(self):
        self.file_handle.close()

    def log(self, text):
        self.file_handle.write(text)
        self.file_handle.write('\n')

    def logImmediate(self, text):
        self.log(text)
        self.file_handle.flush()

################################################################################

class ScreenLogger:

    def __init__(self, state_lock, shared_counter):
        self.state_lock = state_lock
        self.run = True
        self._shared_counter = shared_counter

    def thread(self, context=0):
        """
        Prints the program status once per second
        Run with Multiprocessing to avoid screen manipulatio hosing network IO
        """
        while self.run:
            self.state_lock.acquire()
            val = self._shared_counter.value
            self.state_lock.release()

            if(val < 1024):
                print(f"RX: {val} Bytes")
            elif(val < 1024*1024):
                print(f"RX: {val/1024:.3f} KiB")
            else:
                print(f"RX: {val/1024/1024:.3f} MiB")

            libTime.sleep(1)

    def stop(self):
        self.run = False

################################################################################
