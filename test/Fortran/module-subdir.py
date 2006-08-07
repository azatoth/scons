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
Validate that $FORTRANMODDIR values get expanded correctly on Fortran
command lines relative to the appropriate subdirectory.
"""

import sys

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.subdir('subdir',
            ['subdir', 'src'],
            ['subdir', 'build'])

test.write('myfortran.py', r"""
import getopt
import os
import sys
comment = '#' + sys.argv[1]
length = len(comment)
opts, args = getopt.getopt(sys.argv[2:], 'cM:o:')
for opt, arg in opts:
    if opt == '-o': out = arg
    elif opt == '-M': modsubdir = arg
import os
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:7] == 'module ':
        module = modsubdir + os.sep + l[7:-1] + '.mod'
        open(module, 'wb').write('myfortran.py wrote %s\n' % module)
    if l[:length] != comment:
        outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """\
env = Environment(FORTRANMODDIRPREFIX = '-M',
                  FORTRANMODDIR = 'modules',
                  F90 = r'%(python)s myfortran.py f90',
                  FORTRAN = r'%(python)s myfortran.py fortran')
Export('env')
objs = SConscript('subdir/SConscript')
env.Library('bidule', objs)
""" % locals())

test.write(['subdir', 'SConscript'], """\
Import('env')

env['FORTRANMODDIR'] = 'build'
sources = ['src/modfile.f90']
objs = env.Object(sources)
Return("objs")
""")

test.write(['subdir', 'src', 'modfile.f90'], """\
#f90 comment
module somemodule

integer :: nothing

end module
""")


test.run(arguments = '.')

test.must_match(['subdir', 'build', 'somemodule.mod'],
                "myfortran.py wrote subdir/build/somemodule.mod\n")

test.pass_test()
