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
_exe = TestSCons._exe

test = TestSCons.TestSCons()

posix_conv = """
LIBDIRPREFIX = '-L',
LIBDIRSUFFIX = '',
LIBLINKPREFIX = '-l',
LIBLINKSUFFIX = ''
"""

test.write("wrapper.py",
"""import os
import string
import sys
import getopt

args = sys.argv[1:]
keep = []
opts, args = getopt.getopt(args, "o:c:/c:/o:L:l:", ['static', 'shared'])
for opt, arg in opts:
    if opt == "-L" or opt == "-l":
        keep.append( string.join((opt, arg), "##"))
    elif opt == '--static' or opt == '--shared':
        keep.append(opt)
    else:
        pass
open('%s', 'wb').write(string.join(keep, " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

# Test order LIBPATH/LIBS + string arguments

# We invert the default order in LINKCOM because getopt does not parse option
# after the first non-option argument
test.write('SConstruct', """
foo = Environment(%(posix_conv)s, LINKCOM = '%(_python_)s wrapper.py -o $TARGET $_LINKWCFLAGS $SOURCE')
foo.Append(LINKWCFLAGS = [('LIBPATH', 'foo'), ('LIBS', 'foo'), ('LIBPATH', 'bar'), ('LIBS', 'bar')])
foo.Program(target = 'dummy', source = 'dummy.c')
""" % locals())

test.write('dummy.c', r"""
""")


test.run(arguments = 'dummy' + _exe)

test.fail_test(test.read('wrapper.out') != "-L##foo -l##foo -L##bar -l##bar")

# Test LINKFLAGS/LIBPATH/LIBS + string arguments

test.write('SConstruct', """
foo = Environment(%(posix_conv)s, LINKCOM = '%(_python_)s wrapper.py -o $TARGET $_LINKWCFLAGS $SOURCE')
foo.Append(LINKWCFLAGS = [('LINKFLAGS', '--static'), ('LIBS', 'foo'), ('LINKFLAGS', '--shared')])
foo.Program(target = 'dummy', source = 'dummy.c')
""" % locals())

test.write('dummy.c', r"""
""")

test.run(arguments = 'dummy' + _exe)

test.fail_test(test.read('wrapper.out') != "--static -l##foo --shared")

# Test LIBPATH/LIBS + list arguments

test.write('SConstruct', """
foo = Environment(%(posix_conv)s, LINKCOM = '%(_python_)s wrapper.py -o $TARGET $_LINKWCFLAGS $SOURCE')
foo.Append(LINKWCFLAGS = [('LINKFLAGS', ['--static']), ('LIBPATH', ['foobar']), 
    ('LIBS', ['foo', 'bar']), ('LINKFLAGS', ['--shared'])])
foo.Program(target = 'dummy', source = 'dummy.c')
""" % locals())

test.write('dummy.c', r"""
""")

test.run(arguments = 'dummy' + _exe)

test.fail_test(test.read('wrapper.out') != "--static -l##foo --shared")

test.pass_test()
