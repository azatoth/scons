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

import SCons.Errors
import SCons.Tool.Packaging.tarbz2
import SCons.Tool.Packaging.targz
import SCons.Tool.Packaging.zip

# TODO this should be generated from listing the current module
package_builder = {
    'tarbz2' : tarbz2.create_builder,
    'targz'  : targz.create_builder,
    'zip'    : zip.create_builder,
}

def create_builder(env, **kw):
    """ factory method for the Package Builder.
    According to to the given "type" of a package a special Builder is returned
    """
    assert kw.has_key('source')
    assert kw.has_key('target')
    assert kw.has_key('type')

    target, source, type = kw['target'], kw['source'], kw['type']

    if package_builder.get(type[0])==None:
      raise SCons.Errors.UserError ("packager %s not available."%type)
      return None
    else:
      return package_builder.get(type[0])(env)

def create_default_target(kw):
    """ In the absence of a filename for a given Package, this function deduces
    one out of the projectname and version keywords.
    """
    projectname, version = kw['projectname'], kw['version']
    return "%s-%s"%(projectname,version)
