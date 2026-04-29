# from .uMux_IF_BaseBoard import uMux_IF_BaseBoard
# Global imports
import re

# Local Library Imports
from uMux_IF_Chain.base_board import umux_if_base_board
from uMux_IF_Chain.base_board.umux_if_base_board import CommError


class BB_Rev4_Pico(umux_if_base_board.uMux_IF_BaseBoard):
    def __init__(self, port=None, channel=None, url=None, doopen=True):
        self.HW_ID = "BB_Rev4_Pico"
        super().__init__(port=port, channel=channel, url=url, doopen=doopen)
        self.get_device_info()
        self.power_on_delay_s = 2

    def i2c_write(self, i2c_addr: int, data_array: list) -> bool: 
        # I2C:WRITE <devAddr>,<numBytes>,<hex bytes...>
        # All In hex
        # I2C:WRITE 20, 2, 1020\n
        write_size = len(data_array)

        write_size_str = self._byteArrayToStrHex([write_size])
        hex_addr = self._byteArrayToStrHex([i2c_addr])
        data_str = self._byteArrayToStrHex(data_array)

        str_to_write = 'I2C:WRITE:' + hex_addr + "," + write_size_str + ',' + data_str

        self._write(str_to_write)

        self._read()
        if(not(self.ret_str.startswith("!OKAY"))):
            CommError("I2C Write Failed")
        else:
            return True # Write was good

    def i2c_write_read(self, i2c_addr: int, nbytes_read: int, data_array: list) -> list:
        # I2C Write and then read with a repeated start
        # I2C:WRRD <devAddr>, <txNumBytes>, <rxNumBytes>, <txData>

        write_size = len(data_array)

        write_size_str = self._byteArrayToStrHex([write_size])
        hex_addr = self._byteArrayToStrHex([i2c_addr])
        read_size_str = self._byteArrayToStrHex([nbytes_read])
        data_str = self._byteArrayToStrHex(data_array)

        str_to_write = 'I2C:WRRD:' + hex_addr + "," + write_size_str + ',' + read_size_str + ',' + data_str

        self._write(str_to_write)

        self._read()
        if(not(self.ret_str.startswith("!OKAY"))):
            CommError("I2C Write Failed")
        
        self._read(wait_end=True, remove_term=True)
        self.ret_str_data = self.ret_str
        data_list = self._strHextoByteArrayList(self.ret_str_data)
        return data_list
    
    def i2c_write_read_nrp(self, i2c_addr: int, nbytes_read: int, data_array: list) -> list:
        # I2C Write and then read no repeated start
        # I2C:WRRD <devAddr>, <txNumBytes>, <rxNumBytes>, <txData>

        write_size = len(data_array)

        write_size_str = self._byteArrayToStrHex([write_size])
        hex_addr = self._byteArrayToStrHex([i2c_addr])
        read_size_str = self._byteArrayToStrHex([nbytes_read])
        data_str = self._byteArrayToStrHex(data_array)

        str_to_write = 'I2C:WRRD:' + hex_addr + "," + write_size_str + ',' + read_size_str + ',' + data_str

        self._write(str_to_write)

        self._read()
        if(not(self.ret_str.startswith("!OKAY"))):
            CommError("I2C Write Failed")
        
        self._read(wait_end=True, remove_term=True)
        self.ret_str_data = self.ret_str
        data_list = self._strHextoByteArrayList(self.ret_str_data)
        return data_list

    def i2c_read(self, i2c_addr: int, num_bytes: int) -> list:
        # I2C Read
        # II2C:READ <devAddr>, <rxNumBytes>

        hex_addr = self._byteArrayToStrHex([i2c_addr])
        read_size_str = self._byteArrayToStrHex([num_bytes])

        str_to_write = 'I2C:WRRD:' + hex_addr + "," + read_size_str

        self._write(str_to_write)

        self._read()
        if(not(self.ret_str.startswith("!OKAY"))):
            CommError("I2C Write Failed")
        
        self._read(wait_end=True, remove_term=True)
        self.ret_str_data = self.ret_str
        data_list = self._strHextoByteArrayList(self.ret_str_data)
        return data_list
    
    def i2c_scan_addr(self) -> list:
        str_to_write = "I2C:SCAN?"
        self._write(str_to_write)
        self._read(wait_end=True, remove_term=False)
        self.ret_str_data = self.ret_str
        addresses = [int(x, 16) for x in re.findall(r"0x[0-9A-Fa-f]+", self.ret_str_data)]
        return addresses

    def stack_pwr_get(self) -> bool:
        self._write("STACK:PWR?")
        self._read(wait_end=True, remove_term=True)
        if(self.ret_str == "ENABLED"):
            if(self.auto_print > 0):
                print("STACK is Powered ON")
            return True
        else:
            if(self.auto_print > 0):
                print("STACK is Powered OFF")
            return False

    def stack_pwr_set(self, state=True) -> bool:
        if(state==True):
            self._write("STACK:PWR ON")
        else:
            self._write("STACK:PWR OFF")
        
        self._read()
        if(self.ret_str.startswith("!OKAY")):
            return True
        else:
            CommError("stack_pwr_set didn't recieve !OKAY in time")


    def stack_write(self, chip_select: int, data_array: list) -> bool:
        # {SPI:WRITE Chip_Sel, nBytes_send, nData}\n

        write_size = len(data_array)
        write_size_str = self._byteArrayToStrHex([write_size])
        
        cs_str = self._byteArrayToStrHex([chip_select]) # Convert int number to valid hex

        #Convert the uint8 array into a long string to be appened to the main string to write
        data_str = self._byteArrayToStrHex(data_array)

        # Construct the main string to write to the VCP device
        str_to_write = 'STACK:WRITE ' + cs_str + "," + write_size_str + ',' + data_str # Assemble final string to be sent
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()

        if(self.ret_str.startswith("!OKAY")):
            return True
        else:
            # I don't think we need the below because the firmware will timeout and send an !ERR
            # which will be caught in the superclass _read command
            CommError("Never Recieved !OKAY from the device")
            return False
        
    def stack_write_read(self, chip_select: int, nbytes_read: int, data_array: list) -> list:
        # {SPI:WRITE_READ Chip_Sel, nBytes_send, nBytes_rcv, nData}\n

        write_size = len(data_array)
        write_size_str = self._byteArrayToStrHex([write_size])
        read_size_str = self._byteArrayToStrHex([nbytes_read])
        
        cs_str = self._byteArrayToStrHex([chip_select]) # Convert int number to valid hex

        #Convert the uint8 array into a long string to be appened to the main string to write
        data_str = self._byteArrayToStrHex(data_array)

        # Construct the main string to write to the VCP device
        str_to_write = f'STACK:WRITE_READ {cs_str},{write_size_str},{read_size_str},{data_str}'
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read()

        if(not(self.ret_str.startswith("!OKAY"))):
            # I don't think we need the below because the firmware will timeout and send an !ERR
            # which will be caught in the superclass _read command
            CommError("Never Recieved !OKAY from the device")
            return False
        
        # read the returned data
        self._read(wait_end=True)

        # convert the string into bytes
        self.ret_str_data = self.ret_str
        ret_array = self._strHextoByteArrayList(self.ret_str_data)
        return ret_array

    def stack_read(self, chip_select: int, num_bytes: int) -> list:
        # {SPI:READ Chip_Sel, nBytes_rcv}
        nbytes_str  = self._byteArrayToStrHex([num_bytes])
        cs_str      = self._byteArrayToStrHex([chip_select])

        # Construct the main string to write to the VCP device
        str_to_write = f'STACK:READ {cs_str},{nbytes_str}'# Assemble final string to be sent
        self._write(str_to_write)

                # Read back the return value from the interface
        self._read()
        if(not(self.ret_str.startswith("!OKAY"))):
            CommError("\tERROR: SPI_Read Failed : " + self.ret_str)

        elif(self.auto_print > 0):
            print('\t' + self.ret_str)

        # read the returned data
        self._read(wait_end=True)
        if(len(self.ret_str) != (num_bytes << 1)):
            CommError("\tERROR: Failed to return the correct number of bytes")
            return []

        # convert the string into bytes
        self.ret_str_data = self.ret_str
        ret_array = self._strHextoByteArrayList(self.ret_str_data)
        return ret_array
    
    def stack_get_dev_stack(self) -> int:
        str_to_write = "STACK:DEV_STACK?"
        self._write(str_to_write)
        # read the returned data
        self._read(wait_end=True, remove_term=True)
        nBytes = 4
        if(len(self.ret_str) != (nBytes << 1)):
            CommError("\t!ERROR: Failed to return the correct number of bytes")

        # convert the string into bytes
        self.ret_str_data = self.ret_str
        ret_array = self._strHextoByteArrayList(self.ret_str_data)
        return ret_array[0]
    
    def stack_hard_reset(self, chip_select: int): raise NotImplementedError
        ## TODO: This will require adding the functionality to the firmware, the base hooks are there. 

    def clk_reference(self, print2console=False) -> str:
        str_to_write = 'CLK:STATus?' # Assemble final string to be sent
        self._write(str_to_write)

        # Read back the return value from the interface
        self._read(wait_end=True, remove_term=False)

        if(self.auto_print > 0):
            print('\t' + self.ret_str)

        self.ret_str_data = self.ret_str

        if(print2console==True):
            print(self.ret_str)
            return ''
        else:
            return self.ret_str
    
    def set_periodic_checking_enable(self) -> bool:
        self._write("FW:PERiodic EN")
        self._read()
        if(self.ret_str.startswith("!OKAY")):
            return True
        else:
            print("Somethign Went Wrong, Never recieved !OKAY")
            return

    def set_periodic_checking_disable(self) -> bool:
        self._write("FW:PERiodic DIS")
        self._read()
        if(self.ret_str.startswith("!OKAY")):
            return True
        else:
            print("Somethign Went Wrong, Never recieved !OKAY")
            return False

    def get_periodic_checking(self) -> bool:
        self.write("FW:PERiodic ?")
        state = self._read()    # Read the state
        self._read()            # Read the !OKAY
        if(self.ret_str.startswith("!OKAY")):
            if(state.startswith("ENABLED")):
                return True
            else:
                return False
        else:
            print("Somethign Went Wrong, Never recieved !OKAY")
            return False

    def read_temp_C(self, print2console=False) -> list:
        self._write("FW:TEMPerature?")
        self._read(wait_end=True, remove_term=True)

        temps = re.findall(r"[-+]?\d+\.\d+", self.ret_str)
        si_temp, smps_temp = map(float, temps)

        if(print2console):
            print(f"CLK IC Temp = {si_temp:.2f} °C  :  Power Supply Temp = {smps_temp:.2f} °C ")

        return [si_temp, smps_temp]

    def read_temp_F(self, print2console=False) -> list:
        [si_temp, smps_temp] = self.read_temp_C(False)
        si_temp = si_temp * 9/5 + 32
        smps_temp = smps_temp * 9/5 + 32

        if(print2console):
            print(f"CLK IC Temp = {si_temp:.2f} °F  :  Power Supply Temp = {smps_temp:.2f} °F ")

        return [si_temp, smps_temp]

    ##########################################################
    ## TODO: Add file handling methods here to list, write, read, the files on the internal file system
    ##########################################################

    ##########################################################
    ## TODO: Add Fan PWM control methods
    ##########################################################

    ##########################################################
    ## TODO: Add methods to read ADCs and power use
    ##########################################################

    ##########################################################
    ## TODO: Add methods for Ethernet status
    ##########################################################