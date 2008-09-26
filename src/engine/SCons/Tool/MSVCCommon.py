import os
from os.path import exists as pexists
import subprocess
import re

import SCons.Platform.win32
import SCons.Errors

from SCons.Util import can_read_reg
from SCons.Util import RegGetValue, RegError
import SCons.Util

_VS_STANDARD_HKEY_ROOT = r"Software\Microsoft\VisualStudio\%0.1f"
_VS_EXPRESS_HKEY_ROOT = r"Software\Microsoft\VCExpress\%0.1f"

# Default value of VS to use
DEFVERSION = 9.0

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
    dkeep = dict([(i, []) for i in keep])
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
    if not pexists(path):
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
            for v in [9.0, 8.0, 7.1, 7.0]:
                batfilename = FindMSVSBatFile(v)
                if batfilename is not None:
                    break
            if batfilename is None:
                raise IOError("No batfile for default version was found")
        else:
            batfilename = FindMSVSBatFile(version)
            if batfilename is None:
                raise IOError("batfile for version %s not found" % version)

    vars = ParseBatFile(batfilename, vars)
    for k, v in vars.items():
        env.PrependENVPath(k, v, delete_existing=1)

def generate(env):
    from logging import basicConfig, DEBUG
    basicConfig(level = DEBUG)

    for flavor in ['std', 'express']:
        for v in [9.]:
            try:
                vars = varbat_variables(v, flavor)
                for k, v in vars.items():
                    print k, v
            except IOError:
                pass

def exists(env):
    return 1
