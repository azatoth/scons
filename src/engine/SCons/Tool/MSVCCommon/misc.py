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
"""

import os

import SCons.Errors

from SCons.Tool.MSVCCommon.common import  VSCOMNTOOL_VARNAME
from SCons.Tool.MSVCCommon.version import get_default_version
from SCons.Tool.MSVCCommon.findloc import find_bat
from SCons.Tool.MSVCCommon.envhelpers import normalize_env, get_output, parse_output
from SCons.Tool.MSVCCommon.defaults import use_def_env

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
    nenv = normalize_env(env['ENV'], VSCOMNTOOL_VARNAME.values() + ['COMSPEC'])
    output = get_output(path, args, env=nenv)

    return parse_output(output, vars)

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

def set_psdk(env):
    from sdk import set_default_sdk, set_sdk

    if not env.has_key("MSSDK"):
        if env.has_key('MSVS_VERSION'):
            msver = env['MSVS_VERSION']
            set_default_sdk(env, msver)
        else:
            print "No MSVS_VERSION: this is likely to be a bug"

    elif env['MSSDK'] is not None:
        set_sdk(env, env['MSSDK'])
    else:
        pass

def merge_default_version(env):
    version = get_default_version(env)
    # TODO(SK):  move this import up top without introducing circular
    # problems with others importing merge_default_version().
    import SCons.Tool.msvs
    version_num, suite = SCons.Tool.msvs.msvs_parse_version(version)

    batfilename = FindMSVSBatFile(version_num)
    # XXX: I think this is broken. This will silently set a bogus tool instead
    # of failing, but there is no other way with the current scons tool
    # framework
    if batfilename is not None:
        vars = ('LIB', 'LIBPATH', 'PATH', 'INCLUDE')
        vars = ParseBatFile(env, batfilename, vars)

        for k, v in vars.items():
            env.PrependENVPath(k, v, delete_existing=1)

    #try:
    #    version = get_default_version(env)
    #    if version is not None:
    #        version_num, suite = SCons.Tool.msvs.msvs_parse_version(version)
    #        if env.has_key('MSVS_USE_DEFAULT_PATHS') and \
    #           env['MSVS_USE_DEFAULT_PATHS']:
    #            use_def_env(env, version_num, 'std')
    #            try:
    #                use_def_env(env, version_num, 'std')
    #            except ValueError, e:
    #                print "Could not get defaultpaths: %s" % e
    #                MergeMSVSBatFile(env, version_num)

    #        else:
    #            MergeMSVSBatFile(env, version_num)
    #    else:
    #        MergeMSVSBatFile(env)

    #except SCons.Errors.MSVCError:
    #    pass
