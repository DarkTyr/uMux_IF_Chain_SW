# -*- coding: utf-8 -*-
'''
Class to read temperature from a Sensirion STS31-DIS temperature sensor

This chip requires an i2c class that can write two bytes before reading. 
This is typically done with i2c mem write_read methods.

TODO: This is not an all inclusive class yet. It only impliments what is needed
for the uMux IF Rev2 board.

TODO: Measurement Commands
TODO: One shot measurements w/wo Clock Stretching
TODO: Continuous measurements
TODO: Chip soft reset
TODO: Readout of the status register
TODO: Heater Control
TODO: CRC checking for readout data

'''

class STS31_DIS:
    def __init__(self, i2c_addr=0x4A):
        # Address check, it can only be 0x4A or 0x4B
        if i2c_addr != 0x4A and i2c_addr != 0x4B:
            raise ValueError("Invalid I2C address. Must be 0x4A or 0x4B.")
        self.i2c_addr = i2c_addr    # 7 bit i2c address
        self._write = None
        self._write_read = None

    def link_methods(self, write, write_read):
        raise NotImplementedError("Configuration not implemented for STS31-DIS.")
        # self._write = write
        # self._write_read = write_read

    def config_device(self):
        raise NotImplementedError("Configuration not implemented for STS31-DIS.")

    def read_temp_C(self):
        raise NotImplementedError("Configuration not implemented for STS31-DIS.")
        # val = self._write_read(self.i2c_addr, 0x2, [0x00])
        # degrees_C = self.convert_int2temp_C(val)
        # return degrees_C

    def read_temp_F(self):
        raise NotImplementedError("Configuration not implemented for STS31-DIS.")
        # temp = self.read_temp_C()
        # temp = (temp * 1.8 + 32)
        # return temp

    def convert_int2temp_C(self, data):
        # Convert 16 bit int to float degrees C
        if(type(data) == int):
            val_float = float(data)
        elif(type(data) == list):
            val_float = float((data[0] << 8) | (data[1]))  # Map bits
        else:
            # Should work with numpy arrays as well
            val_float = float((data[0] << 8) | (data[1]))  # Map bits
        
        degrees_C = (val_float) / (2**16 - 1) * 175.0 - 45.0
        return degrees_C

    def convert_int2temp_F(self, data):
        degrees_C = self.convert_int2temp_C(data)
        degrees_F = degrees_C * 1.8 + 32
        return degrees_F
    
    def convert_temp_C2int(self, temp_C):
        # Convert temperature in C to 16 bit int
        val_float = (temp_C + 45.0) / 175.0 * (2**16 - 1)
        return int(val_float) & 0xFFFF
    
    def convert_temp_F2int(self, temp_F):
        # Convert temperature in F to 16 bit int
        degrees_C = (temp_F - 32) / 1.8
        return self.convert_temp2int(degrees_C)