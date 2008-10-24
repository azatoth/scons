#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""This module provides helpers to find the ms-tools product
directories (compilers, sdk, etc...)."""

import os

import SCons.Util

from SCons.Tool.MSVCCommon.common import  read_reg, debug
from SCons.Tool.MSVCCommon.common import  SUPPORTED_VERSIONS, VSCOMNTOOL_VARNAME

# How to look for .bat file ?
#  - VS 2008 Express (x86):
#     * from registry key productdir, gives the full path to vsvarsall.bat. In
#     HKEY_LOCAL_MACHINE):
#         Software\Microsoft\VCEpress\9.0\Setup\VC\productdir
#     * from environmnent variable VS90COMNTOOLS: the path is then ..\..\VC
#     relatively to the path given by the variable.
#
#  - VS 2008 Express (WoW6432: 32 bits on windows x64):
#         Software\Wow6432Node\Microsoft\VCEpress\9.0\Setup\VC\productdir
#
#  - VS 2005 Express (x86):
#     * from registry key productdir, gives the full path to vsvarsall.bat. In
#     HKEY_LOCAL_MACHINE):
#         Software\Microsoft\VCEpress\8.0\Setup\VC\productdir
#     * from environmnent variable VS80COMNTOOLS: the path is then ..\..\VC
#     relatively to the path given by the variable.
#
#  - VS 2005 Express (WoW6432: 32 bits on windows x64): does not seem to have a
#  productdir ?
#
#  - VS 2003 .Net (pro edition ? x86):
#     * from registry key productdir. The path is then ..\Common7\Tools\
#     relatively to the key. The key is in HKEY_LOCAL_MACHINE):
#         Software\Microsoft\VisualStudio\7.1\Setup\VC\productdir
#     * from environmnent variable VS71COMNTOOLS: the path is the full path to
#     vsvars32.bat
#
#  - VS 98 (VS 6):
#     * from registry key productdir. The path is then Bin
#     relatively to the key. The key is in HKEY_LOCAL_MACHINE):
#         Software\Microsoft\VisualStudio\6.0\Setup\VC98\productdir

_VS_STANDARD_HKEY_ROOT = r"Software\Microsoft\VisualStudio\%0.1f"
_VS_EXPRESS_HKEY_ROOT = r"Software\Microsoft\VCExpress\%0.1f"

def pdir_from_reg(version, flavor = 'std'):
    """Try to find the  product directory from the registry.

    Return None if failed or the directory does not exist"""
    if not SCons.Util.can_read_reg:
        debug('SCons cannot read registry')
        return None

    if flavor == 'std':
        vsbase = _VS_STANDARD_HKEY_ROOT % version
    elif flavor == 'express':
        vsbase = _VS_EXPRESS_HKEY_ROOT % version
    else:
        raise ValueError("Flavor %s not understood" % flavor)

    try:
        if version >= 7:
            comps = read_reg(vsbase + '\Setup\VC\productdir')
        else:
            comps = read_reg(vsbase + '\Setup\Microsoft Visual C++\productdir')
        debug('Found product dir in registry: %s' % comps)
    except WindowsError, e:
        debug('Did not find product dir key %s in registry' % \
              (vsbase + '\Setup\VC\productdir'))
        return None

    if 7 <= version < 8:
        comps = os.path.join(comps, os.pardir, "Common7", "Tools")
    elif version < 7:
        comps = os.path.join(comps, "Bin")

    if not os.path.exists(comps):
        debug('%s is not found on the filesystem' % comps)
        return None

    return comps

def pdir_from_env(version):
    """Try to find the  product directory from the environment.

    Return None if failed or the directory does not exist"""
    key = VSCOMNTOOL_VARNAME[version]
    d = os.environ.get(key, None)

    def get_pdir():
        ret = None
        if version >= 8:
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

    return p

def find_varbat(version, flavor = 'std', batname = 'vcvarsall.bat'):
    pdir = find_vcbat_dir(version, flavor)
    if pdir is None:
        return None

    batfile = os.path.join(pdir, batname)
    if os.path.isfile(batfile):
        return batfile
    else:
        debug("%s file not on file system" % batfile)
        return None

def find_bat(version, flavor = 'std'):
    # On version < 8, there is not compilation to anything but x86, so use
    # vars32.bat. On higher versions, cross compilation is possible, so use the
    # varsall.bat. AFAIK, those support any cross-compilation depending on the
    # argument given.
    if version < 7:
        return find_varbat(version, flavor, 'vcvars32.bat')
    elif version < 8:
        return find_varbat(version, flavor, 'vsvars32.bat')
    else:
        return find_varbat(version, flavor, 'vcvarsall.bat')

def find_msvs_paths(version, flavor):
    paths = {}

    pdir = find_vcbat_dir(version, flavor)
    if pdir:
        paths['VCINSTALLDIR'] = os.path.normpath(pdir)
        paths['VSINSTALLDIR'] = os.path.normpath(os.path.join(pdir, os.pardir))

    return paths
