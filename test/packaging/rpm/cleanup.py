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
Assert that files created by the RPM packager will be removed by 'scons -c'.
"""

import os
import TestSCons

machine = TestSCons.machine
python = TestSCons.python

test = TestSCons.TestSCons()

# TODO: skip this test, since only the intermediate directory needs to be
# removed.

rpm = test.Environment().WhereIs('rpm')

if not rpm:
    test.skip_test('rpm not found, skipping test\n')

test.subdir('src')

test.write( [ 'src', 'main.c' ], r"""
int main( int argc, char* argv[] )
{
  return 0;
}
""")

test.write('SConstruct', """
import os

env=Environment(tools=['default', 'packaging'])

prog = env.Install( '/bin/' , Program( 'src/main.c')  )

env.Package( projectname    = 'foo',
             version        = '1.2.3',
             packageversion = 0,
             type           = 'rpm',
             license        = 'gpl',
             summary        = 'balalalalal',
             x_rpm_Group    = 'Application/fu',
             description    = 'this should be really really long',
             source         = [ prog ],
             source_url     = 'http://foo.org/foo-1.2.3.tar.gz'
            )

env.Alias( 'install', prog )
""")

# first run: build the package
# second run: test if the intermediate files have been cleaned
test.run( arguments='' )
test.run( arguments='-c' )

src_rpm     = 'foo-1.2.3-0.src.rpm'
machine_rpm = 'foo-1.2.3-0.%s.rpm' % machine

test.must_not_exist( machine_rpm )
test.must_not_exist( src_rpm )
test.must_not_exist( 'foo-1.2.3.tar.gz' )
test.must_not_exist( 'foo-1.2.3.spec' )
test.must_not_exist( 'foo-1.2.3/foo-1.2.3.spec' )
test.must_not_exist( 'foo-1.2.3/SConstruct' )
test.must_not_exist( 'foo-1.2.3/src/main.c' )
test.must_not_exist( 'foo-1.2.3' )
test.must_not_exist( 'foo-1.2.3/src' )
test.must_not_exist( 'bin/main' )
