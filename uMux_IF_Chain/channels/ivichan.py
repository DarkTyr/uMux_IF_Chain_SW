
import importlib
import qsdumux.channels



class usbtmcchan(qsdumux.channels.channel):
    def __init__(self, device = None, purl = None):
        (self.device) = (device)
        usbtmc = importlib.import_module("usbtmc")
        (self.fd, self.state, self.purl) = (usbtmc.Instrument(self.device), "init", purl)

    def open(self):
        self.fd.open()
        self.state = "open"
        return self

    def close(self):
        self.fd.close()
        self.state = "closed"

    def fromparsedurl(purl):
        return usbtmcchan(purl.path.strip('/'), purl)



class vxi11chan(qsdumux.channels.channel):
    def __init__(self, hostname, name = None, purl = None):
        (self.hostname, self.name) = (hostname, name)
        vxi11 = importlib.import_module("vxi11")
        (self.fd, self.state, self.purl) = (vxi11.Instrument(self.hostname, self.name), "init", purl)

    def open(self):
        self.fd.open()
        self.state = "open"
        return self

    def close(self):
        self.fd.close()
        self.state = "closed"

    def fromparsedurl(purl):
        name = None if len(purl.path) == 0 else purl.path.strip('/')
        return vxi11chan(purl.hostname, name, purl)



