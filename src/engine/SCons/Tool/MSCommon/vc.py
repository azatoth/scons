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

__doc__ = """Module for Visual C/C++ detection and configuration.
"""

import os

import common

class VisualC:
    """
    An base class for finding installed versions of Visual C/C++.
    """
    def __init__(self, version, **kw):
        self.version = version
        self.__dict__.update(kw)

    def vcbin_arch(self):
        if common.is_win64():
            result = {
                'x86_64' : ['amd64', r'BIN\x86_amd64'],
                'ia64' : [r'BIN\ia64'],
            }.get(target_arch, [])
        else:
            result = {
                'x86_64' : ['x86_amd64'],
                'ia64' : ['x86_ia64'],
            }.get(target_arch, [])
        # TODO(1.5)
        #return ';'.join(result)
        return string.join(result, ';')

    #

    batch_file_map = {
        # Indexed by (target_architecture, host_architecture).
        ('x86_64', 'x86') : [
            r'bin\x86_amd64\vcvarsx86_amd64.bat',
        ],
        ('x86_64', 'x86') : [
            r'bin\ia64\vcvarsia64.bat',
            r'bin\x86_ia64\vcvarsx86_ia64.bat',
        ],
        ('x86_64', 'x86_64') : [
            r'bin\amd64\vcvarsamd64.bat',
            r'bin\x86_amd64\vcvarsx86_amd64.bat',
        ],
        ('ia64', 'ia64') : [
            r'bin\x86_ia64\vcvarsx86_ia64.bat',
        ],
        ('x86', 'x86') : [
            r'bin\vcvars32.bat',
        ],
    }

    def find_batch_file(self):
        key = (target_architecture, host_architecture)
        potential_batch_files = self.batch_file_map.get(key)
        if potential_batch_files:
            product_dir = self.msvc_root_dir()
            for batch_file in potential_batch_files:
                bf = os.path.join(product_dir, batch_file)
                if os.path.isfile(bf):
                    return bf
        return None

    #

    def get_batch_file(self):
        try:
            return self._cache['batch_file']
        except KeyError:
            executable = self.find_batch_file()
            self._cache['batch_file'] = batch_file
            return batch_file
        

# The list of supported Visual C/C++ versions we know how to detect.
#
# The first VC found in the list is the one used by default if there
# are multiple VC installed.  Barring good reasons to the contrary,
# this means we should list VC with from most recent to oldest.
#
# If you update this list, update the documentation in Tool/vc.xml.
SupportedVisualCList = [
    VisualC('9.0',
            hkey_root=[
                r'Software%sMicrosoft\VisualStudio\9.0\Setup\VC\ProductDir',
                r'Software%sMicrosoft\VCExpress\9.0\Setup\VC\ProductDir',
            ],
            default_install=r'Microsoft Visual Studio 9.0\VC',
            common_tools_var='VS90COMNTOOLS',
            vc_sub_dir='VC\\',
            batch_file_base='vcvars',
            supported_arch=['x86', 'x86_64', 'ia64'],
            atlmc_include_subdir = [r'ATLMFC\INCLUDE'],
            atlmfc_lib_subdir = {
                'x86'       : r'ATLMFC\LIB',
                'x86_64'    : r'ATLMFC\LIB\amd64',
                'ia64'      : r'ATLMFC\LIB\ia64',
            },
            crt_lib_subdir = {
                'x86_64'    : r'LIB\amd64',
                'ia64'      : r'LIB\ia64',
            },
    ),
    VisualC('8.0',
            hkey_root=[
                r'Software%sMicrosoft\VisualStudio\8.0\Setup\VC\ProductDir',
                r'Software%sMicrosoft\VCExpress\8.0\Setup\VC\ProductDir',
            ],
            default_install=r'%s\Microsoft Visual Studio 8\VC',
            common_tools_var='VS80COMNTOOLS',
            vc_sub_dir='VC\\',
            batch_file_base='vcvars',
            supported_arch=['x86', 'x86_64', 'ia64'],
            atlmc_include_subdir = [r'ATLMFC\INCLUDE'],
            atlmfc_lib_subdir = {
                'x86'       : r'ATLMFC\LIB',
                'x86_64'    : r'ATLMFC\LIB\amd64',
                'ia64'      : r'ATLMFC\LIB\ia64',
            },
            crt_lib_subdir = {
                'x86_64'    : r'LIB\amd64',
                'ia64'      : r'LIB\ia64',
            },
    ),
    VisualC('7.1',
            hkey_root=[
                r'Software%sMicrosoft\VisualStudio\7.1\Setup\VC\ProductDir',
            ],
            default_install=r'%s\Microsoft Visual Studio 7.1.NET 2003\VC7',
            common_tools_var='VS71COMNTOOLS',
            vc_sub_dir='VC7\\',
            batch_file_base='vcvars',
            supported_arch=['x86'],
            atlmc_include_subdir = [r'ATLMFC\INCLUDE'],
            atlmfc_lib_subdir = {
                'x86' : r'ATLMFC\LIB',
            },
    ),
    VisualC('7.0',
            hkey_root=[
                r'Software%sMicrosoft\VisualStudio\7.0\Setup\VC\ProductDir',
            ],
            default_install=r'%s\Microsoft Visual Studio .NET\VC7',
            common_tools_var='VS70COMNTOOLS',
            vc_sub_dir='VC7\\',
            batch_file_base='vcvars',
            supported_arch=['x86'],
            atlmc_include_subdir = [r'ATLMFC\INCLUDE'],
            atlmfc_lib_subdir = {
                'x86' : r'ATLMFC\LIB',
            },
    ),
    VisualC('6.0',
            hkey_root=[
                r'Software%sMicrosoft\VisualStudio\6.0\Setup\Microsoft Visual C++\ProductDir',
            ],
            default_install=r'%s\Microsoft Visual Studio\VC98',
            common_tools_var='VS60COMNTOOLS',
            vc_sub_dir='VC98\\',
            batch_file_base='vcvars',
            supported_arch=['x86'],
            atlmc_include_subdir = [r'ATL\INCLUDE', r'MFC\INCLUDE'],
            atlmfc_lib_subdir = {
                'x86' : r'MFC\LIB',
            },
    ),
]

SupportedVCMap = {}
for vc in SupportedVCList:
    SupportedVCMap[vc.version] = vc


# Finding installed versions of Visual C/C++ isn't cheap, because it goes
# not only to the registry but also to the disk to sanity-check that there
# is, in fact, something installed there and that the registry entry isn't
# just stale.  Find this information once, when requested, and cache it.

InstalledVCList = None
InstalledVCMap = None

def get_installed_vcs():
    global InstalledVCList
    global InstalledVCMap
    if InstalledVCList is None:
        InstalledVCList = []
        InstalledVCMap = {}
        for vc in SupportedVCList:
            debug('trying to find VC %s' % vc.version)
            if vc.get_vc_dir():
                debug('found VC %s' % vc.version)
                InstalledVCList.append(vc)
                InstalledVCMap[vc.version] = vc
    return InstalledVCList


def detect_vc(version=None):
    vcs = get_installed_vcs()
    if version is None:
        return len(vcs) > 0
    return vcs.has_key(version)

def set_vc_by_version(env, msvc):
    if not SupportedVCMap.has_key(msvc):
        msg = "VC version %s is not supported" % repr(msvc)
        raise SCons.Errors.UserError, msg
    get_installed_vcs()
    vc = InstalledVCMap.get(msvc)
    if not vc:
        msg = "VC version %s is not installed" % repr(msvc)
        raise SCons.Errors.UserError, msg
    set_vc_by_directory(env, vc.get_vc_dir())

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
