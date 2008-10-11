import SCons.Util

try:
    from logging import debug
except ImportError:
    debug = lambda x : None

SUPPORTED_VERSIONS = [9.0, 8.0, 7.1, 7.0, 6.0]
SUPPORTED_VERSIONSSTR = [str(i) for i in SUPPORTED_VERSIONS]

VSCOMNTOOL_VARNAME = dict([(v, 'VS%dCOMNTOOLS' % round(v * 10))
                           for v in SUPPORTED_VERSIONS])

def is_win64():
    """Return true if running on windows 64 bits."""
    # Unfortunately, python does not seem to have anything useful: neither
    # sys.platform nor os.name gives something different on windows running on
    # 32 bits or 64 bits. Note that we don't care about whether python itself
    # is 32 or 64 bits here
    value = "Software\Wow6432Node"
    yo = SCons.Util.RegGetValue(SCons.Util.HKEY_LOCAL_MACHINE, value)[0]
    if yo is None:
        return 0
    else:
        return 1

def read_reg(value):
    return SCons.Util.RegGetValue(SCons.Util.HKEY_LOCAL_MACHINE, value)[0]

