# -*- coding: utf-8 -*-
# ArgParse for parsing com port
import argparse

# Used for timing data transfer for the long_data_check()
import time

#tqdm provides a utility for a progress bar
import tqdm

# CSV is used to process the initialization text file
import csv

# the main classes here
from uMux_IF_Chain.uMux_IF import uMux_IF_Rev1
from uMux_IF_Chain.base_board import base_board_rev3

# SYTNH_CONFIG_FILE = '../../HexRegisterValues.txt'
TICS_FILE = 'HexRegisterValues.txt'


if (__name__ == '__main__'):
    parser = argparse.ArgumentParser()
    parser.add_argument("com_port", help="Com Port to communicate with Base Board")
    parser.add_argument("-v", "--verbosity", help="Set terminal debugging verbosity", action="count", default=0)
    args = parser.parse_args()

    # Create base board interface class and set debug message level
    bb = base_board_rev3.Base_Board_Rev3(args.com_port)
    bb.get_devce_info()
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

    def synth_config_from_file(TICS_FILE = 'HexRegisterValues.txt'):
        print("Configuring LMX2592 from file: {}".format(TICS_FILE))
        with open(TICS_FILE) as csvfile:
            data = list(csv.reader(csvfile, delimiter='\t'))

        for reg in data:
            print(reg[0])
            reg_val = int(reg[1], base=16)
            for i in ifb:
                i._synth_write_int(reg_val)
        for i in ifb:
            i._lmx.trigger_cal()

    def long_data_check(itter, nBytes, inner_itter):
        print("long_data_check(itter={}, nBytes={}, inner_itter={})".format(itter, nBytes, inner_itter))
        # turn off debug message from bb class
        bb.auto_print = 0
        for i in ifb:
            # turn off all debug messages
            i.debug = 0
            # Add class parameter to track failed data
            i.data_fail = 0

        cur_time = time.monotonic()
        #main loop
        for x in tqdm.tqdm(range(itter)):
            #inner loop
            for i in ifb:
                i.data_fail += i.spi_loopback(nBytes, inner_itter)
            # time.sleep(0.001)
        nxt_time = time.monotonic()
        print("Complete!")
        print("long_data_check(itter={}, nBytes={}, inner_itter={})\n".format(itter, nBytes, inner_itter)
            + "\tResults:")

        total_data_MB = itter*nBytes*inner_itter/1024/1024
        total_time_s = nxt_time-cur_time
        for i in ifb:
            print("\tCS={}, Fails={}".format(i._cs, i.data_fail))
        
        print("Statistics:\n"
            + "\t    Total Time : {} s\n".format(total_time_s)
            + "\t               : {} min\n".format((total_time_s)/60)
            + "\t               : {} hr\n".format((total_time_s)/60/60)
            + "\t    Total Data : {} MB\n".format(total_data_MB)
            + "\tOne Board data : {} MB\n".format(total_data_MB/len(ifb))
            + "\t     Data Rate : {} MB/s\n".format(total_data_MB/total_time_s)
            + "\t               : {} kB/s".format(total_data_MB/total_time_s*1024)
            )
