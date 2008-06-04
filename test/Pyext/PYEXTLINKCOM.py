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

import sys
import TestSCons

from fakecc import get_fakecmd

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

test.write('mypyextcc.py', get_fakecmd(nokeep = "/*pyextcc*/"))
test.write('mypyextlink.py', get_fakecmd(nokeep = "/*pyextlink*/"))

test.write('SConstruct', """
env = Environment(tools = ['default', 'pyext'],
                  PYEXTLINKCOM = r'%(_python_)s mypyextlink.py -o $TARGET $SOURCE',
                  PYEXTCCCOM = r'%(_python_)s mypyextcc.py -o $TARGET $SOURCE',
                  PYEXTSUFFIX = '.yo')
env.PythonObject(target = 'test1.obj', source = 'test1.c')
env.PythonExtension(target = 'test1', source = 'test1.obj')
""" % locals())

test.write('test1.c', r"""This is a python .c file.
/*pyextcc*/
/*pyextlink*/
""")

test.run(arguments = '.', stderr = None)

test.must_match('test1.yo', "This is a python .c file.\n")

test.pass_test()

