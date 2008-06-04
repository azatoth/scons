"""SCons.Tool.allow_undefined

This is NOT a tool.
"""

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

import os

from subprocess import Popen, PIPE

def get_darwin_version():

	p = Popen(["sw_vers", "-productVersion"], stdout = PIPE, stderr = PIPE)
	st = p.wait()
	if st:
		raise RuntimeError(
                "Could not execute sw_vers -productVersion to get version")

	verstring = p.stdout.next()
	a, b, c = verstring.split(".")
	try:
		major = int(a)
		minor = int(b)
		micro = int(c)

		return major, minor, micro
	except ValueError:
		raise ValueError("Could not parse version string %s" % verstring)

def get_darwin_allow_undefined():
    """Return the list of flags to allow undefined symbols in a shared library.

    On MAC OS X, takes MACOSX_DEPLOYMENT_TARGET into account."""
    major, minor, micro = get_darwin_version()
    if major == 10:
        if minor < 3:
            flag = ["-Wl,-undefined", "-Wl,suppress"]
        else:
            try:
                deptarget = os.environ['MACOSX_DEPLOYMENT_TARGET']
                ma, mi = deptarget.split(".")
                if int(mi) < 3:
                    flag = ['-Wl,-flat_namespace', '-Wl,-undefined', '-Wl,suppress']
                else:
                    flag = ['-Wl,-undefined', '-Wl,dynamic_lookup']
            except KeyError:
                flag = ['-Wl,-flat_namespace', '-Wl,-undefined', '-Wl,suppress']
    else:
        # Unknown version of mac os x ? Just set to empty list
        flag = []

    return flag
