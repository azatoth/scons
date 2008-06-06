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
Test that the --debug=memory option works.
"""

import TestSCons
import sys
import string
import re
import time

test = TestSCons.TestSCons()

test.write('SConstruct', """
def cat(target, source, env):
    open(str(target[0]), 'wb').write(open(str(source[0]), 'rb').read())
env = Environment(BUILDERS={'Cat':Builder(action=Action(cat))})
env.Cat('file.out', 'file.in')
""")

test.write('file.in', "file.in\n")

test.run(arguments = '--debug=heapmonitor')

lines = string.split(test.stdout(), '\n')

resz = r' *\d+[.]?\d* +(B|KB|MB|GB|TB) *'

pendbuild = re.compile(r'scons: done building targets.')
pstartsum = re.compile(r'-* SUMMARY -*')
pendsum = re.compile(r'-{70,79}')

pinst = re.compile(r'[\w,.]{1,32} ')
pts = re.compile(r'  \d\d:\d\d:\d\d[.]\d\d +(%s|finalize)' % resz)
psum = re.compile(r'[\w,.]* +\d+ Alive +\d+ Free +%s' % resz)

numclasses = 0
numts = 1
numinst = 0
phase = 0
phase_inst = 1
phase_sum = 2

for l in lines:
    if phase == 0:
        if pendbuild.match(l) is not None:
            phase = phase_inst
    elif phase == phase_inst:
        if pstartsum.match(l) is not None:
            phase = phase_sum
        elif pinst.match(l) is not None:
            if numts == 0:
                test.fail_test('Instance without size information')
            numts = 0
            numinst += 1
        elif pts.match(l) is not None:
            numts += 1
        else:
            test.fail_test('Unexpected output')
    elif phase == phase_sum:
        if pendsum.match(l) is not None:
            break
        test.fail_test(psum.match(l) is None)
        numclasses += 1

test.fail_test(numinst == 0)
test.fail_test(numclasses == 0)

test.pass_test()
