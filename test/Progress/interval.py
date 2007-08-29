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
Verify that the "interval=" parameter to Progress skips Nodes.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
import sys
env = Environment()
env['BUILDERS']['C'] = Builder(action=Copy('$TARGET', '$SOURCE'))
Progress('stderr: $TARGET\\n', file=sys.stderr, interval=2)
env.C('f1.out', 'f1.in')
env.C('f2.out', 'f2.in')
env.C('f3.out', 'f3.in')
env.C('f4.out', 'f4.in')
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write('f4.in', "f4.in\n")

expect_stdout = """\
Copy("f1.out", "f1.in")
Copy("f2.out", "f2.in")
Copy("f3.out", "f3.in")
Copy("f4.out", "f4.in")
"""

expect_stderr = """\
stderr: f1.in
stderr: f2.in
stderr: f3.in
stderr: f4.in
stderr: .
"""

test.run(arguments = '-Q .', stdout=expect_stdout, stderr=expect_stderr)

test.pass_test()
