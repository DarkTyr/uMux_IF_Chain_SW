# from .uMux_IF_Baseboard import uMux_IF_BaseBoard
import uMux_IF_BaseBoard

class BB_Rev3_F732(uMux_IF_BaseBoard.uMux_IF_BaseBoard):
    def __init__(self, port=None, channel=None, url=None, doopen=True):
        self.HW_ID = "BB_Rev3_F732"
        super().__init__(port=port, channel=channel, url=url, doopen=doopen)
        
    def spi_write(self, chip_select: int, data_array: list):
        # Check the datatype of the array and range of each element

        write_size = list(len(data_array))
        write_size_str = self._byteArrayToStrHex(write_size)
        
        cs_str = self._byteArrayToStrHex([chip_select]) # Convert int number to valid hex

        #Convert the uint8 array into a long string to be appened to the main string to write
        data_str = self._byteArrayToStrHex(data_array)

        # Construct the main string to write to the VCP device
        str_to_write = 'SPI:WRITE ' + cs_str + "," + write_size_str + ',' + data_str # Assemble final string to be sent
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()
        if(self.ret_str != "OKAY"):
            print("\tERROR: SPI_Write Failed : " + self.ret_str)
            return
        elif(self.auto_print > 0):
            print('\t' + self.ret_str)

    def clk_reference(self) -> str:
        str_to_write = 'I2C:SI_LOCK?' # Assemble final string to be sent
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()

        if(self.auto_print > 0):
            print('\t' + self.ret_str)
        return self.ret_str