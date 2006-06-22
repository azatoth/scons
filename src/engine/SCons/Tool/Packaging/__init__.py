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
import SCons.Tool.Packaging.rpm

import os
import SCons.Defaults

# TODO this should be generated from listing the current module
package_builder = {
    'tarbz2' : tarbz2.create_builder,
    'targz'  : targz.create_builder,
    'zip'    : zip.create_builder,
    'rpm'    : rpm.create_builder,
}

def create_builder(env, kw):
    """ factory method for the Package Builder.
    According to to the given "type" of a package a special Builder is returned
    """
    assert kw.has_key('source')
    assert kw.has_key('target')
    assert kw.has_key('type')

    target, source, type = kw['target'], kw['source'], kw['type']

    list = []
    for t in type:
        # XXX: catching the non-availability of a given build is hard since 
        #      comparing with None through an Exception (because of __cmp__ in
        #      Builder) and checking if Builder is None throughs an
        #      InternalError
        list.append(package_builder.get(t)(env))
    return list

def create_default_target(kw):
    """ In the absence of a filename for a given Package, this function deduces
    one out of the projectname and version keywords.
    """
    projectname, version = kw['projectname'], kw['version']
    return "%s-%s"%(projectname,version)

def create_fakeroot_emitter(fakeroot):
    """This emitter changes the source to be rooted in the given fakeroot.
    """
    def fakeroot_emitter(target, source, env):
        pass

    return fakeroot_emitter
