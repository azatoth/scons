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

"""
Verify that a failed build action with -j works as expected.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

_python_ = TestSCons._python_

try:
    import threading
except ImportError:
    # if threads are not supported, then
    # there is nothing to test
    TestCmd.no_result()
    sys.exit()


test = TestSCons.TestSCons()

# Test that we can handle parallel builds with a dependency graph
# where:
#    a) Some nodes have multiple parents
#    b) Some targets fail building
#    c) Some targets succeed building

test.write('SConstruct', """
def fail_action(target = None, source = None, env = None):
    return 2

failed_target0 = Command(target='failed00', source='', action=fail_action)
ok_target0     = Command(target='ok00',     source='', action=Touch('${TARGET}'))

prev_level = failed_target0 + ok_target0

for i in range(1,20):
    
    failed_target = Command(target='failed%02d' % i, source='', action=fail_action)
    ok_target     = Command(target='ok%02d' % i,     source='', action=Touch('${TARGET}'))

    next_level = failed_target + ok_target
    for j in range(1,10):
        next_level = next_level + Alias('a%02d%02d' % (i,j), prev_level)

    prev_level = next_level

all = Alias('all', prev_level)

Default(all)
""")

test.run(arguments = 'all',
         status = 2,
         stderr = "scons: *** [failed19] Error 2\n")
test.must_not_exist(test.workpath('ok'))


for i in range(5):
    test.run(arguments = '-c all')

    test.run(arguments = '-j8 all',
             status = 2,
             stderr = "(scons: \*\*\* \[failed\d+] Error 2\n)+",
             match=TestSCons.match_re_dotall)


for i in range(5):
    test.run(arguments = '-c all')

    test.run(arguments = '-j 8 -k all',
             status = 2,
             stderr = "(scons: \*\*\* \[failed\d+] Error 2\n)+",
             match=TestSCons.match_re_dotall)
    for i in range(20):
        test.must_exist(test.workpath('ok%02d' % i))


for i in range(5):
    test.run(arguments = 'all --random',
             status = 2,
             stderr = "scons: \*\*\* \[failed\d+] Error 2\n",
             match=TestSCons.match_re_dotall)
    test.must_not_exist(test.workpath('ok'))

for i in range(5):
    test.run(arguments = '-c all')

    test.run(arguments = '-j8 --random all',
             status = 2,
             stderr = "(scons: \*\*\* \[failed\d+] Error 2\n)+",
             match=TestSCons.match_re_dotall)

for i in range(5):
    test.run(arguments = '-c all')

    test.run(arguments = '-j 8 -k --random all',
             status = 2,
             stderr = "(scons: \*\*\* \[failed\d+] Error 2\n)+",
             match=TestSCons.match_re_dotall)
    for i in range(20):
        test.must_exist(test.workpath('ok%02d' % i))

test.pass_test()
