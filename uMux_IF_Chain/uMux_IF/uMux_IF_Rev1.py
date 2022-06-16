# -*- coding: utf-8 -*-
'''
Module Tyr_Serial_IF
=================================
This module is responsible for communicating with any development board
that contains a tyr command processor.
'''
# System level imports
import time

import numpy as np

# local imports
# from devices import tmp275
from uMux_IF_Chain.devices import tmp275
from uMux_IF_Chain.devices import lmx2592

class _CMD:
    R = 0x01
    W = 0x00

    CMD_LEN         = 6

    NULL            = 0x00
    ISR             = 0x01
    ISR_MASK        = 0x02
    MON_CTRL        = 0x03
    FW_ID           = 0x10  # Firmware ID
    FW_CID          = 0x11  # MCU Unique ID Number (96 Bit)
    FW_BSN          = 0x12  # Read EEPROM to get Board Serial Number
    FW_EEPROM       = 0x13  # Read the reported full EEPROM
    FW_BB_LB        = 0x14
    FW_PIN_CTRL     = 0x15
    FW_SOFT_RST     = 0x16
    TEMP_THLD       = 0x20
    TEMP_READ       = 0x21
    NULLING_CTRL    = 0x30
    NULLING_UP      = 0x31
    NULLING_DN      = 0x32
    SYNTH_SR        = 0x40
    SYNTH_RST       = 0x41
    SYNTH_INIT      = 0x42
    SYNTH_WRITE     = 0x43
    SYNTH_REG_DUMP  = 0x44
    I2C_IF          = 0x50
    SPI_LOOPBACK    = 0x51
    PROG_EEPROM     = 0x60

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

class _GPIO:
    PIN_Slave_nINT      = 0x1 << 0
    PIN_Vref_En         = 0x1 << 1
    PIN_Local_I2C_SCL   = 0x1 << 2
    PIN_Local_I2C_SDA   = 0x1 << 3
    PIN_Op_Amp_SHDN     = 0x1 << 4
    PIN_EEPROM_nCS      = 0x1 << 5
    PIN_Synth_En        = 0x1 << 6
    PIN_Slave_nRST      = 0x1 << 7
    PIN_EEPROM_nWP      = 0x1 << 8


class UMux_IF_Rev1:
    def __init__(self, base_board, chip_select):
        self._cs = chip_select
        self._bb = base_board
        self._dac_nbits = 14
        self.debug = 1
        self.firmware_id = []
        self.unique_id = []
        self.board_serial_number = []
        self.eeprom = []
        self._delay = 0.0
        self._delay_i2c = 0.0
        self._tmp = tmp275.TMP275(0x48)
        self._lmx = lmx2592.LMX2592(self._synth_write_array, self._synth_read_array, 100)

    def _write(self, data: list[int]) -> None:
        self._bb.spi_write(self._cs, data)
        if(self.debug):
            print("uMux_IF_Rev1._write(): _cs={} data={}".format(self._cs, data))

    def _read(self, nBytes: int) -> list[int]:
        ret = self._bb.spi_read(self._cs, nBytes)
        if(self.debug):
            print("uMux_IF_Rev1._read():  _cs={} nBytes={} ret={}".format(self._cs, nBytes, ret))
        return ret

    def _write_read(self, nBytes_read: int, data: list[int]) -> list[int]:
        ret = self._bb.spi_write_read(self._cs, nBytes_read, data)
        if(self.debug):
            print("uMux_IF_Rev1._write_read(): _cs={} nBytes={}\n\tdata={}\n\tret={}" \
                  .format(self._cs, nBytes_read, data, ret))
        return ret

    def mcu_reset(self) -> None:
        data = [0x00] * _CMD.CMD_LEN
        data[0] = (_CMD.FW_SOFT_RST << 1) | _CMD.W
        data[1] = 0x55
        data[2] = 0x44
        data[3] = 0x33
        data[4] = 0x22
        self._write(data)
        return None

    def base_band_loop_back_enable(self) -> None:
        data = [0x00] * _CMD.CMD_LEN
        data[0] = (_CMD.FW_BB_LB << 1) | _CMD.W
        data[1] = 0x01
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return
        else:
            print("Write Failed")

    def base_band_loop_back_disable(self) -> None:
        data = [0x00] * _CMD.CMD_LEN
        data[0] = (_CMD.FW_BB_LB << 1) | _CMD.W
        data[1] = 0x00
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return
        else:
            print("Write Failed")

    def base_band_loop_back_get(self) -> bool:
        data = [0x00] * _CMD.CMD_LEN
        data[0] = (_CMD.FW_BB_LB << 1) | _CMD.R
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD):
            if(ret[1] == 0x01):
                return True
            elif(ret[1] == 0x00):
                return False
        else:
            print("Write Failed")

    def nulling_up_set(self, dac_val_I: int, dac_val_Q: int) -> None:
        if(dac_val_I > 2**self._dac_nbits):
            print("Value too high: dac_val_I")
            return
        elif(dac_val_I < 0):
            return

        if(dac_val_Q > 2**self._dac_nbits):
            print("Value too high: dac_val_I")
            return
        elif(dac_val_Q < 0):
            return

        data = [0x00] * _CMD.CMD_LEN
        temp_int = dac_val_I << 2
        data[0] = (_CMD.NULLING_UP << 1) | _CMD.W
        data[1] = (temp_int & 0xFF00) >> 8
        data[2] = (temp_int & 0x00FF) >> 0
        temp_int = dac_val_Q << 2
        data[3] = (temp_int & 0xFF00) >> 8
        data[4] = (temp_int & 0x00FF) >> 0
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return
        else:
            print("Write Failed")
    
    def nulling_up_get(self) -> tuple[int, int]:
        data = [0x00] * _CMD.CMD_LEN
        data[0] = (_CMD.NULLING_UP << 1) | _CMD.R
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD):
            dac_val_I = ((ret[1] << 8) | ret[2]) >> 2
            dac_val_Q = ((ret[3] << 8) | ret[4]) >> 2
            return (dac_val_I, dac_val_Q)
        else:
            print("Write Failed")
            return (None, None)

    def nulling_dn_set(self, dac_val_I: int, dac_val_Q: int) -> None:
        if(dac_val_I > (2**self._dac_nbits - 1)):
            print("Value too high: dac_val_I")
            return
        elif(dac_val_I < 0):
            pass

        if(dac_val_Q > 2**self._dac_nbits):
            print("Value too high: dac_val_Q")
            return
        elif(dac_val_Q < 0):
            pass

        data = [0x00] * _CMD.CMD_LEN
        temp_int = dac_val_I << 2
        data[0] = (_CMD.NULLING_DN << 1) | _CMD.W
        data[1] = (temp_int & 0xFF00) >> 8
        data[2] = (temp_int & 0x00FF) >> 0
        temp_int = dac_val_Q << 2
        data[3] = (temp_int & 0xFF00) >> 8
        data[4] = (temp_int & 0x00FF) >> 0
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return
        else:
            print("Write Failed")

    def nulling_dn_get(self) -> tuple[int, int]:
        data = [0x00] * _CMD.CMD_LEN
        data[0] = (_CMD.NULLING_DN << 1) | _CMD.R
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD):
            dac0 = ((ret[1] << 8) | ret[2]) >> 2
            dac1 = ((ret[3] << 8) | ret[4]) >> 2
            return (dac0, dac1)
        else:
            print("Write Failed")
            return(None, None)

    def synth_init(self) -> None:
        data = [0x00] * _CMD.CMD_LEN
        data[0] = (_CMD.SYNTH_INIT << 1) | _CMD.W
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            pass
        else:
            print("Write Failed")
            return
        self._lmx.synth_init()

    def synth_lock_status(self) -> bool:
        data = [0x00] * _CMD.CMD_LEN
        data[0] = (_CMD.SYNTH_SR << 1) | _CMD.R
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD):
            if(ret[1] == 0xFF):
                return True
            else:
                return False
        else:
            print("Write Failed")
            return None

    def synth_reset(self):
        data = [0x00] * _CMD.CMD_LEN
        data[0] = (_CMD.SYNTH_RST << 1) | _CMD.W
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return True
        else:
            print("Write Failed")
            return False

    def synth_get_Frequency_MHz(self) -> float:
        real_freq_MHz = self._lmx.get_Frequency_MHz()
        return real_freq_MHz

    def synth_set_Frequency_MHz(self, Freq_MHz) -> float:
        real_freq_MHz = self._lmx.set_Frequency_MHz(Freq_MHz)
        if(real_freq_MHz != Freq_MHz):
            print("WARNING: Requested Frequency is not exactly equal to the Real Frequency\n"
                + "\tRequested Frequency = {} MHz\n".format(Freq_MHz)
                + "\t     Real Frequency = {} MHz\n".format(real_freq_MHz))
        return real_freq_MHz

    def synth_powerdown_bit(self) -> None:
        self._lmx.powerdown_bit()

    def synth_powerup_bit(self) -> None:
        self._lmx.powerup_bit()

    def synth_powerdown_get(self) -> bool:
        return self._lmx.powerdown_get()

    def synth_reg_dump(self, print_to_console_only = False):
        cmd_array = [0x00] * _CMD.CMD_LEN
        cmd_array[0] = (_CMD.SYNTH_REG_DUMP << 1) | _CMD.R
        self._write(cmd_array)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD != _RET_VAL.MASK_READ_GOOD):
            print("Failed to understand command, RET_VAL is not READ_GOOD")
            return None
        reg_dump_size = ret[1]
        ret = self._read(reg_dump_size)

        ret = np.reshape(ret, (-1, 3))
        if(print_to_console_only):
            for i in ret:
                print("REG : {} = 0x{:02X}{:02X}".format(i[0], i[1], i[2]))
            return
        else:
            return ret

    def _synth_write_int(self, data: int) -> None:
        array = [0x0] * _CMD.CMD_LEN
        array[0] = (_CMD.SYNTH_WRITE << 1) | _CMD.W
        array[1] = (data >> 16) & 0xFF
        array[2] = (data >> 8) & 0xFF
        array[3] = (data >> 0) & 0xFF
        self._write(array)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return
        else:
            print("_synth_write_int Failed : \n"
                + "\t _cs={}\n".format(self._cs)
                + "\tdata=0x{}\n".format(data)
                + "\t ret=0x{}\n".format(ret))

    def _synth_write_array(self, data: list[int]) -> None:
        array = [0x0] * _CMD.CMD_LEN
        array[0] = (_CMD.SYNTH_WRITE << 1) | _CMD.W
        array[1] = data[0]
        array[2] = data[1]
        array[3] = data[2]
        self._write(array)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return
        else:
            print("_synth_write_array Failed : \n"
                + "\t  _cs={}\n".format(self._cs)
                + "\t data={}\n".format(data)
                + "\tarray={}\n".format(array)
                + "\t  ret={}\n".format(ret))

    def _synth_read_array(self, reg: int) -> list[int]:
        array = [0x0] * _CMD.CMD_LEN
        array[0] = (_CMD.SYNTH_WRITE << 1) | _CMD.R
        array[1] = reg & 0xFF
        self._write(array)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD):
            return ret[1:3]
        else:
            print("_synth_read_array Failed : \n"
                + "\t  _cs={}\n".format(self._cs)
                + "\t  reg={}\n".format(reg)
                + "\tarray={}\n".format(array)
                + "\t  ret={}\n".format(ret))

    def _synth_read_int(self, reg: int) -> int:
        array = [0x0] * _CMD.CMD_LEN
        array[0] = (_CMD.SYNTH_WRITE << 1) | _CMD.R
        array[1] = reg & 0xFF
        self._write(array)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD):
            return int((ret[1] << 8) | ret[2])
        else:
            print("_synth_read_int Failed : \n"
                + "\t _cs={}\n".format(self._cs)
                + "\t reg={}\n".format(reg)
                + "\t ret={}\n".format(ret))
            return []

    def read_temperatures_F(self) -> tuple[float, float]:
        array = [0x00] * _CMD.CMD_LEN
        array[0] = (_CMD.TEMP_READ << 1) | _CMD.R
        self._write(array)
        time.sleep(self._delay + self._delay_i2c)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD):
            synth_temp_F = self._tmp.convert_int2temp_F(ret[1:3])
            mcu_temp_F = self._tmp.convert_int2temp_F(ret[3:5])
            return (synth_temp_F, mcu_temp_F)
        else:
            print("Read Local Tempereatures Failed")
            return (None, None)

    def read_temperatures_C(self) -> tuple[float, float]:
        array = [0x00] * _CMD.CMD_LEN
        array[0] = (_CMD.TEMP_READ << 1) | _CMD.R
        self._write(array)
        time.sleep(self._delay + self._delay_i2c)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD):
            synth_temp_F = self._tmp.convert_int2temp_C(ret[1:3])
            mcu_temp_F = self._tmp.convert_int2temp_C(ret[3:5])
            return (synth_temp_F, mcu_temp_F)
        else:
            print("Read Local Tempereatures Failed")
            return (None, None)

    def spi_loopback(self, nBytes: int, nItter: int) -> int:
        import random
        if(nBytes > 255):
            print("nBytes can not be greater than 255")

        failed_compares = 0

        cmd_array = [0x00] * _CMD.CMD_LEN
        cmd_array[0] = (_CMD.SPI_LOOPBACK << 1) | _CMD.W
        cmd_array[1] = nBytes
        self._write(cmd_array)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD != 1):
            print("Failed to understand command, RET_VAL is not WRITE_GOOD")
            return None
        
        data_array = [random.randint(0, 255) for p in range(0, nBytes)]
        data_array[0] = (_CMD.SPI_LOOPBACK << 1) | _CMD.W
        time.sleep(self._delay)
        ret = self._write_read(nBytes, data_array)
        i = 0
        while(i <= nItter):
            prev_data = data_array
            prev_data[0] = _RET_VAL.MASK_WRITE_GOOD
            data_array = [random.randint(0, 255) for p in range(0, nBytes)]
            data_array[0] = (_CMD.SPI_LOOPBACK << 1) | _CMD.W
            ret = self._write_read(nBytes, data_array)
            if(self.debug):
                print("\tprev_data={}\n\tret_data={}".format(prev_data, ret))
            if(prev_data != ret):
                failed_compares += 1
            i += 1
        
        prev_data = data_array
        prev_data[0] = _RET_VAL.MASK_WRITE_GOOD
        data_array = [random.randint(0, 255) for p in range(0, nBytes)]
        data_array[0] = (_CMD.NULL << 1) | _CMD.W
        ret = self._write_read(nBytes, data_array)
        if(self.debug):
            print("\tprev_data={}\n\tret_data={}".format(prev_data, ret))
        if(prev_data != ret):
            failed_compares += 1

        return failed_compares

    def read_FWID(self):
        cmd_array = [0x00] * _CMD.CMD_LEN
        cmd_array[0] = (_CMD.FW_ID << 1) | _CMD.R
        self._write(cmd_array)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD != _RET_VAL.MASK_READ_GOOD):
            print("Failed to understand command, RET_VAL is not READ_GOOD")
            return None
        fwid_size = ret[1]   # Firmware returns the CID size (96 Bits, 12 bytes, 3 words)
        ret = self._read(fwid_size)
        self.firmware_id = ret
        return ret

    def read_CID(self):
        cmd_array = [0x00] * _CMD.CMD_LEN
        cmd_array[0] = (_CMD.FW_CID << 1) | _CMD.R
        self._write(cmd_array)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD != _RET_VAL.MASK_READ_GOOD):
            print("Failed to understand command, RET_VAL is not READ_GOOD")
            return None
        cid_size = ret[1]   # Firmware returns the CID size (96 Bits, 12 bytes, 3 words)
        ret = self._read(cid_size)
        self.unique_id = ret
        return ret

    def read_BSN(self):
        cmd_array = [0x00] * _CMD.CMD_LEN
        cmd_array[0] = (_CMD.FW_BSN << 1) | _CMD.R
        self._write(cmd_array)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD != _RET_VAL.MASK_READ_GOOD):
            print("Failed to understand command, RET_VAL is not READ_GOOD")
            return None
        bsn_size = ret[1]   # Firmware returns the CID size (96 Bits, 12 bytes, 3 words)
        ret = self._read(bsn_size)
        self.board_serial_number = ret
        return ret

    def read_eeprom(self, print_human_readable=False):
        cmd_array = [0x00] * _CMD.CMD_LEN
        cmd_array[0] = (_CMD.FW_EEPROM << 1) | _CMD.R
        self._write(cmd_array)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD != _RET_VAL.MASK_READ_GOOD):
            print("Failed to understand command, RET_VAL is not READ_GOOD")
            return None
        eeprom_size = ret[1]
        ret = self._read(eeprom_size)
        data_len = len(ret)
        nfields = int(data_len/16)
        text_array = [""] * nfields
        for idx in range(nfields):
            text_array[idx] = bytes(ret[0+16*idx : 16 + 16*idx]).decode("utf8")
        self.eeprom = text_array
        if(print_human_readable):
            print(text_array[0])
            for idx in range(nfields - 1):
                print("  " + text_array[idx + 1])
        return text_array

    def _write_eeprom(self, bsn, mcu_pn, freq_range, mixer_pn, synth_pn, bb_pn, lo_leak_pn):
        if(len(bsn) > 16):
            print("BSN is too long")
            return
        
        if(len(mcu_pn) > 16):
            print("mcu_pn is too long")
            return

        if(len(freq_range) > 16):
            print("freq_range is too long")
            return

        if(len(mixer_pn) > 16):
            print("mixer_pn is too long")
            return
        
        if(len(synth_pn) > 16):
            print("synth_pn is too long")
            return
        
        if(len(bb_pn) > 16):
            print("bb_pn is too long")
            return

        if(len(lo_leak_pn) > 16):
            print("lo_leak_pn is too long")
            return

        print("All entries are less than 16 bytes length")
        final_string = bsn.ljust(16, "\x00") \
                    + mcu_pn.ljust(16, "\x00") \
                    + freq_range.ljust(16, "\x00") \
                    + mixer_pn.ljust(16, "\x00") \
                    + synth_pn.ljust(16, "\x00") \
                    + bb_pn.ljust(16, "\x00") \
                    + lo_leak_pn.ljust(16, "\x00")

        for i in range(7):
            print(final_string[i*16:i*16+16])

        final_bytes = bytearray(final_string, "utf8")

        cmd_array = [0x00] * _CMD.CMD_LEN
        cmd_array[0] = (_CMD.PROG_EEPROM << 1) | _CMD.W
        cmd_array[1] = 112
        self._write(cmd_array)
        time.sleep(self._delay)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD != _RET_VAL.MASK_WRITE_GOOD):
            print("Failed to understand command, RET_VAL is not WRITE_GOOD")
            return None
        if(ret[1] != len(final_bytes)):
            print("Device did not return the expected number of bytes for the next step")
            return None

        self._write(final_bytes)
        time.sleep(10)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD != _RET_VAL.MASK_WRITE_GOOD):
            print("Something went wrong during writing to the EEPROM")
            return None

    def _read_temp_threshold(self):
        array = [0x00] * _CMD.CMD_LEN
        array[0] = (_CMD.TEMP_THLD << 1) | _CMD.R
        self._write(array)
        time.sleep(self._delay + self._delay_i2c)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD):
            synth_temp_F = self._tmp.convert_int2temp_C(ret[1:3])
            mcu_temp_F = self._tmp.convert_int2temp_C(ret[3:5])
            return (synth_temp_F, mcu_temp_F)
        else:
            print("Read threshold Tempereatures Failed")
            return (None, None)

    def _write_temp_threshold(self, temp_C):
        array = [0x00] * _CMD.CMD_LEN
        array[0] = (_CMD.TEMP_THLD << 1) | _CMD.W
        temp_var = int(temp_C / 0.0625)
        array[1] = 0xFF & (temp_var >> 4)
        array[2] = 0xFF & (temp_var << 4)
        array[3] = array[1]
        array[4] = array[2]
        self._write(array)
        ret = self._read(_RET_VAL.RET_LEN)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD != _RET_VAL.MASK_WRITE_GOOD):
            print("Was unable to set temperature threshold")
            return
        else:
            return
