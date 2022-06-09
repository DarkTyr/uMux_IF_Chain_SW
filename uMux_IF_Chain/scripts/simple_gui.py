
from sre_parse import State
import tkinter as tk
import time

# ArgParse for parsing com port
import argparse

# Used for timing data transfer for the long_data_check()
import time

# CSV is used to process the initialization text file
import csv

# the main classes here
from uMux_IF_Chain.uMux_IF import uMux_IF_Rev1
from uMux_IF_Chain.base_board import base_board_rev3

SYTNH_CONFIG_FILE = '../../HexRegisterValues.txt'

# Indexes for the main array hiolding all of the sliders
IDX_STRINGVAR = 1
IDX_LABEL = 2
IDX_SCALE = 3
IDX_COMMAND = 4
IDX_FROM = 5
IDX_TO = 6

# Time delay to mimic use on real hardware
CMD_DELAY = 0.01

if (__name__ == '__main__'):
    parser = argparse.ArgumentParser()
    parser.add_argument("com_port", help="Com Port to communicate with Base Board")
    parser.add_argument("-f", "--file", help="Synthesizer Init File, used when synth_config_from_file() is called", default=SYTNH_CONFIG_FILE)
    parser.add_argument("-v", "--verbosity", help="Set terminal debugging verbosity", action="count", default=0)
    parser.add_argument("-t", "--test", help="Allows running without hardware", action="store_true")
    args = parser.parse_args()

    def read_scales():
        if(args.test == True):
            # Initial value for Frequency
            con[0][IDX_SCALE].set(5500)
            # Initial values for Lo Nulling set to half scale
            con[1][IDX_SCALE].set(8192)
            con[2][IDX_SCALE].set(8192)
            con[3][IDX_SCALE].set(8192)
            con[4][IDX_SCALE].set(8192)
        else:
            freq = ifb[dropdown_var.get()].synth_get_Frequency_MHz()
            con[0][IDX_SCALE].set(freq)
            dac0, dac1 = ifb[dropdown_var.get()].nulling_up_get()
            con[1][IDX_SCALE].set(dac0)
            con[2][IDX_SCALE].set(dac1)
            dac0, dac1 = ifb[dropdown_var.get()].nulling_dn_get()
            con[3][IDX_SCALE].set(dac0)
            con[4][IDX_SCALE].set(dac1)

    # command that can be called to update lock status of LO
    def readLockStatus():
        status = ifb[dropdown_var.get()].synth_lock_status()
        if(status == True):
            butLock.configure(text="LO Lock\nYes", bg="green")
        else:
            butLock.configure(text="LO Lock\nNo", bg="red")

    # command to shutdown LO
    def toggleShutDownLO():
        state = readShutDownState()
        if(state == True):
            ifb[dropdown_var.get()].synth_powerup_bit()
        else:
            ifb[dropdown_var.get()].synth_powerdown_bit()
        readShutDownState()
        readLockStatus()
    
    def readShutDownState():
        state = ifb[dropdown_var.get()].synth_powerdown_get()
        if(state == True):
            butShutDown.configure(text="Synth\nSHDN", bg="red")
        else:
            butShutDown.configure(text="Synth\nEnabled", bg="green")
        return state

    # commands to toggle base band loop back
    def toggleBBLoopBack():
        state = readBBLoopBack()
        if(state == True):
            ifb[dropdown_var.get()].base_band_loop_back_disable()
        else:
            ifb[dropdown_var.get()].base_band_loop_back_enable()
        readBBLoopBack()

    def readBBLoopBack():
        state = ifb[dropdown_var.get()].base_band_loop_back_get()
        if(state == True):
            butBBloop.configure(text="BB Loop\nEnabled", bg="green")
        else:
            butBBloop.configure(text="BB Loop\nDisabled", bg="red")
        return state

    # command to read temperatures
    def readTemperatures():
        (synth_temp_C, mcu_temp_C) = ifb[dropdown_var.get()].read_temperatures_C()
        print("Board= {}, synth_temp= {:.3f} C  mcu_temp = {:.3f} C".format(dropdown_var.get(), synth_temp_C, mcu_temp_C))

    # command that is called when the synth_init button is pressed
    def synthInit():
        if(args.verbosity > 0):
            print("synthInit : Pressed")

        # Call the init for the selected card
        ifb[dropdown_var.get()].synth_init()

        # Since this does change the frequency value read_scales is called
        read_scales()
        readLockStatus()
        readShutDownState()

    # command that is called when the Frequency scale is changed
    def freqChange(slide_value):
        if(args.verbosity > 0):
            print("freqChange : Slide Value = {}".format(slide_value))

        if(args.test == False):
            ifb[dropdown_var.get()].synth_set_Frequency_MHz(int(slide_value))

        if(args.test == True):
            time.sleep(CMD_DELAY)

    # command that is called when scale is changed for Lo Nulling
    def loNullUpI(slide_value):
        if(args.verbosity > 0):
            print("loNullUpI : Slide Value = {}".format(slide_value))

        if(args.test == False):
            ifb[dropdown_var.get()].nulling_up_set(int(slide_value),
                                                   int(con[2][IDX_SCALE].get()))

        if(args.test == True):
            time.sleep(CMD_DELAY)

    # command that is called when scale is changed for Lo Nulling
    def loNullUpQ(slide_value):
        if(args.verbosity > 0):
            print("loNullUpQ : Slide Value = {}".format(slide_value))

        if(args.test == False):
            ifb[dropdown_var.get()].nulling_up_set(int(con[1][IDX_SCALE].get()),
                                                   int(slide_value))

        if(args.test == True):
            time.sleep(CMD_DELAY)

    # command that is called when scale is changed for Lo Nulling
    def loNullDnI(slide_value):
        if(args.verbosity > 0):
            print("loNullDnI : Slide Value = {}".format(slide_value))

        if(args.test == False):
            ifb[dropdown_var.get()].nulling_dn_set(int(slide_value),
                                                   int(con[4][IDX_SCALE].get()))

        if(args.test == True):
            time.sleep(CMD_DELAY)

    # command that is called when scale is changed for Lo Nulling
    def loNullDnQ(slide_value):
        if(args.verbosity > 0):
            print("loNullDnQ : Slide Value = {}".format(slide_value))

        if(args.test == False):
            ifb[dropdown_var.get()].nulling_dn_set(int(con[3][IDX_SCALE].get()),
                                                   int(slide_value))

        if(args.test == True):
            time.sleep(CMD_DELAY)

    # Used to change focus with the tab key
    def focusNext(widget):
        widget.tk_focusNext().focus_set()
        return 'break'

    # used to change focus with Shift+Tab
    def focusPrev(widget):
        widget.tk_focusPrev().focus_set()
        return 'break'

    # used to incrememnt scale by 100
    def keyboard_scale_shift_increment(event):
        val = event.widget.get()
        val += 100 - 1
        event.widget.set(val)

    # used to decrement scale by 100
    def keyboard_scale_shift_decrment(event):
        val = event.widget.get()
        # decrement by desired minus 1 because then the scale will increment and send commadn
        val -= 100 - 1
        event.widget.set(val)

    def keyboard_scale_alt_increment(event):
        val = event.widget.get()
        val += 10 - 1
        event.widget.set(val)

    def keyboard_scale_alt_decrement(event):
        val = event.widget.get()
        val -= 10 - 1
        event.widget.set(val)

    def onDropDownChange(value):
        if(args.verbosity):
            print("onDropDownChange({})".format(value))
        read_scales()
        readLockStatus()
        readShutDownState()
        readBBLoopBack()

    if(args.test == False):
        # Create base board interface class and set debug message level
        bb = base_board_rev3.Base_Board_Rev3(args.com_port)
        bb.get_devce_info()
        if(args.verbosity == 0):
            bb.auto_print = 0
        elif(args.verbosity == 1):
            bb.auto_print = 1
        elif(args.verbosity == 2):
            bb.auto_print = 2
        
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
    else:
        n_ifb = 4
        ifb = [0x00] * n_ifb

    root = tk.Tk()

    ifb_opts = [*range(0, n_ifb)]

    # Instantiate the dropdown option menu for card selection
    dropdown_var = tk.IntVar()
    dropdown_var.set(0)
    dropdown = tk.OptionMenu(root,
                            dropdown_var,
                            *ifb_opts,
                            command=onDropDownChange)

    dropdown.grid(row = 0, column = 0)

    # Instantiate button to initialize synthesizers
    butInit = tk.Button(root, text="Synth Init", command = synthInit)
    butInit.grid(row = 0, column = 1)

    # Instantiate button to read the lock status
    butLock = tk.Button(root, text="Lock Status\n", command=readLockStatus)
    butLock.grid(row = 0, column = 2)

    # Instantiate button to read the lock status
    butShutDown = tk.Button(root, text="Synth\n", command=toggleShutDownLO)
    butShutDown.grid(row = 0, column = 3)

    # Instantiate button to read the lock status
    butBBloop = tk.Button(root, text="BB Loop\n", command=toggleBBLoopBack)
    butBBloop.grid(row = 0, column = 4)

    # Instantiate button to read temperatures
    butReadTemp = tk.Button(root, text="Read\nTemps\n", command=readTemperatures)
    butReadTemp.grid(row = 0, column = 5)

    # Main array holding pointers to objects used to make the GUI
    con = [
        # name, StringVar, label, slider, command, from_, to
        ["LO\nFrequency", 0x00, 0x00, 0x00, freqChange, 4000,  8000],
        ["Up\nLoNull\nI", 0x00, 0x00, 0x00, loNullUpI,    0, 16383],
        ["Up\nLoNull\nQ", 0x00, 0x00, 0x00, loNullUpQ,    0, 16383],
        ["Dn\nLoNull\nI", 0x00, 0x00, 0x00, loNullDnI,    0, 16383],
        ["Dn\nLoNull\nQ", 0x00, 0x00, 0x00, loNullDnQ,    0, 16383],
        ]

    # arbitray size
    # root.geometry("500x500")

    # Loop through the main array building the sliders, labels, binding keyboard commands
    for i in range(5):
        con[i][IDX_STRINGVAR] = tk.StringVar()
        con[i][IDX_STRINGVAR].set(con[i][0])
        con[i][IDX_LABEL] = tk.Label(root,
                                    textvariable = con[i][1])
        con[i][IDX_SCALE] = tk.Scale(root,
                                    length = 300,
                                    from_ = con[i][IDX_TO],
                                    to = con[i][IDX_FROM],
                                    command = con[i][IDX_COMMAND])
        con[i][IDX_LABEL].grid(row = 1, column = i)
        con[i][IDX_SCALE].grid(row = 2, column = i)
        con[i][IDX_SCALE].bind('<Tab>', lambda e, t=con[i][IDX_SCALE]: focusNext(t))
        con[i][IDX_SCALE].bind('<Shift-Tab>', lambda e, t=con[i][IDX_SCALE]: focusPrev(t))
        con[i][IDX_SCALE].bind('<Shift-Up>', keyboard_scale_shift_increment)
        con[i][IDX_SCALE].bind('<Alt-Up>', keyboard_scale_alt_increment)
        con[i][IDX_SCALE].bind('<Shift-Down>', keyboard_scale_shift_decrment)
        con[i][IDX_SCALE].bind('<Alt-Down>', keyboard_scale_alt_decrement)

    # Set the initial focus for startup
    con[0][IDX_SCALE].focus_set()

    # Set scales to default values, could maybe read them from the hardware
    # at this point
    read_scales()
    readLockStatus()
    readShutDownState()
    readBBLoopBack()

    # Start Main loop
    root.mainloop()

