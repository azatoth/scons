import os
import re

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

    if not os.path.exists(froot):
        debug("%s not found on fs" % froot)
        return None

    return froot

def query_versions():
    froot = find_framework_root()
    if froot:
        os.listdir(froot)

        l = re.compile('v[0-9]+.*')
        versions = filter(lambda e, l=l: l.match(e), contents)

        def versrt(a,b):
            # since version numbers aren't really floats...
            aa = a[1:]
            bb = b[1:]
            aal = string.split(aa, '.')
            bbl = string.split(bb, '.')
            # sequence comparison in python is lexicographical
            # which is exactly what we want.
            # Note we sort backwards so the highest version is first.
            return cmp(bbl,aal)

        versions.sort(versrt)
    else:
        versions = []

    return versions
