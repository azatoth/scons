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
Test the ability to use the archiver in combination with builddir.
"""

import os
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

tar = test.detect('TAR', 'tar')

#if tar:
#  #
#  # TEST: builddir usage. XXX
#  #
#  test.subdir('src')
#  test.subdir('build')
#
#  test.write('src/main.c', '')
#
#  test.write('SConstruct', """
#BuildDir('build', 'src')
#Package( projectname = 'libfoo',
#         subdir      = 'build/libfoo',
#         version     = '1.2.3',
#         source      = [ 'src/main.c', 'SConstruct' ] )
#""")
#
#  test.run(stderr = None)
#
#  test.fail_test( not os.path.exists( 'build/libfoo-1.2.3.tar.gz' ) )
#
#  #
#  # TEST: builddir not placed in archive
#  #
#  test.subdir('src')
#  test.subdir('build')
#  test.subdir('temp')
#
#  test.write('src/main.c', '')
#
#  test.write('SConstruct', """
#BuildDir('build', 'src')
#Package( projectname = 'libfoo',
#         subdir      = 'build/libfoo',
#         version     = '1.2.3',
#         source      = [ 'src/main.c', 'SConstruct' ] )
#Tar( 'build/libfoo-1.2.3.tar.gz', TARFLAGS = '-C temp -xzf' )
#""")
#
#  test.run(stderr = None)
#
#  test.fail_test( not os.path.exists( 'build/libfoo-1.2.3.tar.gz' ) )
#  test.fail_test( not os.path.exists( 'temp/libfoo/src/main.c' ) )
#  test.fail_test( not os.path.exists( 'temp/libfoo/SConstruct' ) )


test.pass_test()
