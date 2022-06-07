# -*- coding: utf-8 -*-
'''
Hardware and software testing

'''

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

# Freq Resolution is double the normal of 0.2MHz when the VCO doubler is active
frequnecy_list_MHz = [4000.0, 4100.0, 4200.0, 4300.0, 4400.0, 4444.0, 4456.2, 4555.0, 4555.2, 4600, 
                      5000.0, 5100.0, 5200.0, 5300.0, 5400.0, 5444.0, 5456.2, 5555.0, 5555.2, 5600,
                      6000.0, 6100.0, 6200.0, 6300.0, 6400.0, 6444.0, 6456.2, 6555.0, 6555.2, 6600,
                      7000.0, 7100.0, 7200.0, 7300.0, 7400.0, 7444.0, 7456.4, 7555.0, 7555.4, 7600]
                      
dac_list = [0, 1, 1000, 1024, 2042, 2048, 4090, 4096, 8192, 16383,
            1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000, 15000, 16000]

def test_bb_loopback_enable(if_board):
    if_board.base_band_loop_back_enable()
    cur_state = if_board.base_band_loop_back_get()
    if(cur_state == True):
        return "PASS - test_bb_loopback_enable"
    else:
        return "FAIL - test_bb_loopback_enable"

def test_bb_loopback_disable(if_board):
    if_board.base_band_loop_back_disable()
    cur_state = if_board.base_band_loop_back_get()
    if(cur_state == False):
        return "PASS - test_bb_loopback_enable"
    else:
        return "FAIL - test_bb_loopback_enable"

def test_nulling_up_set(if_board, value):
    if_board.nulling_up_set(value, value)
    dacI, dacQ = if_board.nulling_up_get()
    if((dacI == value) & (dacQ == value)):
        return ("PASS - test_nulling_up_set - " + str(value))
    elif(dacI != value):
        return ("FAIL - test_nulling_up_set - dacI - " + str(value))
    elif(dacQ != value):
        return ("FAIL - test_nulling_up_set - dacQ - " + str(value))
    else:
        return ("Fail - test_nulling_up_set - All  - " + str(value))

def test_nulling_dn_set(if_board, value):
    if_board.nulling_dn_set(value, value)
    dacI, dacQ = if_board.nulling_dn_get()
    if((dacI == value) & (dacQ == value)):
        return ("PASS - test_nulling_dn_set - " + str(value))
    elif(dacI != value):
        return ("FAIL - test_nulling_dn_set - dacI - " + str(value))
    elif(dacQ != value):
        return ("FAIL - test_nulling_dn_set - dacQ - " + str(value))
    else:
        return ("Fail - test_nulling_dn_set - All  - " + str(value))      

def test_synth_init(if_board):
    cur_lock_state = if_board.synth_lock_status()
    if(cur_lock_state == True):
        return ("N/R - test_synth_init - Synth Already locked and configured")
    
    if_board.synth_init()
    # Give the chip 100ms to perform its locking procedure and to update the internal flag
    time.sleep(0.10)
    cur_lock_state = if_board.synth_lock_status()
    if(cur_lock_state == True):
        return ("PASS - test_synth_init - Synth Initialized")
    else:
        return ("FAIL - test_synth_init - Synth unable to lock")

def test_synth_set_Frequency_MHz(if_board, freq_MHz):
    real_freq = if_board.synth_set_Frequency_MHz(freq_MHz)
    ret_freq = if_board.synth_get_Frequency_MHz()
    if((ret_freq == real_freq) & (freq_MHz == real_freq)):
        return ("PASS - test_synth_set_Frequency_MHz - " + str(freq_MHz))
    elif((ret_freq == real_freq)):
        return ("PASS - test_synth_set_Frequency_MHz - " + str(freq_MHz) + " : " + str(real_freq))
    else:
        return ("FAIL - test_synth_set_Frequency_MHz - " + str(freq_MHz) + " : " + str(real_freq) + " : " + str(ret_freq))

def test_synth_powerdown_bit(if_board):
    if_board.synth_powerdown_bit()
    power_down_state = if_board.synth_powerdown_get()
    if(power_down_state == True):
        return ("PASS - test_synth_powerdown_bit")
    else:
        return ("FAIL - test_synth_powerdown_bit")

def test_synth_powerup_bit(if_board):
    if_board.synth_powerup_bit()
    power_down_state = if_board.synth_powerdown_get()
    if(power_down_state == False):
        return ("PASS - test_synth_powerdown_bit")
    else:
        return ("FAIL - test_synth_powerdown_bit")

if (__name__ == '__main__'):
    parser = argparse.ArgumentParser()
    parser.add_argument("com_port", help="Com Port to communicate with Base Board")
    parser.add_argument("-n", "--num_itter", help="Set the number of itterations to run through test suite", default=1)
    parser.add_argument("-s", "--skip_running", help="Skip automatically starting tests", action="store_true", default=0)
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
        # Not a fan of adding an array to each class, but here we are
        ifb[i].test_results = []

    def read_all_temps():
        print("___ read_all_temps ___")
        for i in range(dev_stack.bit_length()):
            (synth_temp_C, mcu_temp_C) = ifb[i].read_temperatures_C()
            print("{} : synth_temp_C = {:.3f}, mcu_temp_C = {:.3f}".format(i, synth_temp_C, mcu_temp_C))

    read_all_temps()

    def run_test_suite():
        for x in ifb:
            x.test_results.append(test_bb_loopback_enable(x))
            x.test_results.append(test_bb_loopback_disable(x))
            x.test_results.append(test_synth_init(x))
            x.test_results.append(test_synth_powerdown_bit(x))
            x.test_results.append(test_synth_powerup_bit(x))
            for z in dac_list:
                x.test_results.append(test_nulling_up_set(x, z))
            for z in dac_list:
                x.test_results.append(test_nulling_dn_set(x, z))
            for z in frequnecy_list_MHz:
                x.test_results.append(test_synth_set_Frequency_MHz(x, z))
        read_all_temps()
    
    if(args.skip_running == False):
        run_test_suite()
    
