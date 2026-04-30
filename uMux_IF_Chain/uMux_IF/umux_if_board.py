# -*- coding: utf-8 -*-


class CommError(Exception):
    pass

class _CMD:
    R       = 0x01  # Read

    CMD_LEN         = 6

    FW_ID   = 0x10  # Firmware ID

class _RET_VAL:
    RET_LEN = 6

    MASK_WRITE_GOOD =   0x1 << 0
    MASK_READ_GOOD =    0x1 << 1
    MASK_INVALID_CMD =  0x1 << 2
    MASK_I2C_NACK =     0x1 << 3
    MASK_MCU_RST_DONE = 0x1 << 4
    MASK_BUSY =         0x1 << 5
    MASK_RSVD =         0x1 << 6
    MASK_OVERHEAT =     0x1 << 7

class uMux_IF_Board:
    def __init__(self, base_board, chip_select):
        self._cs = chip_select
        self._bb = base_board
        self.firmware_id = ''
        self.debug = 0

    def _write(self, data: list[int]) -> None:
        self._bb.stack_write(self._cs, data)
        if(self.debug):
            print("uMux_IF_Rev1._write(): _cs={} data={}".format(self._cs, data))

    def _read(self, nBytes: int) -> list[int]:
        ret = self._bb.stack_read(self._cs, nBytes)
        if(self.debug):
            print("uMux_IF_Rev1._read():  _cs={} nBytes={} ret={}".format(self._cs, nBytes, ret))
        return ret

    def read_FWID(self):
        cmd_array = [0x00] * _CMD.CMD_LEN
        cmd_array[0] = (_CMD.FW_ID << 1) | _CMD.R
        self._write(cmd_array)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD != _RET_VAL.MASK_READ_GOOD):
            raise CommError("Failed to understand command, RET_VAL is not READ_GOOD")
        fwid_size = ret[1] # Returns the length of fw_id
        ret = self._read(fwid_size)
        self.firmware_id = bytes(ret).decode('ascii').rstrip('\x00')
        return self.firmware_id

    def mcu_reset(self): raise NotImplementedError

    def base_band_loop_back_enable(self): raise NotImplementedError

    def base_band_loop_back_disable(self): raise NotImplementedError

    def base_band_loop_back_get(self): raise NotImplementedError

    def nulling_enable(self): raise NotImplementedError

    def nulling_disable(self): raise NotImplementedError

    def nulling_state_get(self): raise NotImplementedError

    def nulling_up_set(self): raise NotImplementedError

    def nulling_up_get(self): raise NotImplementedError

    def nulling_dn_set(self): raise NotImplementedError

    def nulling_dn_get(self): raise NotImplementedError



    def synth_init(self): raise NotImplementedError
    
    def synth_lock_status(self): raise NotImplementedError

    def synth_reset(self): raise NotImplementedError

    def synth_get_Frequency_MHz(self): raise NotImplementedError

    def synth_set_Frequency_MHz(self): raise NotImplementedError

    def synth_powerdown_bit(self): raise NotImplementedError

    def synth_powerup_bit(self): raise NotImplementedError

    def synth_powerdown_get(self): raise NotImplementedError

    def synth_reg_dump(self): raise NotImplementedError


    def read_temperatures_F(self): raise NotImplementedError

    def read_temperatures_C(self): raise NotImplementedError



    def read_CID(self): raise NotImplementedError

    def read_BSN(self): raise NotImplementedError

    def read_eeprom(self): raise NotImplementedError

    def _write_eeprom(self): raise NotImplementedError




from uMux_IF_Chain.uMux_IF import umux_if_rev1
from uMux_IF_Chain.uMux_IF import umux_if_rev2

def open_uMux_IF_Board(base_board, chip_select):
    board = uMux_IF_Board(base_board=base_board, chip_select=chip_select)
    board.read_FWID()

    if "uMux_IF_Rev1_Base 1.0.0" in board.firmware_id:
        return umux_if_rev1.UMux_IF_Rev1(base_board, chip_select)

    if "uMux_IF_Rev2_Base" in board.firmware_id:
        return umux_if_rev2.UMux_IF_Rev2(base_board, chip_select)
    
    raise RuntimeError(f"Unknown hardware type: {board.firmware_id}")