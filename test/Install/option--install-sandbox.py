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
Test the --install-sandbox commandline option for Install() and InstallAs().
"""

import os.path
import sys
import TestSCons

test = TestSCons.TestSCons()

test.subdir('install', 'subdir')
target  = 'destination'
destdir = test.workpath( target )

#
test.write('SConstruct', r"""
env = Environment(SUBDIR='subdir')
env.Install(r'%s', 'file1.out')
env.InstallAs([r'%s', r'%s'], ['file2.in', r'%s'])
""" % (destdir,
       'file2.out',
       os.path.join('$SUBDIR', 'file3.out'),
       os.path.join('$SUBDIR', 'file3.in') ))

test.write('file1.out', "file1.out\n")
test.write('file2.in', "file2.in\n")
test.write(['subdir', 'file3.in'], "subdir/file3.in\n")

subdir_file3_in = os.path.join('subdir', 'file3.in')
file1_out       = target+os.path.join( target, os.path.join( destdir, 'file1.out' ) )
expect = test.wrap_stdout("""\
Install file(s): "file2.in %s" as "%s %s"
Install file(s): "file1.out" as "%s"
""" % ( subdir_file3_in,
        os.path.join( target, 'file2.out' ),
        os.path.join( target, subdir_file3_in.replace( 'in', 'out' ) ),
        file1_out, ) )

test.run(arguments = '--install-sandbox=%s' % destdir, stdout=expect)

test.fail_test(test.read(file1_out) != "file1.out\n")
test.fail_test(test.read('destination/file2.out') != "file2.in\n")
test.fail_test(test.read('destination/subdir/file3.out') != "subdir/file3.in\n")

#
test.pass_test()
