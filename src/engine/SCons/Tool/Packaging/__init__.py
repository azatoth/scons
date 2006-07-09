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
import SCons.Environment

import SCons.Tool.Packaging.tarbz2
import SCons.Tool.Packaging.targz
import SCons.Tool.Packaging.zip
import SCons.Tool.Packaging.rpm
import SCons.Tool.Packaging.msi
import SCons.Environment

import os
import SCons.Defaults

# TODO this should be generated from listing the current module
packagers = {
    'tarbz2' : tarbz2,
    'targz'  : targz,
    'zip'    : zip,
    'rpm'    : rpm,
    'msi'    : msi,
}

def get_packager(env, kw):
    """ factory method for the packager.
    """
    type = kw['type']
    if SCons.Util.is_String( type ):
        type = [ type ]

    try:
        return map( packagers.get, type )
    except KeyError:
        raise SCons.Errors.UserError( 'packager %s not available' % t )

def create_default_target(kw, packager=None):
    """ In the absence of a target for a given Package, this function deduces
    one out of the projectname and version keywords.

    If a packager is given, it is asked to generate a default target.
    """
    target = []

    try:
        target.extend( packager.create_default_target(kw) )
    except AttributeError:
        projectname, version = kw['projectname'], kw['version']
        target.append( "%s-%s"%(projectname,version) )

    return target

def create_default_package_root(kw):
    projectname, version = kw['projectname'], kw['version']
    return "%s-%s"%(projectname,version)

def get_src_package_root_emitter(src_package_root):
    """This emitter changes the source to be rooted in the given package_root.
    """
    def src_package_root_emitter(target, source, env):
        new_source = []
        for s in source:
            filename = os.path.join( src_package_root, env.strip_abs_path( s.get_path() ) )
            new_s    = env.Command( source = s,
                                    target = filename,
                                    action = SCons.Defaults.Copy( '$TARGET', '$SOURCE' ),
                                  )[0]

            # store the tags of our original file in the new file.
            new_s.set_tags( s.get_tags( factories=[ LocationTagFactory() ] ) )

            new_source.append( new_s )

        return (target, new_source)

    return src_package_root_emitter

class TagFactory:
    """An instance of this class has the responsibility to generate additional
    tags for a SCons.Node.FS.File instance.

    Subclasses have to be callable. This class definition is informally
    describing the interface.
    """

    def __call__(self, file, current_tag_dict):
        """ This call has to return additional tags in the form of a dict.
        """
        pass

    def attach_additional_info(self, info=None):
        pass

class LocationTagFactory(TagFactory):
    """ This class creates the "location" tag, which describes the install
    location of a given file.

    This is done by analyzing the builder of a given file for a InstallBuilder,
    from this builder the install location is deduced.
    """

    def __call__(self, file, current_tag_dict):
        if current_tag_dict.has_key('install_location'):
            return {}

        if file.has_builder() and\
           file.builder == SCons.Environment.InstallBuilder and\
           file.has_explicit_builder():
            return { 'install_location' : file.builder.targets( file ) }
        else:
            return {}
