# from .uMux_IF_Baseboard import uMux_IF_BaseBoard

from uMux_IF_Chain.base_board import umux_if_base_board
from uMux_IF_Chain.base_board.umux_if_base_board import CommError

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
    
    def i2c_write(self, i2c_addr: int, data_array: list):
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
            return
        elif(self.auto_print > 0):
            print('\t' + self.ret_str)

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
        # convert the string into bytes
        self.ret_str_data = self.ret_str
        ret_array = self._strHextoByteArrayList(self.ret_str_data)
        return ret_array

    def spi_write(self, chip_select: int, data_array: list):
        # Check the datatype of the array and range of each element

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

