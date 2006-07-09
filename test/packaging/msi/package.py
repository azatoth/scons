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
Test the ability to create a simple msi package.
"""

import os
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

wix = test.Environment().WhereIs('candle')

if wix:
  test.write( 'file1.exe', "file1" )
  test.write( 'file2.exe', "file2" )

  test.write('SConstruct', """
import os

f1 = Install( '/usr/' , 'file1.exe'  )
f2 = Install( '/usr/' , 'file2.exe'  )

Package( projectname    = 'foo',
         version        = '1.2.3',
         packageversion = 0,
         type           = 'msi',
         summary        = 'balalalalal',
         description    = 'this should be reallly really long',
	 vendor         = 'Nanosoft',
         source         = [ f1, f2 ],
        )

Alias( 'install', [ f1, f2 ] )
""")

  test.run(arguments='', stderr = None)

  test.fail_test( not os.path.exists( 'foo-1.2.3.wxs' ) )
  test.fail_test( not os.path.exists( 'foo-1.2.3-0.msi' ) )

test.pass_test()
