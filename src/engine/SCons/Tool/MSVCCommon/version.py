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

import SCons.Util
import SCons.Errors
from SCons.Tool.MSVCCommon.findloc import find_bat
from SCons.Tool.MSVCCommon.vs import get_installed_visual_studios

# Default value of VS to use
DEFVERSIONSTR = "9.0"
DEFVERSION = float(DEFVERSIONSTR)

# RDEVE: currently only these flavour have been tested
SUPPORTED_ARCH = ['x86','amd64']


def query_versions():
    """Query the system to get available versions of VS. A version is
    considered when a batfile is found."""
    msvs_list = get_installed_visual_studios()
    # TODO(1.5)
    #versions = [ msvs.version for msvs in msvs_list ]
    versions = map(lambda msvs:  msvs.version, msvs_list)
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
        # TODO(1.5):
        #v = [str(i) for i in query_versions()]
        v = map(str, query_versions())
        if v:
            versions = v
        env['MSVS'] = {'VERSIONS' : versions}
    else:
        versions = env['MSVS'].get('VERSIONS', versions)

    if not env.has_key('MSVS_VERSION'):
        env['MSVS_VERSION'] = versions[0] #use highest version by default

    env['MSVS']['VERSION'] = env['MSVS_VERSION']

    return env['MSVS_VERSION']

def get_default_arch(env):
    """Return the default arch to use for MSVS

    if no version was requested by the user through the MSVS_ARCH environment
    variable, select x86

    Return
    ------
    arch: str
    """

    try:
      arch=env['MSVS_ARCH']
    except:
      arch='x86'

    if not arch in SUPPORTED_ARCH:
      arch='x86'

    return arch

def detect_msvs():
    """Return 1 if at least one version of MS toolchain is detected."""
    version = query_versions()
    if len(version) > 0:
        return 1
    else:
        return 0

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
