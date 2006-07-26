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
from xml.dom.minidom import *

python = TestSCons.python

test = TestSCons.TestSCons()

wix = test.Environment().WhereIs('candle')

if wix:
  #
  # build with minimal tag set and test for the given package meta-data
  #
  test.write( 'file1.exe', "file1" )
  test.write( 'file2.exe', "file2" )

  test.write('SConstruct', """
import os

f1 = Install( '/usr/' , 'file1.exe'  )
f2 = Install( '/usr/' , 'file2.exe'  )

Package( projectname    = 'foo',
         version        = '1.2',
         type           = 'msi',
         summary        = 'balalalalal',
         description    = 'this should be reallly really long',
         vendor         = 'Nanosoft_2000',
         source         = [ f1, f2 ],
        )

Alias( 'install', [ f1, f2 ] )
""")

  test.run(arguments='', stderr = None)

  test.fail_test( not os.path.exists( 'foo-1.2.wxs' ) )
  test.fail_test( not os.path.exists( 'foo-1.2.msi' ) )

  dom     = parse( test.workpath( 'foo-1.2.wxs' ) )
  Product = dom.getElementsByTagName( 'Product' )[0]
  Package = dom.getElementsByTagName( 'Package' )[0]

  test.fail_test( not Product.attributes['Manufacturer'].value == 'Nanosoft_2000' )
  test.fail_test( not Product.attributes['Version'].value      == '1.2' )
  test.fail_test( not Product.attributes['Name'].value         == 'foo' )

  test.fail_test( not Package.attributes['Description'].value == 'balalalalal' )
  test.fail_test( not Package.attributes['Comments'].value    == 'this should be reallly really long' )

  #
  # build with file tags resulting in multiple components in the msi installer
  #
  test.write( 'file1.exe', "file1" )
  test.write( 'file2.exe', "file2" )
  test.write( 'file3.html', "file3" )
  test.write( 'file4.dll', "file4" )

  test.write('SConstruct', """
import os

f1 = Install( '/usr/' , 'file1.exe'  )
f2 = Install( '/usr/' , 'file2.exe'  )
f3 = Install( '/usr/' , 'file3.html' )
f4 = Install( '/usr/' , 'file4.dll'  )

Tag( f1, x_msi_feature = 'Java Part' )
Tag( f2, x_msi_feature = 'Java Part' )
Tag( f3, 'doc' )
Tag( f4, x_msi_feature = 'default' )

Package( projectname    = 'foo',
         version        = '1.2',
         type           = 'msi',
         summary        = 'balalalalal',
         description    = 'this should be reallly really long',
         vendor         = 'Nanosoft_tx2000',
         source         = [ f1, f2, f3, f4 ],
        )

Alias( 'install', [ f1, f2, f3, f4 ] )
""")

  test.run(arguments='', stderr = None)

  test.fail_test( not os.path.exists( 'foo-1.2.wxs' ) )
  test.fail_test( not os.path.exists( 'foo-1.2.msi' ) )

  dom      = parse( test.workpath( 'foo-1.2.wxs' ) )
  elements = dom.getElementsByTagName( 'Feature' )
  test.fail_test( not elements[1].attributes['Title'].value == 'Main Part' )
  test.fail_test( not elements[2].attributes['Title'].value == 'Documentation' )
  test.fail_test( not elements[3].attributes['Title'].value == 'Java Part' )

test.pass_test()
