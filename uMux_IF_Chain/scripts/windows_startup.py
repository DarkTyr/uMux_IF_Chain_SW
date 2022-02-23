# -*- coding: utf-8 -*-
import csv
import time

from uMux_IF_Chain.uMux_IF import uMux_IF_Rev1
from uMux_IF_Chain.base_board import base_board_rev3

SYTNH_CONFIG_FILE = '../../HexRegisterValues.txt'




if (__name__ == '__main__'):
    COM_PORT = "COM20"

    with open(SYTNH_CONFIG_FILE) as csvfile:
        data = list(csv.reader(csvfile, delimiter='\t'))
    
    tyr = base_board_rev3.Base_Board_Rev3(COM_PORT)
    tyr.get_devce_info()
    ifb = uMux_IF_Rev1.UMux_IF_Rev1(tyr, 0x1)

    def synth_config_from_file():
        print("Configuring LMX2592 from file: {}".format(SYTNH_CONFIG_FILE))
        for reg in data:
            print(reg[0])
            reg_val = int(reg[1], base=16)
            ifb.synth_write_int(reg_val)
            time.sleep(0.01)
