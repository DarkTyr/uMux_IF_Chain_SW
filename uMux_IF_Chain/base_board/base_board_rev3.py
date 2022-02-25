# -*- coding: utf-8 -*-
'''
Module Tyr_Serial_IF
=================================
This module is responsible for communicating with any development board
that contains a tyr command processor.
'''
# System level imports
import serial
import time

# local imports
from uMux_IF_Chain.devices import tmp275

class Base_Board_Rev3:
    def __init__(self, port=''):
        if(port == ''):
            raise IOError("There is no default serial com port, user must tell Tyr_Serial_IF what port to use")
        self.port = port    # Serial port we are supposed to communicate with
        self.com = serial.Serial(port=self.port, timeout=5, write_timeout=5) # PySerial object
        self.ret_int = 0         # Number of bytes sent to the VCP
        self.sent_str = ''       # holder for the string that was sent to the device
        self.rcvd_str = ''       # place to hold that the command was received by the firmware
        self.ret_str = ''        # Place to hold the returned string for the last command
        self.ret_str_data = ''   # Place to hold returned data so it is not overwritten
        self.auto_print = 1      # Shall I print to console?
        self._termination = '\n' # Expected string line termination
        # Firmware information
        self.fw_identity = ''
        self.fw_serial_number = ''
        self.fw_version = ''
        self.fw_description = ''
        self.fw_timestamp = ''
        self.tmp_center = tmp275.TMP275(0x48)
        self.tmp_center.link_methods(self.i2c_write, self.i2c_write_read)
        self.tmp_power_converter = tmp275.TMP275(0x49)
        self.tmp_power_converter.link_methods(self.i2c_write, self.i2c_write_read)

    def close(self):
        '''Close the serial port'''
        self.com.close()

    def open(self):
        '''Open the serial port'''
        self.com.open()

    def _byteArrayToStrHex(self, dataArray: list) -> str:
        data_str = ''
        for i in dataArray:
            data_str = data_str + hex(i)[2:].rjust(2,'0').upper()

        return data_str
    
    def _write(self, str_in: str):
        '''Write to the Serial com port'''
        #clear previous transaction status
        self.rcvd_str = ''
        if(self.auto_print > 0):
            print(str_in)
        #Append the termination character self._termination
        self.sent_str = str_in + self._termination
        #write to the serial interface and then compare the number of bytes sent
        self.ret_int = self.com.write(self.sent_str.encode())
        #check length
        if(self.ret_int != len(self.sent_str)):
            print("\tCRIT ERROR: Failed to send all of the bytes within the timeout period!!")
            return
        self.rcvd_str = self.com.read_until()[:-1].decode()
        if(self.rcvd_str != "!RCVD"):
            print("ERROR: Firmware didn't understand the sent command: \n\tsent_str: " + 
                           self.sent_str + "\n\trcvd_str: " + self.rcvd_str)
            return
        elif(self.auto_print > 1):
            print('\t' + self.rcvd_str)

    def _read(self):
        '''Read from the serial com port using read_until()'''
        temp_str = self.com.read_until().decode()
        self.ret_str = temp_str[:-1]   # Remove line termination
        if(self.auto_print > 1):
                print('\t' + self.ret_str)

    def get_devce_info(self):
        self._write("*IDN?")
        self._read()
        self.fw_identity = self.ret_str
        self._write("*SN?")
        self._read()
        self.fw_serial_number = self.ret_str
        self._write("*FW_VER?")
        self._read()
        self.fw_version = self.ret_str
        self._write("*FW_DESC?")
        self._read()
        self.fw_description = self.ret_str
        self._write("*FW_TIMESTAMP?")
        self._read()
        self.fw_timestamp = self.ret_str

        if(self.auto_print > 0):
            print(self.fw_identity)
            print('\t' + self.fw_description)
            print('\t' + self.fw_serial_number)
            print('\t' + self.fw_version)
            print('\t' + self.fw_timestamp)

    def i2c_write(self, i2c_addr: int, data_array: list):
        # Check the datatype of the array and range of each element
        for i in data_array:
            if(type(i) != int):
                raise TypeError('Type in the list must be integer')
            if(i < 0):
                raise ValueError('Numbers in list must conform to the uint8 range, ' + str(i) + ' is negative')
            if(i > 255):
                raise ValueError('Numbers in list must conform to the uint8 range, ' + str(i) + ' is above 255')

        write_size = len(data_array)
        write_size_str = hex(write_size)[2:].rjust(2,'0') # Convert int number to valid hex
        
        hex_addr = hex(i2c_addr)[2:].rjust(2,'0') # Convert int number to valid hex

        #Convert the uint8 array into a long string to be appened to the main string to write
        data_str = self._byteArrayToStrHex(data_array)

        # Construct the main string to write to the VCP device
        str_to_write = 'I2C:WRITE:' + hex_addr + "," + write_size_str + ',' + data_str # Assemble final string to be sent
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()
        if(self.ret_str != "OKAY"):
            print("\tERROR: I2C_Write Failed : " + self.ret_str)
            return
        elif(self.auto_print > 0):
            print('\t' + self.ret_str)

    def i2c_write_read(self, i2c_addr: int, nbytes_read: int, data_array: list) -> list:
        # Check the datatype of the array and range of each element
        for i in data_array:
            if(type(i) != int):
                raise TypeError('Type in the list must be integer')
            if(i < 0):
                raise ValueError('Numbers in list must conform to the uint8 range, ' + str(i) + ' is negative')
            if(i > 255):
                raise ValueError('Numbers in list must conform to the uint8 range, ' + str(i) + ' is above 255')

        write_size = len(data_array)
        write_size_str = hex(write_size)[2:].rjust(2,'0') # Convert int number to valid hex
        read_size_str = hex(nbytes_read)[2:].rjust(2,'0') # Convert int number to valid hex
        hex_addr = hex(i2c_addr)[2:].rjust(2,'0') # Convert int number to valid hex

        #Convert the uint8 array into a long string to be appened to the main string to write
        data_str = self._byteArrayToStrHex(data_array)

        # Construct the main string to write to the VCP device
        str_to_write = 'I2C:WRITE_READ:' + hex_addr + "," + write_size_str + ',' + \
                       read_size_str + ',' + data_str # Assemble final string to be sent
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()
        if(self.ret_str != "OKAY"):
            print("\tERROR: I2C_Write_Read Failed : " + self.ret_str)
            return
        elif(self.auto_print > 0):
            print('\t' + self.ret_str)

        # read the returned data
        self._read()
        if(len(self.ret_str) != (nbytes_read << 1)):
            print("\tERROR: Failed to return the correct number of bytes")
            return []

        # convert the string into bytes
        self.ret_str_data = self.ret_str
        nBytes = int((len(self.ret_str_data))/2)
        ret_array = [int(0)] * nBytes
        data = self.ret_str_data
        data2 = [data[i:i + 2] for i in range(0, len(data), 2)]
        for i in range(len(ret_array)):
                ret_array[i] = int(data2[i], base=16)
        return ret_array

    def i2c_read(self, i2c_addr: int, num_bytes: int) -> list:
        read_size_str = hex(num_bytes)[2:].rjust(2,'0') # Convert int number to valid hex
        hex_addr = hex(i2c_addr)[2:].rjust(2,'0') # Convert int number to valid hex

        # Construct the main string to write to the VCP device
        str_to_write = 'I2C:READ:' + hex_addr + "," + read_size_str # Assemble final string to be sent
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()
        if(self.ret_str != "OKAY"):
            print("\tERROR: I2C_Read Failed : " + self.ret_str)
            return []
        elif(self.auto_print > 0):
            print('\t' + self.ret_str)

        # read the returned data
        self._read()
        if(len(self.ret_str) != (num_bytes << 1)):
            print("\tERROR: Failed to return the correct number of bytes")
            return []

        # convert the string into bytes
        self.ret_str_data = self.ret_str
        nBytes = int((len(self.ret_str_data))/2)
        ret_array = [int(0)] * nBytes
        data = self.ret_str_data
        data2 = [data[i:i + 2] for i in range(0, len(data), 2)]
        for i in range(len(ret_array)):
                ret_array[i] = int(data2[i], base=16)
        return ret_array

    def i2c_scan_addr(self) -> list:
        str_to_write = 'I2C:SCAN_ADDR'
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()
        if(self.ret_str != "OKAY"):
            print("\tERROR: I2C Scan Addr Failed : " + self.ret_str)
            return []
        elif(self.auto_print > 0):
            print('\t' + self.ret_str)

        # read the returned data
        self._read()
        if(len(self.ret_str) != (128 << 1)):
            print("\tERROR: Failed to return the correct number of bytes")
            return []

        # convert the string into bytes
        self.ret_str_data = self.ret_str
        nBytes = int((len(self.ret_str_data))/2)
        temp_array = [int(0)] * nBytes
        data = self.ret_str_data
        data2 = [data[i:i + 2] for i in range(0, len(data), 2)]
        for i in range(len(temp_array)):
                temp_array[i] = int(data2[i], base=16)
        ret_array = []
        for x in temp_array:
            if(x > 0):
                ret_array.append(x)
        return ret_array
        
    def spi_write(self, chip_select: int, data_array: list):
        # Check the datatype of the array and range of each element
        for i in data_array:
            if(type(i) != int):
                raise TypeError('Type in the list must be integer')
            if(i < 0):
                raise ValueError('Numbers in list must conform to the uint8 range, ' + str(i) + ' is negative')
            if(i > 255):
                raise ValueError('Numbers in list must conform to the uint8 range, ' + str(i) + ' is above 255')

        write_size = len(data_array)
        write_size_str = hex(write_size)[2:].rjust(2,'0') # Convert int number to valid hex
        
        cs_str = hex(chip_select)[2:].rjust(2,'0') # Convert int number to valid hex

        #Convert the uint8 array into a long string to be appened to the main string to write
        data_str = self._byteArrayToStrHex(data_array)

        # Construct the main string to write to the VCP device
        str_to_write = 'SPI:WRITE:' + cs_str + "," + write_size_str + ',' + data_str # Assemble final string to be sent
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()
        if(self.ret_str != "OKAY"):
            print("\tERROR: SPI_Write Failed : " + self.ret_str)
            return
        elif(self.auto_print > 0):
            print('\t' + self.ret_str)

    def spi_write_read(self, chip_select: int, nbytes_read: int, data_array: list) -> list:
        # Check the datatype of the array and range of each element
        for i in data_array:
            if(type(i) != int):
                raise TypeError('Type in the list must be integer')
            if(i < 0):
                raise ValueError('Numbers in list must conform to the uint8 range, ' + str(i) + ' is negative')
            if(i > 255):
                raise ValueError('Numbers in list must conform to the uint8 range, ' + str(i) + ' is above 255')
        # Check the number of bytes to be write/read, we want the greater of the two
        nbytes_write = len(data_array)
        if(nbytes_write > nbytes_read):
            nbytes_int = nbytes_write
        else:
            nbytes_int = nbytes_read

        #copy data_array over to another array which is same length or longer
        data_adjust = [0x00] * nbytes_int
        for i in range(len(data_array)):
            data_adjust[i] = data_array[i]

        nbytes_str = hex(nbytes_int)[2:].rjust(2,'0') # Convert int number to valid hex
        cs_str = hex(chip_select)[2:].rjust(2,'0') # Convert int number to valid hex

        #Convert the uint8 array into a long string to be appened to the main string to write
        data_str = self._byteArrayToStrHex(data_adjust)

        # Construct the main string to write to the VCP device
        str_to_write = 'SPI:WRITE_READ:' + cs_str + "," + nbytes_str + ',' + data_str # Assemble final string to be sent
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()
        if(self.ret_str != "OKAY"):
            print("\tERROR: SPI_Write_Read Failed : " + self.ret_str)
            return
        elif(self.auto_print > 0):
            print('\t' + self.ret_str)

        # read the returned data
        self._read()
        if(len(self.ret_str) != (nbytes_int << 1)):
            print("\tERROR: Failed to return the correct number of bytes")
            return []

        # convert the string into bytes
        self.ret_str_data = self.ret_str
        nBytes = int((len(self.ret_str_data))/2)
        ret_array = [int(0)] * nBytes
        data = self.ret_str_data
        data2 = [data[i:i + 2] for i in range(0, len(data), 2)]
        for i in range(len(ret_array)):
                ret_array[i] = int(data2[i], base=16)
        return ret_array

    def spi_read(self, chip_select: int, num_bytes: int) -> list:
        nbytes_str = hex(num_bytes)[2:].rjust(2,'0') # Convert int number to valid hex
        cs_str = hex(chip_select)[2:].rjust(2,'0') # Convert int number to valid hex

        # Construct the main string to write to the VCP device
        str_to_write = 'SPI:READ:' + cs_str + "," + nbytes_str # Assemble final string to be sent
        self._write(str_to_write)

                # Read back the return value from the interface
        self._read()
        if(self.ret_str != "OKAY"):
            print("\tERROR: SPI_Read Failed : " + self.ret_str)
            return []
        elif(self.auto_print > 0):
            print('\t' + self.ret_str)

        # read the returned data
        self._read()
        if(len(self.ret_str) != (num_bytes << 1)):
            print("\tERROR: Failed to return the correct number of bytes")
            return []

        # convert the string into bytes
        self.ret_str_data = self.ret_str
        nBytes = int((len(self.ret_str_data))/2)
        ret_array = [int(0)] * nBytes
        data = self.ret_str_data
        data2 = [data[i:i + 2] for i in range(0, len(data), 2)]
        for i in range(len(ret_array)):
                ret_array[i] = int(data2[i], base=16)
        return ret_array

    def spi_get_dev_stack(self) -> int:
        str_to_write = 'SPI:DEV_STACK'
        self._write(str_to_write)
        self._read()
        if(self.ret_str != "OKAY"):
            print("\tERROR: SPI_get_dev_stack Failed : " + self.ret_str)
            return None
        # read the returned data
        self._read()
        nBytes = 4
        if(len(self.ret_str) != (nBytes << 1)):
            print("\tERROR: Failed to return the correct number of bytes")
            return None

        # convert the string into bytes
        self.ret_str_data = self.ret_str
        ret_array = [int(0)] * nBytes
        data = self.ret_str_data
        data2 = [data[i:i + 2] for i in range(0, len(data), 2)]
        for i in range(len(ret_array)):
            ret_array[i] = int(data2[i], base=16)

        return ret_array[2]

    def enable_periodic_checking(self):
        self._write("*FW_START_PER")
        self._read()

    def disable_periodic_checking(self):
        self._write("*FW_STOP_PER")
        self._read()

    def read_temp_C(self):
        center_tempereature = self.tmp_center.read_temp_C()
        power_temperature = self.tmp_power_converter.read_temp_C()
        return [center_tempereature, power_temperature]

    def read_temp_F(self):
        center_tempereature = self.tmp_center.read_temp_F()
        power_temperature = self.tmp_power_converter.read_temp_F()
        return [center_tempereature, power_temperature]