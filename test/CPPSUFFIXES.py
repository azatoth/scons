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
Test the ability to scan additional filesuffixes added to $CPPSUFFIXES.
"""

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.write('mycc.py', r"""
import string
import sys
def do_file(outf, inf):
    for line in open(inf, 'rb').readlines():
        if line[:10] == '#include <':
            do_file(outf, line[10:-2])
        else:
            outf.write(line)
outf = open(sys.argv[1], 'wb')
for f in sys.argv[2:]:
    do_file(outf, f)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(CPPPATH = ['.'],
                  CC = r'%s mycc.py',
                  CCFLAGS = [],
                  CCCOM = '$CC $TARGET $SOURCES',
                  OBJSUFFIX = '.o')
env.Append(CPPSUFFIXES = ['.x'])
env.Object(target = 'test1', source = 'test1.c')
env.InstallAs('test1_c', 'test1.c')
env.InstallAs('test1_h', 'test1.h')
env.InstallAs('test1_x', 'test1.x')
""" % (python,))

test.write('test1.c', """\
test1.c 1
#include <test1.h>
#include <test1.x>
""")

test.write('test1.h', """\
test1.h 1
#include <foo.h>
""")

test.write('test1.x', """\
test1.x 1
#include <foo.h>
""")

test.write('foo.h', "foo.h 1\n")

test.run(arguments='.', stdout=test.wrap_stdout("""\
%s mycc.py test1.o test1.c
Install file: "test1.c" as "test1_c"
Install file: "test1.h" as "test1_h"
Install file: "test1.x" as "test1_x"
""" % (python,)))

test.must_match('test1.o', """\
test1.c 1
test1.h 1
foo.h 1
test1.x 1
foo.h 1
""")

test.up_to_date(arguments='.')

test.write('foo.h', "foo.h 2\n")

test.run(arguments='.', stdout=test.wrap_stdout("""\
%s mycc.py test1.o test1.c
""" % (python,)))

test.must_match('test1.o', """\
test1.c 1
test1.h 1
foo.h 2
test1.x 1
foo.h 2
""")

test.up_to_date(arguments='.')

test.write('test1.x', """\
test1.x 2
#include <foo.h>
""")

test.run(arguments='.', stdout=test.wrap_stdout("""\
%s mycc.py test1.o test1.c
Install file: "test1.x" as "test1_x"
""" % (python,)))

test.must_match('test1.o', """\
test1.c 1
test1.h 1
foo.h 2
test1.x 2
foo.h 2
""")

test.up_to_date(arguments='.')

test.write('test1.h', """\
test1.h 2
#include <foo.h>
""")

test.run(arguments='.', stdout=test.wrap_stdout("""\
%s mycc.py test1.o test1.c
Install file: "test1.h" as "test1_h"
""" % (python,)))

test.must_match('test1.o', """\
test1.c 1
test1.h 2
foo.h 2
test1.x 2
foo.h 2
""")

test.up_to_date(arguments='.')

test.pass_test()
