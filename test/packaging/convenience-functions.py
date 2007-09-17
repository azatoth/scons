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
Test the FindInstalledFiles() and the FindSourceFiles() functions.
"""

import os
import TestSCons

python = TestSCons.python
test = TestSCons.TestSCons()

test.write( "f1", "" )
test.write( "f2", "" )
test.write( "f3", "" )

test.write( 'SConstruct', r"""
env  = Environment(tools=['default', 'packaging'])
prog = env.Install( 'bin/', ["f1", "f2"] )
env.File( "f3" )

src_files = map(str, env.FindSourceFiles())
oth_files = map(str, env.FindInstalledFiles())
src_files.sort()
oth_files.sort()

print src_files
print oth_files
""")

expected="""scons: Reading SConscript files ...
['SConstruct', 'f1', 'f2', 'f3']
['bin/f1', 'bin/f2']
scons: done reading SConscript files.
scons: Building targets ...
Install file: "f1" as "bin/f1"
Install file: "f2" as "bin/f2"
scons: done building targets.
"""

test.run(stdout=expected)

test.pass_test()
