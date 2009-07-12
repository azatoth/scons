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

import TestSCons

test = TestSCons.TestSCons()

makensis = test.where_is('makensis')
if not makensis:
    test.skip_test("Could not find 'makensis'; skipping test.\n")

# Test creation of an installer with NSIS header files
test.write('dummyfile', 'A')

test.write('foo.nsi', """\
Name "Foo"

OutFile "foo_installer.exe"

!include dummy_dir\\..\\test_custom_header.nsh

Section "Foo"

File "dummyfile"

SectionEnd 
""")

test.write('test_custom_header.nsh', """
!echo "Bar"
""")

test.write('SConstruct', """\
import os
env = Environment(ENV = os.environ)
env.NSISInstaller('foo')
""")

test.subdir('dummy_dir')

test.run()
test.must_exist('foo_installer.exe')

test.run()
test.must_contain_all_lines(test.stdout(), ['is up to date'])

test.write('dummyfile', 'B')
test.run()
test.must_not_contain_any_line(test.stdout(), ['is up to date'])

test.pass_test()
