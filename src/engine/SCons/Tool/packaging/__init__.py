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

import SCons.Environment
from SCons.Options import *
from SCons.Errors import *
from SCons.Util import is_List, make_path_relative

import os, imp
import SCons.Defaults


__all__ = [ 'tarbz', 'targz', 'zip', 'rpm', 'msi', 'ipk' ]


#
# Utility and Builder function
#
def Tag(env, target, source=None, *args, **kw):
    """ Tag a file with the given arguments. This functin effectively calls the 
    set_tags() function of Node.Fs object.
    """
    nodes = env.arg2nodes(source, env.fs.Entry)

    if len(kw) == 0 and len(args) == 0:
        raise UserError, "No tags for PackageTag() given."

    if source:
        raise UserError, "Source argument given, but will not be used."

    # XXX: sanity checks
    for x in args:
        kw[x] = ''

    for t in target:
        n.set_tags( kw )

def Package(env, target=None, source=None, **kw):
    """ Entry point for the package tool.
    """
    # first check some arguments
    if not source:
        raise UserError, "No source for Package() given"

    if not kw.has_key('type'):
        if env['BUILDERS'].has_key('Tar'):
            kw['type']='targz'
        elif env['BUILDERS'].has_key('Zip'):
            kw['type']='zip'
        else:
            raise UserError, "No type for Package() given"
    package_type=kw['type']
    if not is_List(package_type):
        package_type=package_type.split(',')

    # now load the needed packagers.
    def load_packager(type):
        try:
            file,path,desc=imp.find_module(type, __path__)
            return imp.load_module(type, file, path, desc)
        except ImportError, e:
            raise EnvironmentError("packager %s not available: %s"%(type,str(e)))

    packagers=map(load_packager, package_type)

    # now try to setup the default_target and the default package_root
    # arguments.
    try:
        # fill up the target list with a default target name until the package_type
        # list is of the same size as the target list.
        if target==None or target==[]:
            target=["%(projectname)s-%(version)s"%kw]

        size_diff=len(package_type)-len(target)
        if size_diff>0:
            target.extend([target]*size_diff)

        if not kw.has_key('packageroot'):
            kw['packageroot']="%(projectname)s-%(version)s"%kw

    except KeyError, e:
        raise SCons.Errors.UserError( "Missing PackageTag '%s'"%e.args[0] )

    # setup the source files
    source=env.arg2nodes(source, env.fs.Entry)

    # call the packager to setup the dependencies.
    targets=[]
    try:
        for packager in packagers:
            t=apply(packager.package, [env,target,source], kw)
            targets.extend(t)

    except KeyError, e:
        raise SCons.Errors.UserError( "Missing PackageTag '%s' for %s packager"\
                                      % (e.args[0],packager.__name__) )
    except TypeError, e:
        # this exception means that a needed argument for the packager is
        # missing. As our packagers get their "tags" as a named function
        # argument we need to find out which one is missing.
        from inspect import getargspec
        args,varargs,varkw,defaults=getargspec(packager.package)
        if defaults!=None:
            args=args[:-len(defaults)] # throw away argument with default values
        map(args.remove, 'env target source'.split())
        # now remove any args for which we have a value in kw.
        args=[x for x in args if not kw.has_key(x)]

        if len(args)==0:
            raise
        elif len(args)==1:
            raise SCons.Errors.UserError( "Missing PackageTag '%s' for %s packager"\
                                          % (args[0],packager.__name__) )
        else:
            raise SCons.Errors.UserError( "Missing PackageTags '%s' for %s packager"\
                                          % (args,packager.__name__) )

    target=env.arg2nodes(target, env.fs.Entry)
    targets.extend(env.Alias( 'package', targets ))
    return targets

def FindSourceFiles(env, target=None, source=None ):
    """ returns a list of all children of the target nodes, which have no
    children. This selects all leaves of the DAG that gets build by SCons for
    handling dependencies.
    """
    nodes = env.arg2nodes(target, env.fs.Entry)

    sources = []
    def build_source(ss):
        for s in ss:
            if s.__class__==SCons.Node.FS.Dir:
                build_source(s.all_children())
            elif len(s.sources)==0 and s.__class__==SCons.Node.FS.File:
                sources.append(s)
            else:
                build_source(s.sources)

    for node in nodes:
        build_source(node.all_children())

    # now strip the build_node from the sources by calling the srcnode
    # function
    def get_final_srcnode(file):
        srcnode = file.srcnode()
        while srcnode != file.srcnode():
            srcnode = file.srcnode()
        return srcnode

    # get the final srcnode for all nodes, this means stripping any
    # attached build node.
    map( get_final_srcnode, sources )

    # remove duplicates
    return list(set(sources))

def FindInstalledFiles(env):
    """ returns the list of all targets of the Install and InstallAs Builder.
    """
    try:
        env['Builders']['Install']
        from SCons.Tool import install
        return install._INSTALLED_FILES
    except KeyError:
        return []

#
# SCons tool initialization functions
#
def generate(env):
    try:
        env['BUILDERS']['Package']
        env['BUILDERS']['Tag']
        env['BUILDERS']['FindSourceFiles']
        env['BUILDERS']['FindInstalledFiles']
    except KeyError:
        env['BUILDERS']['Package'] = Package
        env['BUILDERS']['Tag'] = Tag
        env['BUILDERS']['FindSourceFiles'] = FindSourceFiles
        env['BUILDERS']['FindInstalledFiles'] = FindInstalledFiles

def exists(env):
    return 1

def options(opts):
    opts.AddOptions(
        EnumOption( [ 'type', '--type' ],
                    'the type of package to build',
                    None, map( str, __all__ )
                  )
    )

def copy_attr(f1, f2):
    """ copies the special packaging file attributes from f1 to f2.
    """
    for attr in [x for x in dir(f1) if not hasattr(f2, x) and\
                                       x.startswith('packaging')]:
        setattr(f2, attr, getattr(f1, attr))
#
# Emitter functions which are reused by the various packagers
#
def packageroot_emitter(pkg_root, honor_install_location=1):
    """ creates  the packageroot emitter.

    The package root emitter uses the CopyAs builder to copy all source files
    to the directory given in pkg_root.

    If honor_install_location is set and the copied source file has an
    packaging_install_location attribute, the packaging_install_location is 
    used as the new name of the source file under pkg_root.

    The source file will not be copied if it is already under the the pkg_root
    directory.

    All attributes of the source file will be copied to the new file.
    """
    def package_root_emitter(target, source, env):
        pkgroot=env.fs.Dir(pkg_root)
        def copy_file_to_pkg_root(file):
            if file.is_under(pkgroot):
                return file
            else:
                if hasattr(file, 'packaging_install_location') and\
                   honor_install_location:
                    new_name=make_path_relative(file.packaging_install_location)
                else:
                    new_name=make_path_relative(file.get_path())

                new_file=pkgroot.File(new_name)
                new_file=env.CopyAs(new_file, file)[0]

                copy_attr(file, new_file)

                return new_file
        return (target, map(copy_file_to_pkg_root, source))
    return package_root_emitter

from SCons.Warnings import warn, Warning

def stripinstall_emitter():
    """ create the a emitter which:
     * strips of the Install Builder of the source target, and stores the
       install location as the "packaging_install_location" of the given source
       File object. This effectively avoids having to execute the Install
       Action while storing the needed install location.
     * warns about files that are mangled by this emitter which have no
       Install Builder.
    """
    def strip_install_emitter(target, source, env):
        def has_no_install_location(file):
            return not (file.has_builder() and\
                (file.builder.name=="InstallBuilder" or\
                 file.builder.name=="InstallAsBuilder"))

        if len(filter(has_no_install_location, source)):
            warn(Warning, "there are file to package with have no\
            InstallBuilder attached, this might lead to irreproducible packages")

        n_source=[]
        for s in source:
            if has_no_install_location(s):
                n_source.append(s)
            else:
                for ss in s.sources:
                    n_source.append(ss)
                    copy_attr(s, ss)
                    setattr(ss, 'packaging_install_location', s.get_path())

        return (target, n_source)
    return strip_install_emitter
