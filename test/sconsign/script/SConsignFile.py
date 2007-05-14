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
Verify that the sconsign script works with files generated when
using the signatures in an SConsignFile().
"""

import TestSConsign

test = TestSConsign.TestSConsign(match = TestSConsign.match_re)

test.subdir('sub1', 'sub2')

test.write(['SConstruct'], """\
SConsignFile()
env1 = Environment(PROGSUFFIX = '.exe', OBJSUFFIX = '.obj')
env1.Program('sub1/hello.c')
env2 = env1.Clone(CPPPATH = ['sub2'])
env2.Program('sub2/hello.c')
""")

test.write(['sub1', 'hello.c'], r"""\
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("sub1/hello.c\n");
        exit (0);
}
""")

test.write(['sub2', 'hello.c'], r"""\
#include <stdio.h>
#include <stdlib.h>
#include <inc1.h>
#include <inc2.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("sub2/goodbye.c\n");
        exit (0);
}
""")

test.write(['sub2', 'inc1.h'], r"""\
#define STRING1 "inc1.h"
""")

test.write(['sub2', 'inc2.h'], r"""\
#define STRING2 "inc2.h"
""")

test.run(arguments = '--implicit-cache .')

sig_re = r'[0-9a-fA-F]{32}'

test.run_sconsign(arguments = ".sconsign",
         stdout = r"""=== .:
SConstruct: %(sig_re)s \d+ \d+
=== sub1:
hello.c: %(sig_re)s \d+ \d+
hello.exe: %(sig_re)s \d+ \d+
        hello.obj: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        hello.c: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
=== sub2:
hello.c: %(sig_re)s \d+ \d+
hello.exe: %(sig_re)s \d+ \d+
        hello.obj: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        hello.c: %(sig_re)s \d+ \d+
        inc1.h: %(sig_re)s \d+ \d+
        inc2.h: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
inc1.h: %(sig_re)s \d+ \d+
inc2.h: %(sig_re)s \d+ \d+
""" % locals())

test.run_sconsign(arguments = "--raw .sconsign",
         stdout = r"""=== .:
SConstruct: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
=== sub1:
hello.c: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
hello.exe: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
        hello.obj: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
        %(sig_re)s \[.*\]
hello.obj: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
        hello.c: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
        %(sig_re)s \[.*\]
=== sub2:
hello.c: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
hello.exe: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
        hello.obj: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
        %(sig_re)s \[.*\]
hello.obj: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
        hello.c: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
        inc1.h: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
        inc2.h: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
        %(sig_re)s \[.*\]
inc1.h: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
inc2.h: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?}
""" % locals())

test.run_sconsign(arguments = "-v .sconsign",
         stdout = r"""=== .:
SConstruct:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
=== sub1:
hello.c:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
hello.exe:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
    implicit:
        hello.obj:
            csig: %(sig_re)s
            timestamp: \d+
            size: \d+
    action: %(sig_re)s \[.*\]
hello.obj:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
    implicit:
        hello.c:
            csig: %(sig_re)s
            timestamp: \d+
            size: \d+
    action: %(sig_re)s \[.*\]
=== sub2:
hello.c:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
hello.exe:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
    implicit:
        hello.obj:
            csig: %(sig_re)s
            timestamp: \d+
            size: \d+
    action: %(sig_re)s \[.*\]
hello.obj:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
    implicit:
        hello.c:
            csig: %(sig_re)s
            timestamp: \d+
            size: \d+
        inc1.h:
            csig: %(sig_re)s
            timestamp: \d+
            size: \d+
        inc2.h:
            csig: %(sig_re)s
            timestamp: \d+
            size: \d+
    action: %(sig_re)s \[.*\]
inc1.h:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
inc2.h:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
""" % locals())

test.run_sconsign(arguments = "-c -v .sconsign",
         stdout = r"""=== .:
SConstruct:
    csig: %(sig_re)s
=== sub1:
hello.c:
    csig: %(sig_re)s
hello.exe:
    csig: %(sig_re)s
hello.obj:
    csig: %(sig_re)s
=== sub2:
hello.c:
    csig: %(sig_re)s
hello.exe:
    csig: %(sig_re)s
hello.obj:
    csig: %(sig_re)s
inc1.h:
    csig: %(sig_re)s
inc2.h:
    csig: %(sig_re)s
""" % locals())

test.run_sconsign(arguments = "-s -v .sconsign",
         stdout = r"""=== .:
SConstruct:
    size: \d+
=== sub1:
hello.c:
    size: \d+
hello.exe:
    size: \d+
hello.obj:
    size: \d+
=== sub2:
hello.c:
    size: \d+
hello.exe:
    size: \d+
hello.obj:
    size: \d+
inc1.h:
    size: \d+
inc2.h:
    size: \d+
""" % locals())

test.run_sconsign(arguments = "-t -v .sconsign",
         stdout = r"""=== .:
SConstruct:
    timestamp: \d+
=== sub1:
hello.c:
    timestamp: \d+
hello.exe:
    timestamp: \d+
hello.obj:
    timestamp: \d+
=== sub2:
hello.c:
    timestamp: \d+
hello.exe:
    timestamp: \d+
hello.obj:
    timestamp: \d+
inc1.h:
    timestamp: \d+
inc2.h:
    timestamp: \d+
""" % locals())

test.run_sconsign(arguments = "-e hello.obj .sconsign",
         stdout = r"""=== .:
=== sub1:
hello.obj: %(sig_re)s \d+ \d+
        hello.c: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
=== sub2:
hello.obj: %(sig_re)s \d+ \d+
        hello.c: %(sig_re)s \d+ \d+
        inc1.h: %(sig_re)s \d+ \d+
        inc2.h: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
""" % locals(),
        stderr = r"""sconsign: no entry `hello.obj' in `\.'
""")

test.run_sconsign(arguments = "-e hello.obj -e hello.exe -e hello.obj .sconsign",
         stdout = r"""=== .:
=== sub1:
hello.obj: %(sig_re)s \d+ \d+
        hello.c: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.exe: %(sig_re)s \d+ \d+
        hello.obj: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        hello.c: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
=== sub2:
hello.obj: %(sig_re)s \d+ \d+
        hello.c: %(sig_re)s \d+ \d+
        inc1.h: %(sig_re)s \d+ \d+
        inc2.h: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.exe: %(sig_re)s \d+ \d+
        hello.obj: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        hello.c: %(sig_re)s \d+ \d+
        inc1.h: %(sig_re)s \d+ \d+
        inc2.h: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
""" % locals(),
        stderr = r"""sconsign: no entry `hello.obj' in `\.'
sconsign: no entry `hello.exe' in `\.'
sconsign: no entry `hello.obj' in `\.'
""")

#test.run_sconsign(arguments = "-i -v .sconsign",
#         stdout = r"""=== sub1:
#hello.exe:
#    implicit:
#        hello.obj: %(sig_re)s
#hello.obj:
#    implicit:
#        hello.c: %(sig_re)s
#=== sub2:
#hello.exe:
#    implicit:
#        hello.obj: %(sig_re)s
#hello.obj:
#    implicit:
#        hello.c: %(sig_re)s
#        inc1.h: %(sig_re)s
#        inc2.h: %(sig_re)s
#inc1.h: %(sig_re)s
#inc2.h: %(sig_re)s
#""" % locals())

test.pass_test()
