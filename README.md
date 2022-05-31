# uMux_IF_Chain_SW
Microwave Multiplexer Intermediate Frequency Conversion Chain Software

## Setup for Development
https://setuptools.pypa.io/en/latest/userguide/development_mode.html

## Installation 
One can use pip to install the package. Adding "-e" makes it a link to the source files rather than copying them to the installation directory. This allows them to be edited easily. 

Run below line in terminal at the folder level with setup.py
```
pip install -e .
```

# Simple Script to run
- navigate to "uMux_IF_Chain_SW/uMux_IF_Chain/scripts"
- start iPython
- in iPython, run windows_startup.py /dev/ttyACM0

When that runs you shoud see output listing Board IDN, Device Serial number, firmware version, and FW timestamp. There will be another printout "DEV_STACK : n" where n is a hex number. N is a chip select mapping for the installed number of IF boards. 0x1 means that one board was detected. 0x3 means two boards, 0x7 is three boards. 

- type "ifb" and hit enter. This should be a list of classes matching the number of IF boards installed.

When starting from a powered down state you must call the synth_init() method for each IF board (ifb is the list)

- ifb[0].synth_init()

At power up, the base band loopback is enabled. This loops the DAC output around to the ADCs internally with no modifications except PCB and mux losses. 

to enable the loopback
- ifb[0].base_band_loop_back_enable()
to disable the loopback
- ifb[0].base_band_loop_back_disable()

After intialization of the synthesizer, the user can set the frequency by calling:
- ifb[0].synth_set_Frequency_MHz(4500)
Where 4500 is the frequency is megahertz. There is a frequency resolution of 200kHz, this could be changed later on if need be.
The set frequency method returns the actual frequency that was calculated. 

if you don't want to run the script, a user can instantiate the base_board class and IF board classes from anywhere (assuming correct conda environment). 

'''
from uMux_IF_Chain.base_board import base_board_rev3
bb = base_board_rev3.Base_Board_Rev3(port="/dev/ttyACM0")
# Determine what IF_Boards Rev1 are present
dev_stack = bb.spi_get_dev_stack()
n_ifb = dev_stack.bit_length()
ifb = [0x00] * n_ifb

# Instantiate classes for the IF_Boards Rev1
for i in range(dev_stack.bit_length()):
    ifb[i] = uMux_IF_Rev1.UMux_IF_Rev1(bb, 0x1 << i)

for i in ifb:
    i.synth_init()
    i.base_band_loop_back_disable()

ifb[0].synth_set_Frequency_MHz(4500)
ifb[1].synth_Set_Frequency_MHz(5500)
ifb[2].synth_set_Frequency_MHz(6500)
ifb[3].synth_set_Frequency_MHz(7500)

'''
