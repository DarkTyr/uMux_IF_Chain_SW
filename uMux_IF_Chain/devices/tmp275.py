# -*- coding: utf-8 -*-
'''
Module Tyr_Serial_IF
=================================
This module is responsible for communicating with any development board
that contains a tyr command processor.
'''

class TMP275:
    def __init__(self, i2c_addr=0x24):
        self.i2c_addr = i2c_addr    # 7 bit i2c address
        self.write = None
        self.write_read = None

    def link_methods(self, write, write_read):
        self.write = write
        self.write_read = write_read

    def config_device(self):
        config_byte = 0x60
        self.write(self.i2c_addr, [0x01, config_byte])

    def read_temp_C(self):
        val = self.write_read(self.i2c_addr, 0x2, [0x00])
        val_float = (val[0] << 4) | (val[1] >> 4)   # Map bits
        val_float *= 0.0625     # Scale to Degree C
        return val_float

    def read_temp_F(self):
        temp = self.read_temp_C()
        temp = (temp * 1.8 + 32)
        return temp

    def convert_int2temp_C(self, data):
        val_float = (data[0] << 4) | (data[1] >> 4)   # Map bits
        val_float *= 0.0625     # Scale to Degree C
        return val_float

    def convert_int2temp_F(self, data):
        val_float = self.convert_int2temp_C(data)
        val_float = val_float * 1.8 + 32
        return val_float
    
