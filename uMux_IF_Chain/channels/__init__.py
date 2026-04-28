
import importlib, inspect
from collections import namedtuple



class channel:
    fd = None

    def fromparsedurl(purl): raise NotImplementedError

    def open(self): raise NotImplementedError

    def close(self): raise NotImplementedError



# schemes = dict(
#     file = ("file", "qsdumux.channels.filechan", None),
#     tcp = ("tcp", "qsdumux.channels.socketchan", "tcpchan"),
#     udp = ("udp", "qsdumux.channels.socketchan", "udpchan"),
#     serial = ("serial", "qsdumux.channels.serialchan", None),
#     usbtmc = ("usbtmc", "qsdumux.channels.ivichan", "usbtmcchan"),
#     vxi11 = ("vxi11", "qsdumux.channels.ivichan", "vxi11chan"),
#     mmap = ("mmap", "qsdumux.channels.mmap", "mmap"),
# )

schemes = dict(
    file = ("file", "channels.filechan", None),
    tcp = ("tcp", "channels.socketchan", "tcpchan"),
    udp = ("udp", "channels.socketchan", "udpchan"),
    serial = ("serial", "channels.serialchan", None),
    usbtmc = ("usbtmc", "channels.ivichan", "usbtmcchan"),
    vxi11 = ("vxi11", "channels.ivichan", "vxi11chan"),
    mmap = ("mmap", "channels.mmap", "mmap"),
)

def registerchannel(scheme, moduleref, classname = None):
    assert scheme not in schemes, "%s %s" % (scheme, schemes)
    schemes[scheme] = (scheme, moduleref, classname)



def fromparsedurl(purl, defaulthostname = None, defaultport = None, defaultparams = {}):
    hostname = purl.hostname if purl.hostname else defaulthostname
    port = purl.port if purl.port else defaultport
    defaultparams.update(purl.params)
    netloc = hostname if port == None else "%s:%d" % (hostname, port)
    purl = namedtuple("extpurl", "scheme hostname port path params query fragment")(purl.scheme, hostname, port, purl.path, defaultparams, purl.query, purl.fragment)

    scheme = purl.scheme.rsplit('-')[-1]
    assert scheme in schemes, "unknown scheme (inferred from %s): %s" % (purl, scheme)
    (scheme, moduleref, classname) = schemes[scheme]
    module = module if inspect.ismodule(moduleref) else importlib.import_module(moduleref)
    factory = module if classname == None else getattr(module, classname)
    return factory.fromparsedurl(purl)


def xurlparse(spec):
    if not isinstance(spec, (str, bytes)) or spec.find("://") == -1: return None
    urllibparse = importlib.import_module("urllib.parse")
    re = importlib.import_module("re")

    # parse url twice, the second time as http://, so that we also get the params/fragment/query fields
    o = urllibparse.urlparse(spec) # original
    h = urllibparse.urlparse(re.sub("^.*?://", "http://", spec)) # as if it were http://

    # parse_qs returns a dict with arrays as values - take the last element. provide 'None' if list was empty
    params = urllibparse.parse_qs(h.query,keep_blank_values=True)
    params = { k: ([None] + v)[-1] for (k, v) in params.items() }

    return h._replace(scheme=o.scheme, params=params)


def fromurl(url, defaulthostname = None, defaultport = None, defaultparams = {}):
    purl = xurlparse(url)
    return fromparsedurl(purl, defaulthostname, defaultport, defaultparams)



def xbool(x, default = None): return default if x == None else bool(x)
def xint(x, default = None): return default if x == None else int(x)
def xfloat(x, default = None): return default if x == None else float(x)
def xstr(x, default = None): return default if x == None else str(x)



