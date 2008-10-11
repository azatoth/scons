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
from os.path import join as pjoin, dirname as pdirname, \
                    normpath as pnormpath, exists as pexists
import re
import subprocess
import copy

import SCons.Errors
import SCons.Platform.win32
import SCons.Util

from SCons.Tool.MSVCCommon.findloc import find_bat
from SCons.Tool.MSVCCommon.common import debug

# Default value of VS to use
DEFVERSIONSTR = "9.0"
DEFVERSION = float(DEFVERSIONSTR)

_SUPPORTED_VERSIONS = [9.0, 8.0, 7.1, 7.0, 6.0]
_SUPPORTED_VERSIONSSTR = [str(i) for i in _SUPPORTED_VERSIONS]

_VSCOMNTOOL_VARNAME = dict([(v, 'VS%dCOMNTOOLS' % round(v * 10))
                            for v in _SUPPORTED_VERSIONS])

def normalize_env(env, keys):
    """Given a dictionary representing a shell environment, add the variables
    from os.environ needed for the processing of .bat files; the keys are
    controlled by the keys argument.

    It also makes sure the environment values are correctly encoded.
    
    Note: the environment is copied"""
    normenv = {}
    if env:
        for k in env.keys():
            normenv[k] = copy.deepcopy(env[k]).encode('mbcs')

        for k in keys:
            if os.environ.has_key(k):
                normenv[k] = os.environ[k].encode('mbcs')

    return normenv

def get_output(vcbat, args = None, env = None):
    """Parse the output of given bat file, with given args."""
    if args:
        debug("Calling '%s %s'" % (vcbat, args))
        popen = subprocess.Popen('"%s" %s & set' % (vcbat, args),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env=env)
    else:
        debug("Calling '%s'" % vcbat)
        popen = subprocess.Popen('"%s" & set' % vcbat,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env=env)

    stdout, stderr = popen.communicate()
    if popen.wait() != 0:
        raise IOError(stderr.decode("mbcs"))

    output = stdout.decode("mbcs")
    return output

# You gotta love this: they had to set Path instead of PATH...
# (also below we search case-insensitively because VC9 uses uppercase PATH)
_ENV_TO_T = {"INCLUDE": "INCLUDE", "PATH": "PATH",
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
        # XXX: the _ENV_TO_T indirection may not be necessary anymore. Check
        # this
        if _ENV_TO_T.has_key(i):
            rdk[i] = re.compile('%s=(.*)' % _ENV_TO_T[i], re.I)
        else:
            rdk[i] = re.compile('%s=(.*)' % i, re.I)

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

def output_to_dict(output):
    """Given an output string, parse it to find env variables.
    
    Return a dict where keys are variables names, and values their content"""
    envlinem = re.compile(r'^([a-zA-z0-9]+)=([\S\s]*)$')
    parsedenv = {}
    for line in output.splitlines():
        m = envlinem.match(line)
        if m:
            parsedenv[m.group(1)] = m.group(2)
    return parsedenv

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

def query_versions():
    """Query the system to get available versions of VS. A version is
    considered when a batfile is found."""
    versions = []
    # We put in decreasing order: versions itself should be in drecreasing
    # order
    for v in _SUPPORTED_VERSIONS:
        bat = find_bat(v)
        if bat is not None:
            versions.append(v)

    return versions

def get_default_version(env):
    """Return the default version to use for MSVS

    if no version was requested by the user through the MSVS environment
    variable, query all the available the visual studios through
    query_versions, and take the highest one.

    Return
    ------
    version: str
        the default version."""
    versions = [DEFVERSIONSTR]

    if not env.has_key('MSVS') or not SCons.Util.is_Dict(env['MSVS']):
        v = [str(i) for i in query_versions()]
        if v:
            versions = v
        env['MSVS'] = {'VERSIONS' : versions}
    else:
        versions = env['MSVS'].get('VERSIONS', versions)

    if not env.has_key('MSVS_VERSION'):
        env['MSVS_VERSION'] = versions[0] #use highest version by default

    env['MSVS']['VERSION'] = env['MSVS_VERSION']

    return env['MSVS_VERSION']

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

def ParseBatFile(env, path, vars=['INCLUDE', 'LIB', 'LIBPATH', 'PATH'], args=None):
    """Returns a dict of var/value pairs by running the batch file
    and looking at the resulting environment variables.

    Arguments
    ---------
    env: Environment
        scons environment instance. Is used to provide an environment to
        execute the bat file during parsing.
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
    nenv = normalize_env(env['ENV'], _VSCOMNTOOL_VARNAME.values() + ['COMSPEC'])
    output = get_output(path, args, env=nenv)

    return parse_output(output, vars)
    #parsed = parse_output(output, vars)
    #ret = {}
    #for k in parsed.keys():
    #    if os.environ.has_key(k):
    #       p = os.environ[k].split(os.pathsep)
    #       ret[k] = get_new(p, parsed[k])
    #    else:
    #       ret[k] = parsed[k]

    #return ret

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

    vars = ParseBatFile(env, batfilename, vars)

    for k, v in vars.items():
        env.PrependENVPath(k, v, delete_existing=1)

def merge_default_version(env):
    try:
        version = get_default_version(env)
        if version is not None:
            version_num, suite = SCons.Tool.msvs.msvs_parse_version(version)
            if env.has_key('MSVS_USE_DEFAULT_PATHS') and \
               env['MSVS_USE_DEFAULT_PATHS']:
                use_def_env(env, version_num, 'std')
                try:
                    use_def_env(env, version_num, 'std')
                except ValueError, e:
                    print "Could not get defaultpaths: %s" % e
                    MergeMSVSBatFile(env, version_num)

            else:
                MergeMSVSBatFile(env, version_num)
        else:
            MergeMSVSBatFile(env)

    except SCons.Errors.MSVCError:
        pass


def detect_msvs():
    version = query_versions()
    if len(version) > 0:
        return 1
    else:
        return 0

def get_def_env(version, flavor, vsinstalldir, arch="x86"):
    # raise a ValueError for unsuported version/flavor/arch

    # XXX: handle Windows SDK dir
    defenv = {}
    if version == 9.0:
        if flavor == 'express' or flavor == 'std':
            if arch == "x86":
                vcinstalldir = r"%s\VC" % vsinstalldir
                devenvdir = r"%s\Common7\IDE" % vsinstalldir
                sdkdir = get_cur_sdk_dir_from_reg()

                if sdkdir:
                    paths = [pjoin(sdkdir, 'bin')]
                    lib = [pjoin(sdkdir, 'lib')]
                    include = [pjoin(sdkdir, 'include')]
                else:
                    paths = []
                    lib = []
                    include = []

                paths.append(devenvdir)
                paths.append(r"%s\BIN" % vcinstalldir)
                paths.append(r"%s\Common7\Tools" % vsinstalldir)
                # XXX Handle FRAMEWORKDIR and co
                paths.append(r"%s\VCPackages" % vcinstalldir)
                defenv['PATH'] = os.pathsep.join(paths)

                include.append(r'%s\ATLMFC\INCLUDE' % vcinstalldir)
                include.append(r'%s\INCLUDE' % vcinstalldir)
                defenv['INCLUDE'] = os.pathsep.join(include)

                lib.append(r'%s\ATLMFC\LIB' % vcinstalldir)
                lib.append(r'%s\LIB' % vcinstalldir)
                defenv['LIB'] = os.pathsep.join(lib)

                libpath = [r'%s\ATLMFC\LIB' % vcinstalldir]
                libpath.append(r'%s\LIB' % vcinstalldir)
                defenv['LIBPATH'] = os.pathsep.join(libpath)
            else:
                raise ValueError("arch %s not supported" % arch)
        else:
            raise ValueError("flavor %s for version %s not "\
                             "understood" % (flavor, version))
    else:
        raise ValueError("version %s not supported" % version)

    return defenv

def use_def_env(env, version, flavor, arch="x86"):
    pdir = find_bat(version, flavor)
    if not pdir:
        raise ValueError("bat file not found")
    else:
        pdir = pdirname(pdir)
        pdir = pnormpath(pjoin(pdir, os.pardir))
        d = get_def_env(version, flavor, pdir)
        for k, v in d.items():
            env.PrependENVPath(k, v, delete_existing=1)
