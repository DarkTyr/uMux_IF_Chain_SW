# -*- coding: utf-8 -*-
'''
Module Tyr_Serial_IF
=================================
This module is responsible for communicating with any development board
that contains a tyr command processor.
'''
# System level imports
import time

# local imports
# from devices import tmp275
from uMux_IF_Chain.devices import tmp275

class _CMD:
    R = 0x01
    W = 0x00

    NULL = 0x00
    ISR = 0x01
    SR = 0x02
    MON_CTRL = 0x03
    FW_ID = 0x10
    FW_CID = 0x11
    FW_BSN = 0x12
    FW_BB_LB = 0x13
    FW_PIN_CTRL = 0x14
    FW_SOFT_RST = 0x15
    TEMP_THLD = 0x20
    TEMP_READ = 0x21
    NULLING_CTRL = 0x30
    NULLING_UP = 0x31
    NULLING_DN = 0x32
    SYNTH_SR = 0x40
    SYNTH_SOFT_RST = 0x41
    SYNTH_INIT = 0x42
    SYNTH_WRITE = 0x43

class _RET_VAL:
    MASK_WRITE_GOOD = 0x1 << 0
    MASK_READ_GOOD = 0x1 << 1
    MASK_INVALID_CMD = 0x1 << 2
    MASK_I2C_NACK = 0x1 << 3
    MASK_MCU_RST_DONE = 0x1 << 4
    MASK_BUSY = 0x1 << 5
    MASK_RSVD = 0x1 << 6
    MASK_OVERHEAT = 0x1 << 7

class UMux_IF_Rev1:
    def __init__(self, chip_select):
        self._cs = chip_select
        self._spi_write = None
        self._spi_read = None
        self._dac_nbits = 14
        self.debug = 1
        self._delay = 0.1
        self.blank = None
        self._tmp = tmp275.TMP275(0x48)

    def link_methods(self, spi_write, spi_read):
        self._spi_write = spi_write
        self._spi_read = spi_read

    def _write(self, data):
        if(self.debug):
            print("uMux_IF_Rev1._write(): _cs={} data={}".format(self._cs, data))
        self._spi_write(self._cs, data)

    def _read(self, nBytes):
        ret = self._spi_read(self._cs, nBytes)
        if(self.debug):
            print("uMux_IF_Rev1._read(): _cs={} nBytes={} ret={}".format(self._cs, nBytes, ret))
        return ret

    def base_band_loop_back_enable(self):
        data = [0x00] * 6
        data[0] = (_CMD.FW_BB_LB << 1) | _CMD.W
        data[1] = 0x01
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(0x6)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return
        else:
            print("Write Failed")

    def base_band_loop_back_disable(self):
        data = [0x00] * 6
        data[0] = (_CMD.FW_BB_LB << 1) | _CMD.W
        data[1] = 0x00
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(0x6)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return
        else:
            print("Write Failed")

    def nulling_up(self, dac_val_I: int, dac_val_Q: int):
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

        data = [0x00] * 6
        temp_int = dac_val_I << 2
        data[0] = (_CMD.NULLING_UP << 1) | _CMD.W
        data[1] = (temp_int & 0xFF00) >> 8
        data[2] = (temp_int & 0x00FF) >> 0
        temp_int = dac_val_Q << 2
        data[3] = (temp_int & 0xFF00) >> 8
        data[4] = (temp_int & 0x00FF) >> 0
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(0x6)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return
        else:
            print("Write Failed")

    def nulling_dn(self, dac_val_I, dac_val_Q):
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

        data = [0x00] * 6
        temp_int = dac_val_I << 2
        data[0] = (_CMD.NULLING_DN << 1) | _CMD.W
        data[1] = (temp_int & 0xFF00) >> 8
        data[2] = (temp_int & 0x00FF) >> 0
        temp_int = dac_val_Q << 2
        data[3] = (temp_int & 0xFF00) >> 8
        data[4] = (temp_int & 0x00FF) >> 0
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(0x6)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return
        else:
            print("Write Failed")

    def synth_init(self):
        data = [0x00] * 6
        data[0] = (_CMD.SYNTH_INIT << 1) | _CMD.W
        self._write(data)
        time.sleep(self._delay)
        ret = self._read(0x6)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return
        else:
            print("Write Failed")

    def synth_write(self, data):
        array = [0x0] * 6
        array[0] = (_CMD.SYNTH_WRITE << 1) | _CMD.W
        array[1] = (data >> 16) & 0xFF
        array[2] = (data >> 8) & 0xFF
        array[3] = (data >> 0) & 0xFF
        self._write(array)
        time.sleep(self._delay)
        ret = self._read(0x06)
        if(ret[0] & _RET_VAL.MASK_WRITE_GOOD):
            return
        else:
            print("Write Failed")

    def synth_read(self, reg):
        array = [0x0] * 6
        array[0] = (_CMD.SYNTH_WRITE << 1) | _CMD.R
        array[1] = reg & 0xFF
        self._write(array)
        time.sleep(self._delay)
        ret = self._read(0x06)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD):
            return ret[1:3]
        else:
            print("Read Failed")

    def read_temperatures_F(self):
        array = [0x00] * 6
        array[0] = (_CMD.TEMP_READ << 1) | _CMD.R
        self._write(array)
        time.sleep(self._delay)
        ret = self._read(0x06)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD):
            synth_temp_F = self._tmp.convert_int2temp_F(ret[1:3])
            mcu_temp_F = self._tmp.convert_int2temp_F(ret[3:5])
            return (synth_temp_F, mcu_temp_F)
        else:
            print("Read Local Tempereatures Failed")
            return (None, None)

    def read_temperatures_C(self):
        array = [0x00] * 6
        array[0] = (_CMD.TEMP_READ << 1) | _CMD.R
        self._write(array)
        time.sleep(self._delay)
        ret = self._read(0x06)
        if(ret[0] & _RET_VAL.MASK_READ_GOOD):
            synth_temp_F = self._tmp.convert_int2temp_C(ret[1:3])
            mcu_temp_F = self._tmp.convert_int2temp_C(ret[3:5])
            return (synth_temp_F, mcu_temp_F)
        else:
            print("Read Local Tempereatures Failed")
            return (None, None)

    