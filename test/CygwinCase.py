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

import string
import sys
import TestSCons

test = TestSCons.TestSCons(match=TestSCons.match_re_dotall)

test.write('SConstruct', """\
import os

env = Environment(ENV = {'PATH' : os.environ['PATH']})
platform = env['PLATFORM']

# we have to specify the toolset for HP-UX unless we're using aCC
if platform == 'hpux':
   env.Tool('gcc')
   env.Tool('g++')

target_name = 'test_namespace'
target_sources = [ target_name + '.cpp' ]
target = env.Program(target = target_name, source = target_sources)
""")

test.write('test_namespace.cpp', """\
#include <iostream>
#include "namespace_for_test.hpp"

int main()
{
   std::cout << "Data: \"" << test_namespace::dataString << "\"" << std::endl;
}
""")

test.write('namespace_for_test.hpp', """\
#if !defined(NAMESPACE_FOR_TEST_HPP)
#define NAMESPACE_FOR_TEST_HPP

#include <string>

namespace test_namespace
{
const std::string dataString = "Unchanged string from test_namespace";
}
#endif // #if !defined(NAMESPACE_FOR_TEST_HPP)
""")

# tree output (dependency tree) should contain namespace_for_test.hpp
# Case-sensitivity bug with cygwin scanner prevented this from working.
test.run(arguments="--tree=all", 
         stdout = ".*namespace_for_test.hpp.*")

# Modify the header:
test.write('namespace_for_test.hpp', """\
#if !defined(NAMESPACE_FOR_TEST_HPP)
#define NAMESPACE_FOR_TEST_HPP

#include <string>

namespace test_namespace
{
const std::string dataString = "Another String";
}
#endif // #if !defined(NAMESPACE_FOR_TEST_HPP)
""")

# Modified header should cause rebuild of test_namespace
test.run(arguments="", stdout=".*test_namespace.cpp.*")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
