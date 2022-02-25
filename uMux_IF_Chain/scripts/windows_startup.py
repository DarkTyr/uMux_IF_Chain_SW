# -*- coding: utf-8 -*-
# import csv
import time
import tqdm

from uMux_IF_Chain.uMux_IF import uMux_IF_Rev1
from uMux_IF_Chain.base_board import base_board_rev3

# SYTNH_CONFIG_FILE = '../../HexRegisterValues.txt'




if (__name__ == '__main__'):
    COM_PORT = "COM20"

    # with open(SYTNH_CONFIG_FILE) as csvfile:
    #     data = list(csv.reader(csvfile, delimiter='\t'))
    
    tyr = base_board_rev3.Base_Board_Rev3(COM_PORT)
    tyr.get_devce_info()
    # dev_stack = tyr.spi_get_dev_stack()
    dev_stack = 0xFF
    ifb = [0x00] * dev_stack.bit_length()

    for i in range(dev_stack.bit_length()):
        ifb[i] = uMux_IF_Rev1.UMux_IF_Rev1(tyr, 0x1 << i)

    # def synth_config_from_file():
    #     print("Configuring LMX2592 from file: {}".format(SYTNH_CONFIG_FILE))
    #     for reg in data:
    #         print(reg[0])
    #         reg_val = int(reg[1], base=16)
    #         ifb0.synth_write_int(reg_val)
    #         time.sleep(0.01)

    def long_data_check(itter, nBytes, inner_itter):
        tyr.auto_print = 0
        count = 0
        for i in ifb:
            i.debug = 0
            i.data_fail = 0

        cur_time = time.monotonic()
        #main loop
        for i in tqdm.tqdm(range(itter)):
            #inner loop
            for i in ifb:
                i.data_fail += i.spi_loopback(nBytes, inner_itter)
        nxt_time = time.monotonic()
        print("Complete!")
        print("long_data_check(itter={}, nBytes={}, inner_itter={})\n".format(itter, nBytes, inner_itter)
            + "\tResults:")
        for i in ifb:
            print("\tCS={}, Fails={}".format(i._cs, i.data_fail))
        print("Statistics:\n"
            + "\t    Total Time : {} s\n".format(nxt_time-cur_time)
            + "\t               : {} min\n".format((nxt_time-cur_time)/60)
            + "\t               : {} hr\n".format((nxt_time-cur_time)/60/60)
            + "\t    Total Data : {} MB\n".format(itter*nBytes*inner_itter/1024/1024)
            + "\tOne Board data : {} MB\n".format(itter*nBytes*inner_itter/1024/1024/8))
