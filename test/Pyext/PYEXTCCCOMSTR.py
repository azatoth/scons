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
Test that the $PYEXTCCCOMSTR construction variable allows you to configure the
C compilation output.
"""

import sys
import TestSCons

from fakecc import get_fakecmd

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

test.write('mypyextcc.py', get_fakecmd(nokeep = "/*pyextcc*/"))

test.write('SConstruct', """
env = Environment(tools = ['default', 'pyext'],
                  PYEXTCCCOM = r'%(_python_)s mypyextcc.py -o $TARGET $SOURCE',
                  PYEXTCCCOMSTR = "YOYOYOYO $TARGET $SOURCE",
                  PYEXTOBJSUFFIX = '.obj')
env.PythonObject(target = 'test1', source = 'test1.c')
""" % locals())

test.write('test1.c', """\
test1.c
/*pyextcc*/
""")

test.run(stdout = test.wrap_stdout("""\
YOYOYOYO test1.obj test1.c
""" % locals()))

test.must_match('test1.obj', "test1.c\n")

test.pass_test()
