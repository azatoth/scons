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

# Uncomment to enable debug logging to your choice of file
#import logging,os
#os.unlink('c:/tmp/debug.log')
#logging.basicConfig(filename='c:/tmp/debug.log', level=logging.DEBUG,)

try:
    from logging import debug
except ImportError:
    debug = lambda x : None

#debug = lambda x : open('con', 'w').write(x + '\n')

# TODO(sgk): unused
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

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
