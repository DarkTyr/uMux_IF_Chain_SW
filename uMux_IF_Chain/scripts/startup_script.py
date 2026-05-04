# -*- coding: utf-8 -*-
'''
Script without any form of GUI, used to start up the uMux_IF_Chain and the base board interface.
Has had additions to allow command line interactions with the hardware rather than using a GUI. 
'''
import argparse
import time

import IPython

# the main classes here
from uMux_IF_Chain.base_board import umux_if_base_board
from uMux_IF_Chain.uMux_IF import umux_if_board


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to specify communication channel to Base Board")
    parser.add_argument("-v", "--verbosity", help="Set terminal debugging verbosity", action="count", default=0)
    parser.add_argument("-i", "--interactive", help="Drops into an iPython interface", action="store_true", default=False)
    parser.add_argument("-s", "--skip_startup", help="Skips startup r/w, only creates objects", action="store_true", default=0)
    parser.add_argument("-c", "--cards", help="Ignore auto detect of cards, takes in Hex Chip Select byte: 0x01 up to 0xFF",
                        default="0xFF")
    parser.add_argument("-t", "--temperature", help="Read Temperature", action="store_true", default=False)
    parser.add_argument("--synth_init", help="Initialize the synthesizers", action="store_true", default=False)
    parser.add_argument("--bb_loopback_en", help="Enable baseband loopback", action="store_true", default=False)
    parser.add_argument("--bb_loopback_dis", help="Disable baseband loopback", action="store_true", default=False)
    parser.add_argument("--power_on", help="Power On the IF_Board Stack if Applicable", action="store_true", default=False)
    args = parser.parse_args()

    # Create base board interface class and set debug message level
    bb = umux_if_base_board.open_uMux_IF_BaseBoard(url=args.url)
    if (~args.skip_startup == False):
        bb.get_device_info(print2console=True)


    bb.auto_print = args.verbosity

    print("")
    if(args.power_on):
        if(bb.HW_ID == "BB_Rev4_Pico"):
            cur_state = bb.stack_pwr_get()
            if(not(cur_state)):
                bb.stack_pwr_set(True)
                print(f"  Waiting {bb.power_on_delay_s} seconds for stack power on")
                time.sleep(bb.power_on_delay_s)
            else:
                pass
        else:
            pass
    else:
        pass
    print("")

    dev_stack = int(args.cards, 16)

    if (args.skip_startup == False):
        # Determine what IF_Boards Rev1 are present
        dev_stack = bb.stack_get_dev_stack()

    print("DEV_STACK : 0x" + hex(dev_stack).upper()[2:])
    n_ifb = dev_stack.bit_length()
    ifb = [0x00] * n_ifb

    # Instantiate classes for the IF_Boards Rev1
    for i in range(n_ifb):
        # ifb[i] = uMux_IF_Rev1.UMux_IF_Rev1(bb, 0x1 << i)
        ifb[i] = umux_if_board.open_uMux_IF_Board(bb, 0x1 << i)
        print(f"    Found {ifb[i].HW_ID}")
        ifb[i].debug = args.verbosity


    # Check for synth_init argument and initialize the synthesizers
    if (args.synth_init == True):
        print("Synthesizer initialization")
        for i in range(n_ifb):
            print("Initializing synthesizer {}...".format(i))
            ifb[i].synth_init()
            if (args.verbosity == 0):
                print("Synthesizer {} initialized".format(i))
            elif (args.verbosity >= 1):
                print("Synthesizer {} initialized".format(i))

    # Check for bb_loopback_en argument and enable baseband loopback
    if (args.bb_loopback_en == True):
        for i in range(n_ifb):
            ifb[i].base_band_loop_back_enable()
            if (args.verbosity == 0):
                print("Baseband loopback enabled for IFB {}".format(i))
            elif (args.verbosity >= 1):
                print("Baseband loopback enabled for IFB {}".format(i))

    # Check for bb_loopback_dis argument and disable baseband loopback
    if (args.bb_loopback_dis == True):
        for i in range(n_ifb):
            ifb[i].base_band_loop_back_disable()
            if (args.verbosity == 0):
                print("Baseband loopback disabled for IFB {}".format(i))
            elif (args.verbosity >= 1):
                print("Baseband loopback disabled for IFB {}".format(i))

    # If we performed a synth_init, we should go back and check the status of the synthesizers
    if (args.synth_init == True):
        for i in range(n_ifb):
            ret = ifb[i].synth_lock_status()
            if (args.verbosity == 0):
                print("Synthesizer {} Locked = {}".format(i, ret))
            elif (args.verbosity == 1):
                print("Synthesizer {} Locked = {}".format(i, ret))
            elif (args.verbosity == 2):
                print("Synthesizer {} Locked = {}".format(i, ret))

    # Check for temperature argument and read temperature
    if (args.temperature == True):
        print("Reading temperatures    (Synth, MCU)")
        for i in range(n_ifb):
            ret = ifb[i].read_temperatures_C()
            if (args.verbosity == 0):
                print("Temperature for IFB {} = {}".format(i, ret))
            elif (args.verbosity == 1):
                print("Temperature for IFB {} = {}".format(i, ret))
            elif (args.verbosity == 2):
                print("Temperature for IFB {} = {}".format(i, ret))

    # If an interactive session is requested, drop into iPython and print information to the user
    if (args.interactive == True):
        banner = "____ uMux_IF_Chain-startup_script ____\n" \
            + " com channel url = {}\n".format(args.url) \
            + "       verbosity = {}\n".format(args.verbosity) \
            + "    skip_startup = {}\n".format(args.skip_startup) \
            + "           cards = {}\n".format(dev_stack) \
            + "Defined Classes:\n" \
            + "        bb = base_board_revX.Base_Board_RevX(args.url)\n" \
            + "     n_ifb = dev_stack.bit_length()\n" \
            + "     for i in range(n_ifb):\n" \
            + "        ifb[i] = uMux_IF_RevX.UMux_IF_RevX(bb, 0x1 << i)\n\n"
        print(banner)
        IPython.start_ipython(argv=[], user_ns=locals())


if (__name__ == '__main__'):
    main()
