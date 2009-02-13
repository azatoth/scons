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

from SCons.Tool.MSVCCommon.common import  debug
from SCons.Tool.MSVCCommon.vs import get_vs_by_version

def find_bat(version, flavor = 'std'):
    # On version < 8, there is not compilation to anything but x86, so use
    # vars32.bat. On higher versions, cross compilation is possible, so use the
    # varsall.bat. AFAIK, those support any cross-compilation depending on the
    # argument given.
    version = str(version)
    if flavor == 'express':
        version = version + 'Exp'
    msvs = get_vs_by_version(version)
    if msvs is None:
        return None
    return msvs.get_batch_file()

def find_msvs_paths(version, flavor):
    paths = {}

    version = str(version)
    if flavor == 'express':
        version = version + 'Exp'
    msvs = get_vs_by_version(version)
    if msvs is not None:
        pdir = msvs.get_vc_product_dir()
        paths['VCINSTALLDIR'] = os.path.normpath(pdir)
        paths['VSINSTALLDIR'] = os.path.normpath(os.path.join(pdir, os.pardir))

    return paths

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
