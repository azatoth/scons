"""SCons.Tool.rpm

Tool-specific initialization for rpm.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""

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

import os.path

import SCons.Builder
import SCons.Node.FS
import SCons.Util

def build_rpm(target, source, env):
    tar_file_with_included_specfile = source
    if SCons.Util.is_List(source):
        tar_file_with_included_specfile = source[0]

    handle=os.popen( "%s %s %s"%(env['RPM'], env['RPMFLAGS'],
                               tar_file_with_included_specfile.abspath ) )
    output=handle.read()
    retval=handle.close()

    if retval is not None:
        raise SCons.Errors.BuildError( node=target[0],
                                       errstr=output,
                                       filename=str(target[0]) )
    return retval

def string_rpm(target, source, env):
    return "building %s from %s"%(str(target[0]), str(source[0]))

rpmAction = SCons.Action.Action(build_rpm, string_rpm)

RpmBuilder = SCons.Builder.Builder(action = SCons.Action.Action('$RPMCOM', '$RPMCOMSTR'),
                                   source_factory = SCons.Node.FS.Entry,
                                   source_scanner = SCons.Defaults.DirScanner,
                                   suffix = '$RPMSUFFIX')



def generate(env):
    """Add Builders and construction variables for rpm to an Environment."""
    try:
        bld = env['BUILDERS']['Rpm']
    except KeyError:
        bld = RpmBuilder
        env['BUILDERS']['Rpm'] = bld

    env['RPM']        = 'rpmbuild'
    env['RPMFLAGS']   = SCons.Util.CLVar('')
    env['RPMCOM']     = rpmAction
    env['RPMSUFFIX']  = '.rpm'

def exists(env):
    return env.Detect('rpmbuild')
