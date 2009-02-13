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
Verify that we expect the .py file created by the -python flag to be in
the same subdirectory as the taget.
"""

import os
import sys

import TestSCons

# swig-python expects specific filenames.
# the platform specific suffix won't necessarily work.
if sys.platform == 'win32':
    _dll = '.dll'
else:
    _dll   = '.so' 

test = TestSCons.TestSCons()

test.subdir('sub')

swig = test.where_is('swig')

if not swig:
    test.skip_test('Can not find installed "swig", skipping test.\n')

python = test.get_platform_python()
_python_ = test.get_quoted_platform_python()

# handle testing on other platforms:
ldmodule_prefix = '_'

python_include_dir = test.get_python_inc()

Python_h = os.path.join(python_include_dir, 'Python.h')

if not os.path.exists(Python_h):
    test.skip_test('Can not find %s, skipping test.\n' % Python_h)

python_frameworks_flags = test.get_python_frameworks_flags()

test.write('SConstruct', """
env = Environment(SWIGFLAGS='-python',
                  CPPPATH='%(python_include_dir)s/',
                  LDMODULEPREFIX='%(ldmodule_prefix)s',
                  LDMODULESUFFIX='%(_dll)s',
                  FRAMEWORKS='%(python_frameworks_flags)s',
                  SWIG=r'%(swig)s',
                  )

import sys
if sys.version[0] == '1':
    # SWIG requires the -classic flag on pre-2.0 Python versions.
    env.Append(SWIGFLAGS = ' -classic')

env.LoadableModule('sub/_foo',
                   ['sub/foo.i', 'sub/foo.c'],
                   LDMODULEPREFIX='')
""" % locals())

test.write(['sub', 'foo.i'], """\
%module foo
%{
/* Put header files here (optional) */
/*
 * This duplication shouldn't be necessary, I guess, but it seems
 * to suppress "cast to pointer from integer of different size"
 * warning messages on some systems.
 */
extern char *foo_string();
%}

extern char *foo_string();
""")

test.write(['sub', 'foo.c'], """\
char *
foo_string()
{
    return "This is foo.c!";
}
""")

test.run(arguments = '.')

test.up_to_date(options = '--debug=explain', arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
