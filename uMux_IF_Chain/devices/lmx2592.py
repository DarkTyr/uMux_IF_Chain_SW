# -*- coding: utf-8 -*-
'''
Module lmx2592
=================================

'''
import csv
from typing import Callable

class _REG_38:
    PLL_N_SHIFT = 1

class _R0:
    def __init__(self) -> None:
        self.REG_NUM = 0x00
        self.cur = [0x00, 0x00]
        self.BIT_FCAL_EN = 3
        self.MASK_FCAL_EN = 0x1 << self.BIT_FCAL_EN
        self.BIT_MUXOUT_SEL = 2
        self.MASK_MUXOUT_SEL = 0x1 << self.BIT_MUXOUT_SEL
        self.BIT_RESET = 1
        self.MASK_RESET = 0x01 << self.BIT_RESET
        self.BIT_POWERDOWN = 0
        self.MASK_POWERDOWN = 0x01 << self.BIT_POWERDOWN
        self.FCAL_EN = 0x01
        self.MUXOUT_READBACK = 0
        self.MUXOUT_LOCK_DETECT = 1

class _REG:
    PLL_N = 38
    PLL_DEN_HIGH = 40
    PLL_DEN_LOW = 41
    PLL_NUM_HIGH = 44
    PLL_NUM_LOW = 45
    PLL_VCO_2X = 30

class _PLL_Config:
    def __init__(self, F_ref_MHz: float) -> None:
        self.N = 9
        self.Den = 1000
        self.Num = 0
        self.F_REF_MHZ = F_ref_MHz
        self.ref_x2 = False
        self.vco_x2 = False
        self.Freq = 0

    def desired_Freq(self, Freq_MHz: float) -> float:
        pfd_MHz = (1 + 1 * self.ref_x2) * self.F_REF_MHZ
        if(Freq_MHz < 3550):
            return 0
        elif (Freq_MHz > 7100):
            self.vco_x2 = True
        else:
            self.vco_x2 = False

        self.N, remain = divmod(Freq_MHz * 1e6, pfd_MHz*1e6 * (2 + 2 * self.vco_x2))
        self.N = int(self.N)    # Odd issue where divmod can return a float type
        self.Num = int(remain/(pfd_MHz*1e6 * (2 + 2*self.vco_x2))*self.Den)
        F_real_MHz = float(pfd_MHz*1e6) * (self.N + (self.Num/self.Den))*(2+2*self.vco_x2)/1e6
        self.Freq = round(F_real_MHz, 6)
        return float(self.Freq)

    def Cur_Freq(self, N: int, Den: int, Num: int, vco_x2: bool) -> float:
        self.N = N
        if(Den > 0):
            self.Den = Den
        else:
            self.Den = 1
        self.Num = Num
        self.vco_x2 = vco_x2
        pfd_MHz = (1 + 1 * self.ref_x2) * self.F_REF_MHZ
        F_real_MHz = float(pfd_MHz*1e6) * (self.N + (self.Num/self.Den))*(2+2*self.vco_x2)/1e6
        self.Freq = round(F_real_MHz, 6)
        return float(self.Freq)

class LMX2592:
    def __init__(self, func_spi_write: Callable, func_spi_read: Callable, ref_freq_MHz) -> None:
        self._spi_write = func_spi_write
        self._spi_read = func_spi_read
        self._ref_freq_MHz = ref_freq_MHz
        self._pll = _PLL_Config(self._ref_freq_MHz)
        self._R0 = _R0()
        self.debug = 0

    def get_Frequency_MHz(self) -> float:
        if(self.debug):
            print(self.get_Frequency_MHz.__qualname__+"()")

        temp = self._spi_read(_REG.PLL_DEN_HIGH)
        Den = temp[0] << 24 | temp[1] << 16
        temp = self._spi_read(_REG.PLL_DEN_LOW)
        Den += temp[0] << 8 | temp[1] << 0
        if(self.debug):
            print("\tDen = {}".format(Den))

        temp = self._spi_read(_REG.PLL_NUM_HIGH)
        Num = temp[0] << 24 | temp[1] << 16
        temp = self._spi_read(_REG.PLL_NUM_LOW)
        Num += temp[0] << 8 | temp[1] << 0
        if(self.debug):
            print("\tNum = {}".format(Num))
            
        temp = self._spi_read(_REG.PLL_N)
        N = temp[0] << 7 | temp[1] >> 1
        if(self.debug):
            print("\t  N = {}".format(N))
            
        temp = self._spi_read(_REG.PLL_VCO_2X)
        if(temp[0] & 0x1):
            vco_2x = True
        else:
            vco_2x = False
        if(self.debug):
            print("\tVCO_2x = {}".format(vco_2x))

        cur_freq = self._pll.Cur_Freq(N, Den, Num, vco_2x)
        return cur_freq

    def set_Frequency_MHz(self, Freq_MHz: float) -> float:
        '''
        Write the registers and trigger a relock of the PLL
        N
        Den
        Num
        '''
        if(self.debug):
            print(self.set_Frequency_MHz.__qualname__+"({} MHz)".format(Freq_MHz))

        real_freq = self._pll.desired_Freq(Freq_MHz)
        if(self.debug):
            print("\treal_freq = {}".format(real_freq))

        data = [0x00] * 3
        data[0] = _REG.PLL_DEN_HIGH
        data[1] = (self._pll.Den >> 24 ) & 0xFF
        data[2] = (self._pll.Den >> 16 ) & 0xFF
        self._spi_write(data)
        data[0] = _REG.PLL_DEN_LOW
        data[1] = (self._pll.Den >> 8 ) & 0xFF
        data[2] = (self._pll.Den >> 0 ) & 0xFF
        self._spi_write(data)

        data[0] = _REG.PLL_NUM_HIGH
        data[1] = (self._pll.Num >> 24 ) & 0xFF
        data[2] = (self._pll.Num >> 16 ) & 0xFF
        self._spi_write(data)
        data[0] = _REG.PLL_NUM_LOW
        data[1] = (self._pll.Num >> 8 ) & 0xFF
        data[2] = (self._pll.Num >> 0 ) & 0xFF
        self._spi_write(data)

        data[0] = _REG.PLL_N
        data[1] = ((self._pll.N << _REG_38.PLL_N_SHIFT) >> 8 ) & 0xFF
        data[2] = ((self._pll.N << _REG_38.PLL_N_SHIFT) >> 0 ) & 0xFF       
        self._spi_write(data)

        self._R0.cur = self._spi_read(self._R0.REG_NUM)
        data[0] = self._R0.REG_NUM
        data[1] = self._R0.cur[0]
        data[2] = self._R0.cur[1] | (self._R0.FCAL_EN << self._R0.BIT_FCAL_EN)
        self._spi_write(data)
        return real_freq

    def trigger_cal(self) -> None:
        if(self.debug):
            print(self.trigger_cal.__qualname__+"()")
        data_out = [0x00] * 3
        data_in = self._spi_read(0x00)
        data_out[0] = self._R0.REG_NUM
        data_out[1] = data_in[0]
        data_out[2] = data_in[1] | (self._R0.FCAL_EN << self._R0.BIT_FCAL_EN)
        self._spi_write(data_out)

    def is_locked(self) -> bool:
        if(self.debug):
            print(self.is_locked.__qualname__+"()")
        '''
        This has to change the MUX output mode to send out the locked status, grab data
        which will refelct the clock status. Then it will need to set it back to outputing
        the read back data.
        '''
        data = [0x00] * 3
        # read current state of R0
        self._R0.cur = self._spi_read(self._R0.REG_NUM)
        # Assembly instruction to set the MUXOUT bit
        data[0] = self._R0.REG_NUM
        data[1] = self._R0.cur[0]
        data[2] = self._R0.cur[1] | (self._R0.MUXOUT_LOCK_DETECT << self._R0.BIT_MUXOUT_SEL)
        data[2] = data[2] & ~(self._R0.MASK_FCAL_EN)
        # change the MUXOUT bit
        self._spi_write(data)
        # read the lcok status of the LMX
        status = self._spi_read(self._R0.REG_NUM)
        # prepare data to set back to what it was, except for the FCAL_EN bit, we don't want to trigger another calibration
        data[2] = self._R0.cur[1] & ~(self._R0.MASK_FCAL_EN)
        self._spi_write(data)
        
        if(status[0] == 0xFF):
            return True
        return False

    def synth_init(self) -> None:
        if(self.debug):
            print(self.synth_init.__qualname__+"()")

        if(self._ref_freq_MHz == 100):
            SYTNH_CONFIG_FILE = '../devices/tics_synth_init/lmx2592_init_100MHz_Ref.txt'
            with open(SYTNH_CONFIG_FILE) as csvfile:
                data_file = list(csv.reader(csvfile, delimiter='\t'))

            if(self.debug):
                print("\t Loaded file \"{}\" to init".format(SYTNH_CONFIG_FILE))

            data = [0x00] * 3
            for reg in data_file:
                if(self.debug > 1):
                    print("\t{}".format(reg[0]))
                reg_val = int(reg[1], base=16)
                data[0] = 0xFF & (reg_val >> 16)
                data[1] = 0xFF & (reg_val >> 8)
                data[2] = 0xFF & (reg_val >> 0)
                self._spi_write(data)

        elif(self._ref_freq_MHz == 200):
            SYTNH_CONFIG_FILE = '../devices/tics_synth_init/lmx2592_init_200MHz_Ref.txt'
            with open(SYTNH_CONFIG_FILE) as csvfile:
                data = list(csv.reader(csvfile, delimiter='\t'))

            if(self.debug):
                print("\t Loaded file \"{}\" to init".format(SYTNH_CONFIG_FILE))

            data = [0x00] * 3
            for reg in data:
                if(self.debug > 1):
                    print("\t{}".format(reg[0]))
                reg_val = int(reg[1], base=16)
                data[0] = 0xFF & (reg_val >> 16)
                data[1] = 0xFF & (reg_val >> 8)
                data[2] = 0xFF & (reg_val >> 0)
                self._spi_write(data)

        else:
            print("The software does not know what to do when there is a Ref Freq of {} MHz".format(self._ref_freq_MHz))
    
    def powerdown_bit(self):
        if(self.debug):
            print(self.powerdown_bit.__qualname__+"()")
        data = [0x00] * 3
        self._R0.cur = self._spi_read(self._R0.REG_NUM)
        data[0] = self._R0.REG_NUM
        data[1] = self._R0.cur[0]
        data[2] = self._R0.cur[1] | self._R0.MASK_POWERDOWN
        self._spi_write(data)

    def powerup_bit(self):
        if(self.debug):
            print(self.powerup_bit.__qualname__+"()")
        data = [0x00] * 3
        self._R0.cur = self._spi_read(self._R0.REG_NUM)
        data[0] = self._R0.REG_NUM
        data[1] = self._R0.cur[0]
        data[2] = self._R0.cur[1] & ~self._R0.MASK_POWERDOWN
        self._spi_write(data)

