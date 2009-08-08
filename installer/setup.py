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

import os
import os.path
import stat
import string
import sys
import cx_Freeze
import glob

Version = "__VERSION__"

(head, tail) = os.path.split(sys.argv[0])

if head:
    os.chdir(head)
    sys.argv[0] = tail

description = "Open Source next-generation build tool."

long_description = """Open Source next-generation build tool.
Improved, cross-platform substitute for the classic Make
utility.  In short, SCons is an easier, more reliable
and faster way to build software."""

scripts = [
    '../scons/script/scons',
    '../scons/script/sconsign',
    #'../scons/script/scons-time', # scons-time needs refactoring before it can be run stand-alone
]

includes = [
            (glob.glob(os.path.join(os.path.dirname(sys.executable), 'tcl', 'tcl?.?'))[0], '../tcl'),
            (glob.glob(os.path.join(os.path.dirname(sys.executable), 'tcl', 'tk?.?'))[0], '../tk'),
]

arguments = {
    'name'             : "scons",
    'version'          : Version,
    'description'      : description,
    'long_description' : long_description,
    'author'           : 'Steven Knight',
    'author_email'     : 'knight@baldmt.com',
    'url'              : "http://www.scons.org/",
    'packages'         : ["SCons",
                          "SCons.compat",
                          "SCons.Node",
                          "SCons.Options",
                          "SCons.Platform",
                          "SCons.Scanner",
                          "SCons.Script",
                          "SCons.Tool",
                          "SCons.Tool.MSCommon",
                          "SCons.Tool.packaging",
                          "SCons.Variables",
                         ],
    'package_dir'      : {'' : os.path.join('..', 'scons', 'engine')},
    'scripts'          : scripts,
}

path = sys.path

for item in arguments['package_dir'].values():
    path.append(item)

build_options = dict(
                        compressed = 1,
                        packages = arguments['packages'],
                        optimize = 2,
                        path = path,
                        init_script = os.path.abspath('standalone_init.py'),
                        create_shared_zip = 1,
                        include_files = includes,
                    )

arguments['options'] = dict(build_exe = build_options)

executables = []        
    
for script in scripts:
    executables.append(cx_Freeze.Executable(script))

executables.append(cx_Freeze.Executable('../scons/script/scons-frontend', base = 'Win32GUI'))

arguments['executables'] = executables
    
apply(cx_Freeze.setup, (), arguments)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
