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
Test the ability to handle internationalized package meta-data.

These are x-rpm-Group, description and summary.
"""

import os
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

tar = test.Environment().WhereIs('rpm')

if tar:
  test.subdir('src')

  test.write( [ 'src', 'main.c' ], r"""
int main( int argc, char* argv[] )
{
  return 0;
}
  """)

  test.write('SConstruct', """
prog=Program( 'src/main.c' )
Package( projectname    = 'foo',
         version        = '1.2.3',
         type           = 'rpm',
         license        = 'gpl',
         summary        = 'hello',
         summary_de     = 'hallo',
         summary_fr     = 'bonjour',
         packageversion = 0,
         x_rpm_Group    = 'Application/office',
         x_rpm_Group_de = 'Applikation/büro',
         x_rpm_Group_fr = 'Application/bureau',
         description    = 'this should be really long',
         description_de = 'das sollte wirklich lang sein',
         description_fr = 'ceci devrait être vraiment long',
         source         = [ 'src/main.c' ],
        )
""")

  test.run(arguments='', stderr = None)

  test.fail_test( not os.path.exists( 'foo-1.2.3.rpm' ) )
  test.fail_test( not os.path.exists( 'foo-1.2.3.src.rpm' ) )
  test.fail_test( not os.popen('rpm -qdi foor-1.2.3.rpm').read()=='/src/main')

test.pass_test()
