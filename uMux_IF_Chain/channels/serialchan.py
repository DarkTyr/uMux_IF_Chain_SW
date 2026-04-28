
import serial
import platform
from . import channel, xbool, xint, xfloat, xstr



class SerialChan(channel):
    def __init__(self, port, baudrate = 115200, nbit = 8, parity = 'N', nstop = 1, rtscts = False, xonxoff = False, timeout = None, purl = None):
        # Because Windows has to be different than every other system
        # Strip the slash that is passed in and then make sure it is all upper case. 
        if(platform.system() == "Windows"):
            self.port       = port.strip('/').upper()
        else:
            self.port   = port
        self.baudrate   = baudrate
        self.nbit       = nbit
        self.parity     = parity
        self.nstop      = nstop
        self.rtscts     = rtscts
        self.xonxoff    = xonxoff
        self.timeout    = timeout
        self.fd         = None
        self.state      = 'init'
        self.purl       = purl

    def open(self):
        b = { '7': serial.SEVENBITS, '8': serial.EIGHTBITS }[str(self.nbit)]
        p = { 'E' : serial.PARITY_EVEN, 'O' : serial.PARITY_ODD, 'N' : serial.PARITY_NONE }[self.parity]
        s = { '1' : serial.STOPBITS_ONE, '2' : serial.STOPBITS_TWO }[str(self.nstop)]
        self.fd = serial.Serial(port=self.port, baudrate=self.baudrate, bytesize=b, parity=p, stopbits=s, rtscts=self.rtscts, xonxoff=self.xonxoff, timeout=self.timeout, write_timeout=self.timeout);
        self.state = "open"
        return self

    def close(self):
        self.fd.close()
        (self.fd, self.state) = (None, "closed")



def fromparsedurl(purl):
    baudrate = xint(purl.params.get('baudrate'), 115200)
    nbit = xint(purl.params.get('nbit'), 8)
    parity = xstr(purl.params.get('parity'), 'N')
    nstop = xint(purl.params.get('nstop'), 1)
    rtscts = xbool(purl.params.get('rtscts'), False)
    xonxoff = xbool(purl.params.get('xonxoff'), False)
    timeout = xfloat(purl.params.get('timeout'))
    return SerialChan(purl.path, baudrate, nbit, parity, nstop, rtscts, xonxoff, timeout, purl)


