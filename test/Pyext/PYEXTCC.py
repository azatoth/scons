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

test = TestSCons.TestSCons()

if sys.platform == 'win32':

    test.write('mypyextcc.py', r"""
import sys
args = sys.argv[1:]
inf = None
while args:
    a = args[0]
    args = args[1:]
    if a[0] != '/':
        if not inf:
            inf = a
        continue
    if a[:3] == '/Fo': out = a[3:]
infile = open(inf, 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:11] != '/*pyextcc*/':
        outfile.write(l)
sys.exit(0)
""")

else:

    test.write('mypyextcc.py', r"""
import getopt
import sys
opts, args = getopt.getopt(sys.argv[1:], 'co:I:f:')
for opt, arg in opts:
    if opt == '-o': out = arg
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:11] != '/*pyextcc*/':
        outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools = ['default', 'pyext'],
                  PYEXTCC = r'%(_python_)s mypyextcc.py',
                  SHOBJSUFFIX = '.obj')
env.PythonObject(target = 'test1', source = 'test1.c')
""" % locals())

test.write('test1.c', r"""This is a .c file.
/*pyextcc*/
""")

test.run(arguments = '.', stderr = None)

test.must_match('test1.obj', "This is a .c file.\n")

test.pass_test()

