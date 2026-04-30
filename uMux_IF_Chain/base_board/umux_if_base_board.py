# -*- coding: utf-8 -*-
from uMux_IF_Chain import channels
from uMux_IF_Chain.channels import serialchan

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
            # self.com = channels.serialchan.serialchan(port=port, timeout=self._timeout)
            self.com = channels.serialchan.SerialChan(port=port, timeout=self._timeout)
        elif (url != None):
            self.com = channels.fromurl(url, defaultport=3032, defaultparams=dict(timeout=self._timeout, buffering=0))

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
        """Write to the Serial com port"""

        # Clear previous transaction status
        self.rcvd_str = ''

        # Append termination
        self.sent_str = str_in + self._termination
        data = self.sent_str.encode()

        if(self.auto_print > 1):
            print(data)

        # Write to serial
        bytes_written = self.com.fd.write(data)
        self.com.fd.flush()

        # Validate full write
        if(bytes_written != len(data)):
            raise CommError(
                f"CRIT ERROR: Incomplete write "
                f"({bytes_written}/{len(data)} bytes sent)"
            )

        try:
            rcvd = self._read()
        except CommError as e:
            raise CommError(f"Write succeeded but read failed: {self.sent_str}") from e
        
        if(rcvd != "!RCVD"):
            raise CommError(
                "Firmware didn't understand command:\n"
                f"  sent: {self.sent_str}\n"
                f"  recv: {rcvd}"
            )

        self.rcvd_str = rcvd
        return rcvd

    def _read_line(self, remove_term: bool = True):
        if self.auto_print > 2:
            print(f"umux_if_base_board._read_line(remove_term={remove_term})")

        buf = bytearray()

        while True:
            ch = self.com.fd.read(1)

            if not ch:
                raise CommError("Communication Timed Out")

            buf += ch

            if(ch in (b'\n', b'\r')):
                if(ch == b'\r'):
                    nxt = self.com.fd.read(1)
                    if(not nxt):
                        raise CommError("Communication Timed Out")
                    if(nxt == b'\n'):
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
        if(self.auto_print > 2):
            print(f"umux_if_base_board._read(wait_end={wait_end}, remove_term={remove_term})")

        if(not wait_end):
            line = self._read_line(remove_term=remove_term)

            if line.startswith(("!ERR", "ERROR")):
                raise CommError(line)

            self.ret_str = line
            return line

        # Multi-line mode
        lines = []

        while True:
            line = self._read_line(remove_term=remove_term)

            if(self.auto_print > 2):
                print(f"_read() line = {line}")

            if line.startswith(("!ERR", "ERROR")):
                raise CommError(line)

            if(line.startswith("!END")):
                break

            lines.append(line)

        result = "".join(lines)

        if(self.auto_print > 2):
            print(f"_read() lines = {result}")

        self.ret_str = result
        return result

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
        
    # Method prototypes for consistency accross multiple boards
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

    def get_periodic_checking(self): raise NotImplementedError

    def read_temp_C(self, print2console): raise NotImplementedError

    def read_temp_F(self, print2console): raise NotImplementedError



# Local imports for the open_uMux_IF_BaseBoard() function. 
from uMux_IF_Chain.base_board import bb_rev3_f732
from uMux_IF_Chain.base_board import bb_rev4_pico

# Function to determine which booard is present and map it to which class to 
# instantiate. 
def open_uMux_IF_BaseBoard(port=None, channel=None, url=None, doopen=True, hw_id=None):
    # We have to open the connection and talk to the board to get the firmware identity.
    if(hw_id==None):
        base = uMux_IF_BaseBoard(port=port, channel=channel, url=url, doopen=True)
        base.get_device_info()
        base.close()
        id = base.fw_identity
    else:
        id = hw_id
    
    if "BB_Rev4_Pico" in id:
        return bb_rev4_pico.BB_Rev4_Pico(port=port, channel=channel, url=url, doopen=doopen)

    if "BB_Rev3_F732" in id:
        return bb_rev3_f732.BB_Rev3_F732(port=port, channel=channel, url=url, doopen=doopen)

    raise RuntimeError(f"Unknown hardware type: {id}")

