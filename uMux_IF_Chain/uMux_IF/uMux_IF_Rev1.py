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
from uMux_IF_Chain.devices import lmx2592

class _CMD:
    R = 0x01
    W = 0x00

    CMD_LEN         = 6

    NULL            = 0x00
    ISR             = 0x01
    ISR_MASK        = 0x02
    MON_CTRL        = 0x03
    FW_ID           = 0x10
    FW_CID          = 0x11
    FW_BSN          = 0x12
    FW_BB_LB        = 0x13
    FW_PIN_CTRL     = 0x14
    FW_SOFT_RST     = 0x15
    TEMP_THLD       = 0x20
    TEMP_READ       = 0x21
    NULLING_CTRL    = 0x30
    NULLING_UP      = 0x31
    NULLING_DN      = 0x32
    SYNTH_SR        = 0x40
    SYNTH_SOFT_RST  = 0x41
    SYNTH_INIT      = 0x42
    SYNTH_WRITE     = 0x43
    I2C_IF          = 0x50
    SPI_LOOPBACK    = 0x51

class _RET_VAL:
    RET_LEN = 6

    MASK_WRITE_GOOD = 0x1 << 0
    MASK_READ_GOOD = 0x1 << 1
    MASK_INVALID_CMD = 0x1 << 2
    MASK_I2C_NACK = 0x1 << 3
    MASK_MCU_RST_DONE = 0x1 << 4
    MASK_BUSY = 0x1 << 5
    MASK_RSVD = 0x1 << 6
    MASK_OVERHEAT = 0x1 << 7

class UMux_IF_Rev1:
    def __init__(self, base_board, chip_select):
        self._cs = chip_select
        self._bb = base_board
        self._spi_write = None
        self._spi_read = None
        self._dac_nbits = 14
        self.debug = 1
        self._delay = 0.005
        self._tmp = tmp275.TMP275(0x48)
        self._lmx = lmx2592.LMX2592(self._synth_write_array, self._synth_read_array, 100)

    def _write(self, data: list[int]) -> None:
        if(self.debug):
            print("uMux_IF_Rev1._write(): _cs={} data={}".format(self._cs, data))
        self._bb.spi_write(self._cs, data)

    def _read(self, nBytes: int) -> list[int]:
        ret = self._bb.spi_read(self._cs, nBytes)
        if(self.debug):
            print("uMux_IF_Rev1._read(): _cs={} nBytes={} ret={}".format(self._cs, nBytes, ret))
        return ret

    def _write_read(self, nBytes_read: int, data: list[int]) -> list[int]:
        ret = self._bb.spi_write_read(self._cs, nBytes_read, data)
        if(self.debug):
            print("uMux_IF_Rev1._write_read(): _cs={} nBytes={}\n\tdata={}\n\tret={}" \
                  .format(self._cs, nBytes_read, data, ret))
        return ret


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

    def nulling_up(self, dac_val_I: int, dac_val_Q: int) -> None:
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

    def nulling_dn(self, dac_val_I: int, dac_val_Q: int) -> None:
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

    def synth_set_Frequency_MHz(self, Freq_MHz) -> float:
        real_freq_MHz = self._lmx.set_Frequency_MHz(Freq_MHz)
        if(real_freq_MHz != Freq_MHz):
            print("WARNING: Requested Frequency is not exactly equal to the Real Frequency\n"
                + "\tRequested Frequency = {} MHz\n".format(Freq_MHz)
                + "\t     Real Frequency = {} MHz\n".format(real_freq_MHz))
        return real_freq_MHz

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
            print("Write Failed")

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
            print("Write Failed")

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
            print("Read Failed")

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
            print("Read Failed")
            return []

    def read_temperatures_F(self) -> tuple[float, float]:
        array = [0x00] * _CMD.CMD_LEN
        array[0] = (_CMD.TEMP_READ << 1) | _CMD.R
        self._write(array)
        time.sleep(self._delay)
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
        time.sleep(self._delay)
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
        self._write(data_array)
        i = 0
        while(i < nItter):
            prev_data = data_array
            prev_data[0] = _RET_VAL.MASK_WRITE_GOOD
            data_array = [random.randint(0, 255) for p in range(0, nBytes)]
            data_array[0] = (_CMD.SPI_LOOPBACK << 1) | _CMD.W
            time.sleep(0.001)   ## 1ms sleep to give IF MCU time to move data and restart DMA
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
        time.sleep(0.001)   ## 1ms sleep to give IF MCU time to move data and restart DMA 
        ret = self._write_read(nBytes, data_array)
        if(self.debug):
            print("\tprev_data={}\n\tret_data={}".format(prev_data, ret))
        if(prev_data != ret):
            failed_compares += 1

        return failed_compares
