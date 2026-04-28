
import importlib
from . import channel, xbool, xint, xfloat, xstr



class mmap(channel):
    def __init__(self, filename, offset = 0, length = None, dtype = 'I', purl = None):
        (self.filename, self.offset, self.length, self.dtype) = (filename, offset, length, dtype)
        (self.mview, self.fd, self.f, self.state, self.purl) = (None, None, None, "closed", purl)

    def open(self):
        (os, mmap) = (importlib.import_module("os"), importlib.import_module("mmap"))
        self.f = open(self.filename, "r+b")
        maplen = self.length if self.length else os.stat(self.f.fileno()).st_size
        self.fd = mmap.mmap(self.f.fileno(), maplen, offset=self.offset)
        self.mview = memoryview(self.fd).cast(self.dtype)
        self.state = "open"
        return self

    def close(self):
        self.mview.release()
        self.fd.close()
        self.f.close()
        (self.mview, self.fd, self.f, self.state) = (None, None, None, "closed")

    @classmethod
    def fromparsedurl(cls, purl):
        offset = xint(purl.params.get('offset'), 0)
        length = xint(purl.params.get('length'))
        dtype = xstr(purl.params.get('dtype'), 'I')
        return cls(purl.path, offset, length, dtype, purl)



