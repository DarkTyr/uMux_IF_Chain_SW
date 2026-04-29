# -*- coding: utf-8 -*-
from uMux_IF_Chain import channels

class CommError(Exception):
    pass

class uMux_IF_BaseBoard:
    def __init__(self, port = None, channel = None, url = None, doopen = True):
        self._port = port
        self._url = url
        self.ret_int = 0         # Number of bytes sent to the VCP
        self.sent_str = ''       # holder for the string that was sent to the device
        self.rcvd_str = ''       # place to hold that the command was received by the firmware
        self.ret_str = ''        # Place to hold the returned string for the last command
        self.ret_str_data = ''   # Place to hold returned data so it is not overwritten
        self.auto_print = 0      # Shall I print to console?
        self._termination = '\n' # Expected string line termination
        self._timeout = 5        # Base timeout in seconds

        if (channel != None):
            self.com = channel
        elif (port != None):
            self.com = channels.serialchan.serialchan(port=port, timeout=self._timeout)
        elif (url != None):
            self.com = channels.fromurl(url)

        if doopen: 
            self.open()

    def open(self):
        self.com.open()

    def close(self):
        self.com.close()

    def _byteArrayToStrHex(self, dataArray: list) -> str:
        return bytes(dataArray).hex().upper()

    def _strHextoByteArrayList(self, stringData: str) -> list:
        return list(bytes.fromhex(stringData))
        
    def _write(self, str_in: str):
        '''Write to the Serial com port'''
        #clear previous transaction status
        self.rcvd_str = ''

        #Append the termination character self._termination
        self.sent_str = str_in + self._termination

        #write to the serial interface and then compare the number of bytes sent
        if(self.auto_print > 0):
            print(self.sent_str.encode())
        self.ret_int = self.com.fd.write(self.sent_str.encode())

        #check length
        if(self.ret_int != len(self.sent_str)):
            CommError("\tCRIT ERROR: Failed to send all of the bytes within the timeout period!!")

        ## If the command is a valid command, the device will send back "!RCVD"
        self.rcvd_str = self._read_line() # _read_line handles the auto_print
        if(self.rcvd_str != "!RCVD"):
            CommError("ERROR: Firmware didn't understand the sent command: \n\tsent_str: " + 
                           self.sent_str + "\n\trcvd_str: " + self.rcvd_str)
            return

    def _read_line(self, remove_term: bool = True):
        """Read exactly one line with auto EOL detection and optional removal of line terminations"""

        if(self.auto_print > 2):
            print(f"self._read_line(remove_term={remove_term})")

        buf = bytearray()

        while True:
            ch = self.com.fd.read(1)
            if not ch:
                break  # timeout or disconnect

            buf += ch

            # Detect termination
            if ch in (b'\n', b'\r'):
                # Handle CRLF
                if ch == b'\r':
                    # Read another ot get the \n
                    nxt = self.com.fd.read(1)
                    # Being as the interface doens't throw an exception if it times out.
                    # This is the only way to determine if it timed out, unless we run
                    # our own timer. 
                    if(nxt == b''):
                        CommError("Communication Timed Out")
                    if nxt == b'\n':
                        buf += nxt
                break

        if self.auto_print > 1:
            print('\t', buf)

        raw = buf.decode(errors='replace')

        if remove_term:
            raw = raw.rstrip('\r\n')

        if(self.auto_print > 2):
            print(f"_read_line() raw = {raw}")

        return raw

    def _read(self, wait_end: bool = False, remove_term: bool = True):
        """Read either a single line or a multi-line block terminated by !END."""

        if(self.auto_print > 2):
            print(f"self._read(wait_end={wait_end}, remove_term={remove_term})")

        if not wait_end:
            # Simple single-line read
            self.ret_str = self._read_line(remove_term=remove_term)
            if self.ret_str.startswith("!ERR"):
                raise CommError(self.ret_str)
            return self.ret_str

        # Multi-line mode
        lines = ""
        while True:
            line = self._read_line(remove_term=remove_term)
            if(self.auto_print > 2):
                print(f"_read() line = {line}")

            if self.ret_str.startswith("!ERR"):
                raise CommError(self.ret_str)
            
            if(line.startswith("!END")):
                break
            lines += line
        
        if(self.auto_print > 2):
            print(f"_read() lines = {lines}")

        self.ret_str = lines
        return self.ret_str

    def get_device_info(self, print2console=False):
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

        if((self.auto_print > 0) or print2console):
            print(self.fw_identity)
            print('\t' + self.fw_description)
            print('\t' + self.fw_serial_number)
            print('\t' + self.fw_version)
            print('\t' + self.fw_timestamp)
        
    def i2c_write(self, i2c_addr: int, data_array: list) -> bool: raise NotImplementedError
    def i2c_write_read(self, i2c_addr: int, nbytes_read: int, data_array: list) -> list: raise NotImplementedError
    def i2c_read(self, i2c_addr: int, num_bytes: int) -> list: raise NotImplementedError
    def i2c_scan_addr(self) -> list: raise NotImplementedError

    def clk_reference(self, print2console) -> str: raise NotImplementedError

    def stack_write(self, chip_select: int, data_array: list) -> bool: raise NotImplementedError
    def stack_write_read(self, chip_select: int, nbytes_read: int, data_array: list) -> list: raise NotImplementedError
    def stack_read(self, chip_select: int, num_bytes: int) -> list: raise NotImplementedError
    def stack_get_dev_stack(self) -> int: raise NotImplementedError
    def stack_hard_reset(self, chip_select: int): raise NotImplementedError

    def set_periodic_checking_enable(self): raise NotImplementedError
    def set_periodic_checking_disable(self): raise NotImplementedError
    def get_periodic_checking(self):  raise NotImplementedError
    def read_temp_C(self, print2console): raise NotImplementedError
    def read_temp_F(self, print2console): raise NotImplementedError


from uMux_IF_Chain.base_board import bb_rev3_f732
from uMux_IF_Chain.base_board import bb_rev4_pico

def open_uMux_IF_BaseBoard(port = None, channel = None, url = None, doopen = True):
    base = uMux_IF_BaseBoard(port=port, channel=channel, url=url, doopen=doopen)
    base.get_device_info()
    base.close()

    if "BB_Rev4_Pico" in base.fw_identity:
        return bb_rev4_pico.BB_Rev4_Pico(port=port, channel=channel, url=url, doopen=doopen)

    if "BB_Rev3_F732" in base.fw_identity:
        return bb_rev3_f732.BB_Rev3_F732(port=port, channel=channel, url=url, doopen=doopen)

    raise RuntimeError(f"Unknown hardware type: {base.fw_identity}")

