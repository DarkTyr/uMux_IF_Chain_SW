# -*- coding: utf-8 -*-
# ArgParse for parsing com port
import argparse

import IPython

# Used for timing data transfer for the long_data_check()
import time

#tqdm provides a utility for a progress bar
import tqdm

# CSV is used to process the initialization text file
import csv

# the main classes here
from uMux_IF_Chain.uMux_IF import uMux_IF_Rev1
from uMux_IF_Chain.base_board import base_board_rev3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("com_port", help="Com Port to communicate with Base Board")
    parser.add_argument("-v", "--verbosity", help="Set terminal debugging verbosity", action="count", default=0)
    args = parser.parse_args()

    # Create base board interface class and set debug message level
    bb = base_board_rev3.Base_Board_Rev3(args.com_port)
    bb.get_device_info()
    if(args.verbosity == 0):
        bb.auto_print = 0
    elif(args.verbosity == 1):
        bb.auto_print = 1
    elif(args.verbosity == 2):
        bb.auto_print = 2

    print("")

    # Determine what IF_Boards Rev1 are present
    dev_stack = bb.spi_get_dev_stack()
    print("DEV_STACK : 0x" + hex(dev_stack).upper()[2:])
    n_ifb = dev_stack.bit_length()
    ifb = [0x00] * n_ifb

    # Instantiate classes for the IF_Boards Rev1
    for i in range(dev_stack.bit_length()):
        ifb[i] = uMux_IF_Rev1.UMux_IF_Rev1(bb, 0x1 << i)
        if(args.verbosity == 0):
            ifb[i].debug = 0
        elif(args.verbosity == 1):
            ifb[i].debug = 1
        elif(args.verbosity == 2):
            ifb[i].debug = 2

    IPython.start_ipython(argv=[], user_ns=locals())

if (__name__ == '__main__'):
    main()