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

import os
import string
import sys
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()



test.write('myfc.py', r"""
import sys
fline = '#'+sys.argv[1]+'\n'
outfile = open(sys.argv[2], 'wb')
infile = open(sys.argv[3], 'rb')
for l in filter(lambda l, fl=fline: l != fl, infile.readlines()):
    outfile.write(l)
sys.exit(0)
""")

if os.path.normcase('.f') == os.path.normcase('.F'):
    f77pp = 'f77'
else:
    f77pp = 'f77pp'


test.write('SConstruct', """
env = Environment(SHF77COM = r'%(_python_)s myfc.py f77 $TARGET $SOURCES',
                  SHF77COMSTR = 'Building f77 $TARGET from $SOURCES',
                  SHF77PPCOM = r'%(_python_)s myfc.py f77pp $TARGET $SOURCES',
                  SHF77PPCOMSTR = 'Building f77pp $TARGET from $SOURCES',
                  SHOBJPREFIX='', SHOBJSUFFIX='.shobj')
env.SharedObject(source = 'test01.f')
env.SharedObject(source = 'test02.F')
env.SharedObject(source = 'test03.for')
env.SharedObject(source = 'test04.FOR')
env.SharedObject(source = 'test05.ftn')
env.SharedObject(source = 'test06.FTN')
env.SharedObject(source = 'test07.fpp')
env.SharedObject(source = 'test08.FPP')
env.SharedObject(source = 'test09.f77')
env.SharedObject(source = 'test10.F77')
""" % locals())

test.write('test01.f',          "A .f file.\n#f77\n")
test.write('test02.F',          "A .F file.\n#%s\n" % f77pp)
test.write('test03.for',        "A .for file.\n#f77\n")
test.write('test04.FOR',        "A .FOR file.\n#%s\n" % f77pp)
test.write('test05.ftn',        "A .ftn file.\n#f77\n")
test.write('test06.FTN',        "A .FTN file.\n#%s\n" % f77pp)
test.write('test07.fpp',        "A .fpp file.\n#f77pp\n")
test.write('test08.FPP',        "A .FPP file.\n#f77pp\n")
test.write('test09.f77',        "A .f77 file.\n#f77\n")
test.write('test10.F77',        "A .F77 file.\n#%s\n" % f77pp)

test.run(stdout = test.wrap_stdout("""\
Building f77 test01.shobj from test01.f
Building %(f77pp)s test02.shobj from test02.F
Building f77 test03.shobj from test03.for
Building %(f77pp)s test04.shobj from test04.FOR
Building f77 test05.shobj from test05.ftn
Building %(f77pp)s test06.shobj from test06.FTN
Building f77pp test07.shobj from test07.fpp
Building f77pp test08.shobj from test08.FPP
Building f77 test09.shobj from test09.f77
Building %(f77pp)s test10.shobj from test10.F77
""" % locals()))

test.must_match('test01.shobj', "A .f file.\n")
test.must_match('test02.shobj', "A .F file.\n")
test.must_match('test03.shobj', "A .for file.\n")
test.must_match('test04.shobj', "A .FOR file.\n")
test.must_match('test05.shobj', "A .ftn file.\n")
test.must_match('test06.shobj', "A .FTN file.\n")
test.must_match('test07.shobj', "A .fpp file.\n")
test.must_match('test08.shobj', "A .FPP file.\n")
test.must_match('test09.shobj', "A .f77 file.\n")
test.must_match('test10.shobj', "A .F77 file.\n")

test.pass_test()
