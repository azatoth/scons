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

def find_vsvars32(version, flavor = 'std'):
    pdir = find_vcbat_dir(version, flavor)

    vsvars32 = os.path.join(pdir, "vsvars32.bat")
    if os.path.isfile(vsvars32):
        return vsvars32
    else:
        debug("%s file not on file system" % vsvars32)
        return None

def find_vcvarsall(version, flavor = 'std'):
    pdir = find_vcbat_dir(version, flavor)

    vcvarsall = os.path.join(pdir, "vcvarsall.bat")
    if os.path.isfile(vcvarsall):
        return vcvarsall
    else:
        debug("%s file not on file system" % vcvarsall)
        return None

def find_bat(version, flavor = 'std'):
    if version < 8:
        return find_vsvars32(version, flavor)
    else:
        return find_vcvarsall(version, flavor)

def get_output(vcbat, args = None, keep = ("include", "lib", "libpath", "path")):
    """Parse the output of given bat file, with given args. Only
    take given vars in the argument keep."""
    skeep = set(keep)
    result = {}

    if args:
        debug("Calling '%s %s'" % (vcbat, args))
        popen = subprocess.Popen('"%s" %s & set' % (vcbat, args),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    else:
        debug("Calling '%s'" % vcbat)
        popen = subprocess.Popen('"%s" & set' % vcbat,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

    stdout, stderr = popen.communicate()
    if popen.wait() != 0:
        raise IOError(stderr.decode("mbcs"))

    output = stdout.decode("mbcs")
    return output

_ENV_TO_T = {"include": "INCLUDE", "path": "Path",
             "lib": "LIB", "libpath": "LIBPATH"}

def parse_output(output, keep = ("include", "lib", "libpath", "path")):
    dkeep = dict([(i, []) for i in keep])
    dk = []
    for i in keep:
        dk.append(re.compile('%s=(.*)' % _ENV_TO_T[i]))

    for i in output.splitlines():
        for j in range(len(dk)):
            m = dk[j].match(i)
            if m:
                dkeep[keep[j]].append(m.groups(0))

    ret = {}
    for k in dkeep.keys():
        ret[k.lower()] = dkeep[k]
    return ret

def generate(env):
    from logging import basicConfig, DEBUG
    basicConfig(level = DEBUG)
    
    for flavor in ['std', 'express']:
        for v in [9.]:
            try:
                file = find_bat(v, flavor)
                out = get_output(file)
                print parse_output(out)
            except IOError:
                pass

def exists(env):
    return 1
