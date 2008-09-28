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

__doc__ = """
Common functions for Microsoft Visual Studio and Visual C/C++.
"""

import os
import re
import subprocess

import SCons.Errors
import SCons.Platform.win32
import SCons.Util

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

_VS_STANDARD_HKEY_ROOT = r"Software\Microsoft\VisualStudio\%0.1f"
_VS_EXPRESS_HKEY_ROOT = r"Software\Microsoft\VCExpress\%0.1f"

# Default value of VS to use
DEFVERSION = 9.0

try:
    from logging import debug
except ImportError:
    debug = lambda x : None

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
        comps = read_reg(vsbase + '\Setup\VC\productdir')
        debug('Found product dir in registry: %s' % comps)
    except WindowsError, e:
        debug('Did not find product dir key %s in registry' % \
              (vsbase + '\Setup\VC\productdir'))
        return None

    # XXX: it this necessary for VS .net only, or because std vs
    # express ?
    if 7 <= version < 8:
        comps = os.path.join(comps, os.pardir, "Common7", "Tools")

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

def find_vsvars32(version, flavor = 'std'):
    pdir = find_vcbat_dir(version, flavor)
    if pdir is None:
        return None

    vsvars32 = os.path.join(pdir, "vsvars32.bat")
    if os.path.isfile(vsvars32):
        return vsvars32
    else:
        debug("%s file not on file system" % vsvars32)
        return None

def find_vcvarsall(version, flavor = 'std'):
    pdir = find_vcbat_dir(version, flavor)
    if pdir is None:
        return None

    vcvarsall = os.path.join(pdir, "vcvarsall.bat")
    if os.path.isfile(vcvarsall):
        return vcvarsall
    else:
        debug("%s file not on file system" % vcvarsall)
        return None

def find_bat(version, flavor = 'std'):
    # On version < 8, there is not compilation to anything but x86, so use
    # vars32.bat. On higher versions, cross compilation is possible, so use the
    # varsall.bat. AFAIK, those support any cross-compilation depending on the
    # argument given.
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

# You gotta love this: they had to set Path instead of PATH...
_ENV_TO_T = {"INCLUDE": "INCLUDE", "PATH": "Path",
             "LIB": "LIB", "LIBPATH": "LIBPATH"}

def parse_output(output, keep = ("INCLUDE", "LIB", "LIBPATH", "PATH")):
    # dkeep is a dict associating key: path_list, where key is one item from
    # keep, and pat_list the associated list of paths

    # TODO(1.5):  replace with the following list comprehension:
    #dkeep = dict([(i, []) for i in keep])
    dkeep = dict(map(lambda i: (i, []), keep))

    # rdk will  keep the regex to match the .bat file output line starts
    rdk = {}
    for i in keep:
        rdk[i] = re.compile('%s=(.*)' % _ENV_TO_T[i])

    def add_env(rmatch, key):
        plist = rmatch.group(1).split(os.pathsep)
        for p in plist:
            # Do not add empty paths (when a var ends with ;)
            if p:
                dkeep[key].append(p)

    for line in output.splitlines():
        for k,v in rdk.items():
            m = v.match(line)
            if m:
                add_env(m, k)

    return dkeep

def get_new(l1, l2):
    """Given two list l1 and l2, return the items in l2 which are not in l1.
    Order is maintained."""

    # We don't try to be smart: lists are small, and this is not the bottleneck
    # is any case
    new = []
    for i in l2:
        if i not in l1:
            new.append(i)

    return new

def varbat_variables(version, flavor = 'std', arch = 'x86'):
    """Return a dictionary where the keys are the env variables and the values
    the list of paths.

    Note: only return the paths which were added by the .bat file, to avoid
    polluting the env with all the content of PATH."""
    file = find_bat(version, flavor)
    if file is None:
        raise IOError("bar file for version %s, flavor %s not found" \
                      % (version, flavor))

    # XXX version < 8 does not handle cross compilation ?
    if version < 8:
        out = get_output(file)
        parsed = parse_output(out, keep = ['INCLUDE', 'PATH', 'LIB'])
    else:
        out = get_output(file, args = arch)
        parsed = parse_output(out, keep = ['INCLUDE', 'PATH', 'LIB', 'LIBPATH'])

    ret = {}
    for k in parsed.keys():
        if os.environ.has_key(k):
           p = os.environ[k].split(os.pathsep)
           ret[k] = get_new(p, parsed[k])
        else:
           ret[k] = parsed[k]

    return ret

def FindMSVSBatFile(version, flavor='std', arch="x86"):
    """Returns the location of the MSVS bat file used to set up
    Visual Studio.  Returns None if it is not found.

    Arguments
    ---------
    version: float
        the supported version are 7.0, 7.1 (VS 2003), 8.0 (VS 2005) and 9.0
        (VS 2008)
    flavor: str
        flavor of VS: "std" and "express" are supported.
    arch: str
        only "x86" is supported.

    Note
    ----
    The bat file is search in the following order:
        - first look into the registry
        - if not found, then look into the environment variable
          VS*COMMNTOOLS"""
    if not arch in ["x86"]:
        raise ValueError("Arch different than x86 not supported yet.")

    return find_bat(version, flavor)

def FindDefaultMSVSBatFile(flavor='std', arch='x86'):
    """Return default version of .bat file, with given flavor and arch."""
    for v in [9.0, 8.0, 7.1, 7.0]:
        batfilename = FindMSVSBatFile(v)
        if batfilename is not None:
            break

    if batfilename is None:
        msg = "No batfile for default version was found"
        raise SCons.Errors.MSVCError(msg)

    return batfilename

def ParseBatFile(path, vars=['INCLUDE', 'LIB', 'LIBPATH', 'PATH'], args=None):
    """Returns a dict of var/value pairs by running the batch file
    and looking at the resulting environment variables.

    Arguments
    ---------
    path: str
        full path of the .bat file to set up VS environment (vsvarsall.bat,
        etc...)
    vars: seq
        list of variables to look for
    args: seq or None
        list of arguments to pass to the .bat file through the cmd.exe
        shell"""
    if not os.path.exists(path):
        raise ValueError("File %s does not exist on the filesystem!" % path)

    # XXX: fix args handling here. Do not use a string but a sequence to avoid
    # escaping problems, and letting Popen taking care of it for us.
    output = get_output(path, args, vars)

    parsed = parse_output(output, vars)
    ret = {}
    for k in parsed.keys():
        if os.environ.has_key(k):
           p = os.environ[k].split(os.pathsep)
           ret[k] = get_new(p, parsed[k])
        else:
           ret[k] = parsed[k]

    return ret

def get_required_version(env):
    if not env.has_key('MSVS') or not SCons.Util.is_Dict(env['MSVS']):
        return None

def MergeMSVSBatFile(env, version=None, batfilename=None,
                     vars=["INCLUDE", "LIB", "LIBPATH", "PATH"]):
    """Find MSVC/MSVS bat file for given version, run it and parse the result
    to update the environment.

    If batfilename is given, it will be used. If not give, the .bat file
    corresponding to the given version will be used. If the batfile does not
    exists or is not found, an exception will be raised.

    Arguments
    ---------
    env: Environment
        the scons Environment instance to update
    version: float or None
        version of MSVS to use. If None, a list of versions will be looked
        for, and the first found will be used.
    batfilename: str
        .bat file to use.

    Note
    ----
    When version is None, the following versions are looked for, in that order:
    9.0, 8.0, 7.1, 7.0.

    Examples
    --------
    # Put the necessary variables from VS studio: the first version found
    # will be used
    MergeMSVSBatFile(env)
    # Put the necessary variables from VS 2008
    MergeMSVSBatFile(env, 9.0)
    # Put the necessary variables from the file vcbatfile.bat
    MergeMSVSBatFile(env, batfilename='vcbatfile.bat')
    """
    if not batfilename:
        if version is None:
            batfilename = FindDefaultMSVSBatFile()
        else:
            batfilename = FindMSVSBatFile(version)
            if batfilename is None:
                msg = "batfile for version %s not found" % version
                raise SCons.Errors.MSVCError(msg)

    vars = ParseBatFile(batfilename, vars)
    for k, v in vars.items():
        env.PrependENVPath(k, v, delete_existing=1)
