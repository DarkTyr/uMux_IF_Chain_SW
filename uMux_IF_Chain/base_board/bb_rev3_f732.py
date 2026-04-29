# from .uMux_IF_Baseboard import uMux_IF_BaseBoard

from uMux_IF_Chain.base_board import umux_if_base_board

class BB_Rev3_F732(umux_if_base_board.uMux_IF_BaseBoard):
    def __init__(self, port=None, channel=None, url=None, doopen=True):
        self.HW_ID = "BB_Rev3_F732"
        super().__init__(port=port, channel=channel, url=url, doopen=doopen)

    def clk_reference(self) -> str:
        str_to_write = 'I2C:SI_LOCK?' # Assemble final string to be sent
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()

        if(self.auto_print > 0):
            print('\t' + self.ret_str)
        return self.ret_str
    
    def i2c_write(self, i2c_addr: int, data_array: list) -> bool:
        write_size_str = self._byteArrayToStrHex([len(data_array)]) # Convert int number to valid hex
        
        hex_addr = self._byteArrayToStrHex([i2c_addr]) # Convert int number to valid hex

        #Convert the uint8 array into a long string to be appened to the main string to write
        data_str = self._byteArrayToStrHex(data_array)

        # Construct the main string to write to the VCP device
        str_to_write = f'I2C:WRITE:{hex_addr},{write_size_str},{data_str}'
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()
        if(self.ret_str != "OKAY"):
            print("\tERROR: I2C_Write Failed : " + self.ret_str)
            return False
        elif(self.auto_print > 0):
            print('\t' + self.ret_str)
        
        return True

    def i2c_write_read(self, i2c_addr: int, nbytes_read: int, data_array: list) -> list:
        write_size_str = self._byteArrayToStrHex([len(data_array)]) # Convert int number to valid hex
        read_size_str = self._byteArrayToStrHex([nbytes_read]) # Convert int number to valid hex
        hex_addr =self._byteArrayToStrHex([i2c_addr]) # Convert int number to valid hex

        #Convert the uint8 array into a long string to be appened to the main string to write
        data_str = self._byteArrayToStrHex(data_array)

        # Construct the main string to write to the VCP device
        # str_to_write = 'I2C:WRITE_READ:' + hex_addr + "," + write_size_str + ',' + \
        #                read_size_str + ',' + data_str # Assemble final string to be sent
        str_to_write = f"I2C:WRITE_READ:{hex_addr},{write_size_str},{read_size_str},{data_str}"
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
        ret_array = self._strHextoByteArrayList(self.ret_str_data)
        return ret_array

    def i2c_read(self, i2c_addr: int, num_bytes: int) -> list:
        read_size_str = self._byteArrayToStrHex([num_bytes]) # Convert int number to valid hex
        hex_addr =self._byteArrayToStrHex([i2c_addr]) # Convert int number to valid hex

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
        ret_array = self._strHextoByteArrayList(self.ret_str_data)
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
    
    def stack_write(self, chip_select: int, data_array: list):
        write_size = len(data_array)
        write_size_str = self._byteArrayToStrHex([write_size])
        
        cs_str = self._byteArrayToStrHex([chip_select]) # Convert int number to valid hex

        #Convert the uint8 array into a long string to be appened to the main string to write
        data_str = self._byteArrayToStrHex(data_array)

        # Construct the main string to write to the VCP device
        str_to_write = f"SPI:WRITE {cs_str},{write_size_str},{data_str}"
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()
        if(self.ret_str != "OKAY"):
            print("\tERROR: SPI_Write Failed : " + self.ret_str)
            return
        elif(self.auto_print > 0):
            print('\t' + self.ret_str)

    def stack_write_read(self, chip_select: int, nbytes_read: int, data_array: list) -> list:
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

        nbytes_str = self._byteArrayToStrHex([nbytes_int]) # Convert int number to valid hex
        cs_str = self._byteArrayToStrHex([chip_select]) # Convert int number to valid hex

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
        ret_array = self._strHextoByteArrayList(self.ret_str_data)
        return ret_array

    def stack_read(self, chip_select: int, num_bytes: int) -> list:
        nbytes_str = self._byteArrayToStrHex([num_bytes])# Convert int number to valid hex
        cs_str = self._byteArrayToStrHex([chip_select]) # Convert int number to valid hex

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
        ret_array = self._strHextoByteArrayList(self.ret_str_data)
        return ret_array
    
    def stack_get_dev_stack(self) -> int:
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
        ret_array = self._strHextoByteArrayList(self.ret_str_data)

        return ret_array[0]
    
    def stack_hard_reset(self, chip_select: int):
        cs_str = hex(chip_select)[2:].rjust(2,'0') # Convert int number to valid hex

        # Construct the main string to write to the VCP device
        str_to_write = 'SPI:HARD_RST:' + cs_str # Assemble final string to be sent
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()
        if(self.ret_str != "OKAY"):
            print("\tERROR: SPI Hard Reset Failed : " + self.ret_str)
            return
        elif(self.auto_print > 0):
            print('\t' + self.ret_str)

    def set_periodic_checking_enable(self):
        self._write("*FW_START_PER")
        self._read()

    def set_periodic_checking_disable(self):
        self._write("*FW_STOP_PER")
        self._read()

    def read_temp_C(self, print2console=False):
        center_tempereature = self.tmp_center.read_temp_C()
        power_temperature = self.tmp_power_converter.read_temp_C()

        if(print2console):
                    print(f"Center Temp = {center_tempereature:.2f} °C  :  Power Supply Temp = {power_temperature:.2f} °C ")

        return [center_tempereature, power_temperature]

    def read_temp_F(self, print2console=False):
        center_tempereature = self.tmp_center.read_temp_F()
        power_temperature = self.tmp_power_converter.read_temp_F()

        if(print2console):
            print(f"Center Temp = {center_tempereature:.2f} °F  :  Power Supply Temp = {power_temperature:.2f} °F ")

        return [center_tempereature, power_temperature]
    