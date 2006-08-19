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
Test writing XML output to a file.
"""

import re

import TestRuntest

test = TestRuntest.TestRuntest()

test.subdir('test')

test.write_fake_scons_source_tree()

test.write_failing_test(['test', 'fail.py'])

test.write_no_result_test(['test', 'no_result.py'])

test.write_passing_test(['test', 'pass.py'])

test.run(arguments = '-o xml.out --xml test')

expect_engine = """\
<annotation key="scons_test\\.engine">
 __build__='D456'
 __buildsys__='another_fake_system'
 __date__='Dec 31 1999'
 __developer__='John Doe'
 __version__='4\\.5\\.6'
</annotation>
"""

expect_script = """\
<annotation key="scons_test\\.script">
 __build__='D123'
 __buildsys__='fake_system'
 __date__='Jan 1 1970'
 __developer__='Anonymous'
 __version__='1\\.2\\.3'
</annotation>
"""

# The actual values printed for sys and os.environ will be completely
# dependent on the local values.  Don't bother trying to match, just
# look to see if the opening tag exists.

expect_sys = """\
<annotation key="scons_test\\.sys">
"""

expect_os_environ = """\
<annotation key="scons_test\\.os\\.environ">
"""

expect_fail = """\
 <result id="test/fail\\.py" kind="test" outcome="FAIL">
  <annotation name="Test.exit_code">
   &quot;1&quot;
  </annotation>
  <annotation name="Test\\.stderr">
   &quot;&lt;pre&gt;FAILING TEST STDERR
&lt;/pre&gt;&quot;
  </annotation>
  <annotation name="Test\\.stdout">
   &quot;&lt;pre&gt;FAILING TEST STDOUT
&lt;/pre&gt;&quot;
  </annotation>
  <annotation name="qmtest\\.cause">
   &quot;Non-zero exit_code\\.&quot;
  </annotation>
  <annotation name="qmtest\\.end_time">
   &quot;[\\d.]+&quot;
  </annotation>
  <annotation name="qmtest\\.start_time">
   &quot;[\\d.]+&quot;
  </annotation>
  <annotation name="qmtest\\.target">
   &quot;local&quot;
  </annotation>
 </result>
"""

expect_no_result = """\
 <result id="test/no_result\\.py" kind="test" outcome="FAIL">
  <annotation name="Test.exit_code">
   &quot;2&quot;
  </annotation>
  <annotation name="Test\\.stderr">
   &quot;&lt;pre&gt;NO RESULT TEST STDERR
&lt;/pre&gt;&quot;
  </annotation>
  <annotation name="Test\\.stdout">
   &quot;&lt;pre&gt;NO RESULT TEST STDOUT
&lt;/pre&gt;&quot;
  </annotation>
  <annotation name="qmtest\\.cause">
   &quot;Non-zero exit_code\\.&quot;
  </annotation>
  <annotation name="qmtest\\.end_time">
   &quot;[\\d.]+&quot;
  </annotation>
  <annotation name="qmtest\\.start_time">
   &quot;[\\d.]+&quot;
  </annotation>
  <annotation name="qmtest\\.target">
   &quot;local&quot;
  </annotation>
 </result>
"""

expect_pass = """\
 <result id="test/pass\\.py" kind="test" outcome="PASS">
  <annotation name="qmtest\\.end_time">
   &quot;[\\d.]+&quot;
  </annotation>
  <annotation name="qmtest\\.start_time">
   &quot;[\\d.]+&quot;
  </annotation>
  <annotation name="qmtest\\.target">
   &quot;local&quot;
  </annotation>
 </result>
"""

xml_out = test.read('xml.out')

expect = [
    expect_engine,
    expect_script,
    expect_sys,
    expect_os_environ,
    expect_fail,
    expect_no_result,
    expect_pass,
]

non_matches = []

for e in expect:
    if not re.search(e, xml_out):
        non_matches.append(e)

if non_matches:
    for n in non_matches:
        print "DID NOT MATCH " + '='*60
        print n
    print "ACTUAL XML OUTPUT " + '='*60
    print xml_out
    test.fail_test()

test.pass_test()
