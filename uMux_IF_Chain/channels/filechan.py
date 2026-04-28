
from . import channel



class filechan(channel):
    def __init__(self, filename, purl = None):
        (self.filename) = (filename)
        (self.fd, self.state, self.purl) = (None, "init", purl)

    def open(self):
        self.fd = open(self.filename, "r+b")
        self.state = "open"
        return self

    def close(self):
        self.fd.close()
        (self.fd, self.state) = (None, "closed")



def fromparsedurl(purl):
    return filechan(purl.path, purl)



