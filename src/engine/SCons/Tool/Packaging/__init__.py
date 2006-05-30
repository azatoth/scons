"""SCons.Tool.Packaging

SCons Packaging Tool.
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

# TODO this should be in it's own file
def package_gnu_src(target, source, env):
    if env['BUILDERS']['Tar']:
        apply( env['BUILDERS']['Tar'], env, target, source )
    else:
        raise SCons.Errors.UserError, "Tar Tool is not available."


# TODO this should be generated from listing the current module
packager = {
    'gnu-src' : package_gnu_src
}

def package(target, source, env):
    """ This is the entry point, this function calls the approriate packager for
    a given type of package"""
    for chosen_packager_id in env['PACKAGE_TYPE']:
        packager.get(chosen_packager_id)(target, source, env)
