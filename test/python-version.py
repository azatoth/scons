#!/usr/bin/env python
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

"""
Verify the behavior of our check for unsupported or deprecated versions
of Python.
"""

import re
import string
import sys

import TestCmd
import TestSCons

test = TestSCons.TestSCons(match = TestCmd.match_re_dotall)

test.write('SConstruct', "\n")

test.write('SetOption', "SetOption('warn', 'no-python-version')\n")

python_version = string.split(sys.version)[0]
python_major_version = python_version[:3]

if python_major_version in ():

    error = "scons: \*\*\* SCons version \S+ does not run under Python version %s."
    error = error % re.escape(python_version) + "\n"
    test.run(arguments = '-Q', status = 1, stderr = error)

elif python_major_version in ('1.5', '2.0', '2.1'):

    import os

    sconsflags = os.environ.get('SCONSFLAGS')
    if sconsflags:
        sconsflags = string.replace(sconsflags, '--warn=no-python-version', '')
        os.environ['SCONSFLAGS'] = sconsflags

    warn = "\nscons: warning: Support for Python version %s will be deprecated in a future release.\n"
    warn = warn % re.escape(python_version)
    test.run(arguments = '-Q', stderr = warn + TestSCons.file_expr)

    test.run(arguments = '-f SetOption -Q')

else:

    test.run(arguments = '-Q')

    test.run(arguments = '-f SetOption -Q')

test.pass_test()
