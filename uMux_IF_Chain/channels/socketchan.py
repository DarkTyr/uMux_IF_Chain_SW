
import socket
from . import channel, xbool, xint, xfloat, xstr



class tcpchan(channel):
    def __init__(self, hostname, port, timeout = None, buffering = 16, nodelay = True, rcvbuf = None, bind = None, purl = None):
        (self.hostname, self.port, self.bind) = (hostname, port, bind)
        (self.timeout, self.buffering, self.nodelay, self.rcvbuf) = (timeout, buffering, nodelay, rcvbuf)
        (self.fd, self.socket, self.state, self.purl) = (None, None, "init", purl)

    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.nodelay: self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        if self.rcvbuf: self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.rcvbuf)
        if self.bind: (h, p) = self.bind.rsplit(":", 1); self.socket.bind((h, int(p)))
        self.socket.connect((self.hostname, self.port))
        if self.timeout: self.socket.settimeout(self.timeout)
        self.fd = self.socket.makefile('rwb', buffering=self.buffering)
        self.state = "open"
        return self

    def close(self):
        self.fd.close()
        self.socket.close()
        (self.fd, self.socket, self.state) = (None, None, "closed")

    def fromparsedurl(purl):
        bind = xstr(purl.params.get('bind'))
        timeout = xfloat(purl.params.get('timeout'))
        buffering = xint(purl.params.get('buffering'), 0)
        nodelay = xbool(purl.params.get('nodelay'), True)
        rcvbuf = xint(purl.params.get('rcvbuf'))
        return tcpchan(purl.hostname, purl.port, timeout, buffering, nodelay, rcvbuf, bind, purl)



class udpchan(channel):
    def __init__(self, hostname, port, timeout = None, buffering = 0, rcvbuf = None, bind = None, purl = None):
        (self.hostname, self.port, self.bind) = (hostname, port, bind)
        (self.timeout, self.buffering, self.rcvbuf) = (timeout, buffering, rcvbuf)
        (self.fd, self.socket, self.state, self.purl) = (None, None, "init", purl)

    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.rcvbuf: self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.rcvbuf)
        if self.bind: (h, p) = self.bind.rsplit(":", 1); self.socket.bind((h, int(p)))
        self.socket.connect((self.hostname, self.port))
        if self.timeout: self.socket.settimeout(self.timeout)
        self.fd = self.socket.makefile('rwb', buffering=self.buffering)
        self.state = "open"
        return self

    close = tcpchan.close

    def fromparsedurl(purl):
        bind = xstr(purl.params.get('bind'))
        timeout = xfloat(purl.params.get('timeout'))
        buffering = xint(purl.params.get('buffering'), 0)
        rcvbuf = xint(purl.params.get('rcvbuf'))
        return udpchan(purl.hostname, purl.port, timeout, buffering, rcvbuf, bind, purl)



