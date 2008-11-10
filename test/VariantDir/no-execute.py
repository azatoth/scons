
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
Verify that use of a VariantDir works when the -n option is used (and
the VariantDir, therefore, isn't actually created).
"""

import os

import TestSCons

test = TestSCons.TestSCons()

test.subdir('a')

test.write('SConstruct', """\
env = Environment()
Export('env')
env.SConscript('SConscript', exported=['env'], variant_dir='build', duplicate=0)
""")

test.write('SConscript', """\
Import(['env'])
env.SConscript('a/SConscript', exports=['env'], duplicate=0)
""")

test.write(['a', 'SConscript'], """\
Import(['env'])
env.Command('file.out', 'file.in', Copy('$TARGET', '$SOURCE'))
""")

test.write(['a', 'file.in'], "a/file.in\n")

expect = """\
scons: building associated VariantDir targets: build
Copy("%s", "%s")
""" % (os.path.join('build', 'a', 'file.out'),
       os.path.join('a', 'file.in'))

test.run(arguments = '-Q -n', stdout=expect)

test.pass_test()
