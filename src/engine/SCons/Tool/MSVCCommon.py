import os
import subprocess
import re

import SCons.Platform.win32
import SCons.Errors

from SCons.Util import can_read_reg
from SCons.Util import RegGetValue, RegError
import SCons.Util

_VS_STANDARD_HKEY_ROOT = r"Software\Microsoft\VisualStudio\%0.1f"
_VS_EXPRESS_HKEY_ROOT = r"Software\Microsoft\VCExpress\%0.1f"

try:
    from logging import debug
except ImportError:
    debug = lambda x : None

def read_reg(value):
    return RegGetValue(SCons.Util.HKEY_LOCAL_MACHINE, value)[0]
    
def pdir_from_reg(version, flavor = 'std'):
    """Try to find the  product directory from the registry.

    Return None if failed or the directory does not exist"""
    if not can_read_reg:
        debug('SCons cannot read registry')
        return None

    if flavor == 'std':
        vsbase = _VS_STANDARD_HKEY_ROOT % version
    elif flavor == 'express':
        vsbase = _VS_EXPRESS_HKEY_ROOT % version
    else:
        return ValueError("Flavor %s not understood" % flavor)

    try:
        comps = read_reg(vsbase + '\Setup\VC\productdir')
        debug('Found product dir in registry: %s' % comps)
    except WindowsError, e:
        debug('Did not find product dir key %s in registry' % (vsbase + '\Setup\VC\productdir'))
        return None

    if not os.path.exists(comps):
        debug('%s is not found on the filesystem' % comps)
        return None

    return comps

def pdir_from_env(version):
    """Try to find the  product directory from the environment.

    Return None if failed or the directory does not exist"""
    key = "VS%0.f0COMNTOOLS" % version
    d = os.environ.get(key, None)

    def get_pdir():
        ret = None
        if 7 <= version < 8:
            ret = os.path.join(d, os.pardir, "Common7", "Tools")
        elif version >= 8:
            ret = os.path.join(d, os.pardir, os.pardir, "VC")
        return ret

    pdir = None
    if d and os.path.isdir(d):
        debug('%s found from %s' % (d, key))
        pdir = get_pdir()

    return pdir


def find_vcbat_dir(version, flavor = 'std'):
    debug("Looking for productdir %s, flavor %s" % (version, flavor))
    p = pdir_from_reg(version, flavor)
    if not p:
        p = pdir_from_env(version)
        if not p:
            raise IOError("No productdir found")

    return p

def generate(env):
    from logging import basicConfig, DEBUG
    basicConfig(level = DEBUG)
    
    for flavor in ['std', 'express']:
        for v in [9.]:
            try:
                find_vcbat_dir(v, flavor)
            except IOError:
                pass

def exists(env):
    return 1
