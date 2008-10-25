import os

from common import read_reg, debug

_FRAMEWORKDIR_HKEY_ROOT = r'Software\Microsoft\.NETFramework\InstallRoot'

def find_framework_root():
    # XXX: find it from environment (FrameworkDir)
    try:
        froot = read_reg(_FRAMEWORKDIR_HKEY_ROOT)
        debug("Found framework install root in registry: %s" % froot)
    except WindowsError, e:
        debug("Could not read reg key %s" % _FRAMEWORKDIR_HKEY_ROOT)
        return None

    if not os.path.exists(froot)
        debug("%s not found on fs" % froot)
        return None

    return froot
