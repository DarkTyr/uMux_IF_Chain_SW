# -*- coding: utf-8 -*-

# Global imports
import re
import time
#   For file uploading and downloading
import base64
import os

# Local Library Imports
from uMux_IF_Chain.base_board import umux_if_base_board
from uMux_IF_Chain.base_board.umux_if_base_board import CommError


class BB_Rev4_Pico(umux_if_base_board.uMux_IF_BaseBoard):
    def __init__(self, port=None, channel=None, url=None, doopen=True):
        self.HW_ID = "BB_Rev4_Pico"
        super().__init__(port=port, channel=channel, url=url, doopen=doopen)
        # self.get_device_info()
        self.power_on_delay_s = 3   # Required time for the IF_Boards to boot. 

    def i2c_write(self, i2c_addr: int, data_array: list) -> bool: 
        # I2C:WRITE <devAddr>,<numBytes>,<hex bytes...>
        # All In hex
        # I2C:WRITE 20, 2, 1020\n
        write_size = len(data_array)

        write_size_str = self._byteArrayToStrHex([write_size])
        hex_addr = self._byteArrayToStrHex([i2c_addr])
        data_str = self._byteArrayToStrHex(data_array)

        str_to_write = 'I2C:WRITE ' + hex_addr + "," + write_size_str + ',' + data_str

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

        str_to_write = 'I2C:WRRD ' + hex_addr + "," + write_size_str + ',' + read_size_str + ',' + data_str

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

        str_to_write = 'I2C:WRRD_NRP' + hex_addr + "," + write_size_str + ',' + read_size_str + ',' + data_str

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

        str_to_write = 'I2C:READ' + hex_addr + "," + read_size_str

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
        str_to_write = f'STACK:WRRD {cs_str},{write_size_str},{read_size_str},{data_str}'
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
    
    def stack_hard_reset(self, chip_select: int):
        cs_str  = self._byteArrayToStrHex([chip_select])
        self._write("STACK:HARD_RST {cs_str}")
        
        self._read()
        if(not(self.ret_str.startswith("!OKAY"))):
            CommError("\tERROR: SPI_Read Failed : " + self.ret_str)
        return

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
    
    def clk_read(self, addr_page:int) -> int:
        '''
        addr_page should be a 16 bit number that contains the page and register address (each 1 byte)
        '''
        addr = int(addr_page)
        self._write(f"CLK:READ {addr}")
        self._read(wait_end=True)
        return int(self._ret_str, 16)
    
    def clk_write(self, addr_page, val)-> bool:
        '''
        addr_page should be a 16 bit number that contains the page and register address (each 1 byte)
        '''
        addr = int(addr_page)
        value = int(val)
        self._write(f"CLK:WRITE {addr}, {value}")
        self._read()  # Should be !OKAY
        if(self.ret_str.startswith("!OKAY")):
            return True
        else:
            return False  # Though it should never get here

    def clk_parse_and_program(self, filename):
        '''
        This method reads in an exported file from ClockBuilder Pro (CBPro) from Skyworks.
        The configuration will need to be exported as a "Register File" with the summary header
        and include pre- and post-write control register writes checked. The radial for CSV
        should be selected as well. This is intended to allow the changing of the config via software
        and was used initialy to test the interfaces before file uploading existed.
        - The Si5344 must have an i2c address of 0x69  (Which means bits {6,5,3} are high, else low)
        - the project file is with the PCB Altium folder
        '''
        cnt = 0
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()

                # Skip blank lines and comments
                if not line or line.startswith("#"):
                    continue

                # Skip CSV header
                if line.lower().startswith("address"):
                    continue

                # Expect lines like: 0x0B24,0xC0
                if "," not in line:
                    continue

                addr_str, val_str = line.split(",", 1)
                addr_str = addr_str.strip()
                val_str = val_str.strip()

                # Validate hex format
                if not (addr_str.startswith("0x") and val_str.startswith("0x")):
                    continue

                # Convert
                addr = int(addr_str, 16) & 0xFFFF
                val  = int(val_str, 16) & 0xFF

                # Format SCPI command

                self.clk_write(addr, val)

                cnt += 1
                if(cnt == 3):
                    # This is needed for the device to fully reset into a known initial state
                    time.sleep(0.75)
            # For
        # With
        print(f"BB_Rev4_Pico.clk_parse_and_program({filename}) complete")
        print(f"    Total registers written: {cnt}")

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
        self._write("FW:PERiodic ?")
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
    def file_list(self)-> list:
        '''
        Method that returns a list of tuples. Each tuple is the filename and then the size in bytes.
        '''
        self._write("FILE:LIST?")
        self._read(wait_end=True, remove_term=False)

        result = []
        for line in self.ret_str.strip().splitlines():
            if not line:
                continue
            name, size = line.split(",")
            result.append((name, int(size)))
        
        if(self.auto_print):
            print(result)

        return result

    def file_upload(self, local_name:str, remote_name:str) -> bool:
        '''
        Sends a file to the device file system from the host communicating system.
        Says name, but can be paths for either.  
        '''
        size_bytes = os.path.getsize(local_name)
        self._write(f"FILE:WRITE {remote_name},{size_bytes}")
        self._read()  # Should return okay, but we are not going to check.

        with open(local_name, "rb") as f:
            while True:
                chunk = f.read(64)
                if not chunk:
                    break
                b64 = base64.b64encode(chunk).decode()
                self._write(f"FILE:DATA {b64}")
                self._read(wait_end=False)
            # While
        # with

        self._write(f"FILE:END")
        self._read(wait_end=True)
        
        if(self.ret_str.startswith("!OKAY")):
            return True
        else:
            return False

    def file_download(self, remote_name:str, local_name:str) -> bool:
        '''
        Downloads a file from the device to the host communicating system
        '''
        self._write(f"FILE:READ? {remote_name}")
        self._read(wait_end=False)

        ret = self.ret_str.split(' : ')

        if(ret[0].startswith("!SIZE")):
            size_bytes = int(ret[1])
            print(f"  File Size in Bytes : {size_bytes}")
        else:
            raise CommError(f"Unexpected Returned String : {self.ret_str}")

        received_bytes = 0

        with open(local_name, "wb")as out:
            while True:
                line = self._read()
                if(line.startswith("!END")):
                    break

                chunk = base64.b64decode(line)
                out.write(chunk)
                received_bytes += len(chunk)
            # While
        # With

        print(f"Downloaded {received_bytes}/{size_bytes} Bytes")

        if(received_bytes == size_bytes):
            return True
        else:
            return False
        
    def file_remove(self, remote_name)-> bool:
        '''
        Deletes a file that matches the provided name. 
        remote_name can be a file path on the device. 
        '''
        self._write(f"FILE:RM {remote_name}")
        self._read(wait_end=True)
        if(self.ret_str.startswith("!OKAY")):
            return True
        else:
            return False

    def file_space(self)-> str:
        '''
        The device returns a series of terminated strings showing Total, Used, Free
        in bytes.
        '''
        self._write(f"FILE:SPACE?")
        self._read(wait_end=True, remove_term=False)
        return self.ret_str


    def fan_pwm_get(self):
        self._write("FW:FAN:PWM?")
        self._read(wait_end=True, remove_term=True)
        pwm = int(self.ret_str.rsplit("=")[1])
        return pwm
    

    def fan_pwm_set(self, pwm_percentage):
        pwm_max = 255
        pwm = int(pwm_percentage/100 * pwm_max) & 0xFF
        self._write(f"FW:FAN:PWM {pwm}")
        self._read(wait_end=True)
        

    def adc_read_keys(self, print2console=False):
        self._write("FW:ADC_KEYS?")
        self._read(wait_end=True, remove_term=False)

        result = {}

        for line in self.ret_str.splitlines():
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(":")]
            ch = int(parts[0])
            name = parts[1]
            unit = parts[2]
            result[ch] = {"name": name, "unit": unit}
        if(print2console):
            print(result)

        return result

    def adc_read_keys_regex(self, print2console=False):
        self._write("FW:ADC_KEYS?")
        self._read(wait_end=True, remove_term=False)
    
        pattern = r'(\d+)\s*:\s*([^\:]+?)\s*:\s*([A-Za-z]+)'
        result = {
            int(ch): {"name": name.strip(), "unit": unit}
            for ch, name, unit in re.findall(pattern, self.ret_str)
        }

        if(print2console):
            print(result)

        return result

    def adc_read_all(self):
        self._write("FW:ADC_READ_ALL?")
        self._read(wait_end=True, remove_term=False)
        return self.ret_str

    def adc_read_hr(self, print2console=True):
        self._write("FW:ADC_READ_HR?")
        self._read(wait_end=True, remove_term=False)

        if(print2console):
            print(self.ret_str)

    def adc_read_power_hr(self, print2console=True):
        self._write("FW:ADC_PWR_HR?")
        self._read(wait_end=True, remove_term=False)

        if(print2console):
            print(self.ret_str)


    ##########################################################
    ## TODO: Add methods for Ethernet status
    ##########################################################