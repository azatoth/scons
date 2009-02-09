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

from SCons.Tool.MSVCCommon.findloc import find_bat

def get_def_env(version, flavor, vsinstalldir, arch="x86"):
    # raise a ValueError for unsuported version/flavor/arch

    # XXX: handle Windows SDK dir
    defenv = {}
    if version == 9.0:
        if flavor == 'express' or flavor == 'std':
            if arch == "x86":
                vcinstalldir = r"%s\VC" % vsinstalldir
                devenvdir = r"%s\Common7\IDE" % vsinstalldir

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
        pdir = os.path.dirname(pdir)
        pdir = os.path.normpath(os.path.join(pdir, os.pardir))
        d = get_def_env(version, flavor, pdir)
        for k, v in d.items():
            env.PrependENVPath(k, v, delete_existing=1)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
