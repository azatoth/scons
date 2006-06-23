"""SCons.Tool.rpm

Tool-specific initialization for rpm.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

The rpm tool calls the rpmbuild command. As a speciality only the first source
file is delivered to the rpmbuild command.
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
import re
import shutil

import SCons.Builder
import SCons.Node.FS
import SCons.Util

def get_cmd(source, env):
    tar_file_with_included_specfile = source
    if SCons.Util.is_List(source):
        tar_file_with_included_specfile = source[0]

    return "%s %s %s"%(env['RPM'], env['RPMFLAGS'],
                       tar_file_with_included_specfile.abspath )

def build_rpm(target, source, env):
    # XXX: building the rpm shoudl be done in a temporary directory.
    handle=os.popen( get_cmd(source, env) )
    output=handle.read()
    retval=handle.close()

    if retval is not None:
        raise SCons.Errors.BuildError( node=target[0],
                                       errstr=output,
                                       filename=str(target[0]) )
    else:
        output_files = re.compile( 'Wrote: (.*)' ).findall( output )

        # XXX: ugly ugly ugly
        i=0
        assert len(output_files) == len(target)
        while i<len(output_files):
            print os.path.basename(output_files[i]),os.path.basename(target[i].get_path())
            assert os.path.basename(output_files[i]) == os.path.basename(target[i].get_path())
            #shutil.copy( output_files[i], target[i].abspath )

    return retval

def string_rpm(target, source, env):
    try:
        return env['RPMCOMSTR']
    except KeyError:
        return get_cmd(source, env)

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
    env['RPMFLAGS']   = SCons.Util.CLVar('-ta')
    env['RPMCOM']     = rpmAction
    env['RPMSUFFIX']  = '.rpm'

def exists(env):
    return env.Detect('rpmbuild')
