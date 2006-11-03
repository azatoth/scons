"""SCons.Tool.install

Tool-specific initialization for the install tool.

Three normally shouldn't be any need to import this module directly.
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
import SCons.Action
import shutil, os, stat
from SCons.Util import strip_abs_path

#
# We keep track of *all* installed files.
_INSTALLED_FILES = []

#
# Functions doing the actual work of the Install Builder.
#
def copyFunc(dest, source, env):
    """Install a source file into a destination by copying it (and its
    permission/mode bits)."""
    shutil.copy2(source, dest)
    st = os.stat(source)
    os.chmod(dest, stat.S_IMODE(st[stat.ST_MODE]) | stat.S_IWRITE)
    return 0

def installFunc(target, source, env):
    """Install a source file into a target using the function specified
    as the INSTALL construction variable."""
    try:
        install = env['INSTALL']
    except KeyError:
        raise SCons.Errors.UserError('Missing INSTALL construction variable.')

    assert( len(target)==len(source) )
    for t,s in zip(target,source):
        if install(t.get_path(),s.get_path(),env):
            return 1

    return 0

def stringFunc(target, source, env):
    return env.subst_target_source(env['INSTALLSTR'], 0, target, source)

#
# Emitter functions
#
def add_targets_to_INSTALLED_FILES(target, source, env):
    """ an emitter that adds all files to the list in the _INSTALLED_FILES
    variable in env.
    """
    global _INSTALLED_FILES
    files = _INSTALLED_FILES
    files.extend( [ x for x in target if not x in files ] )
    return (target, source)

class DESTDIR_factory:
    """ a node factory, where all files will be relative to the dir supplied
    in the constructor.
    """
    def __init__(self, env, dir):
        self.env = env
        self.dir = env.arg2nodes( dir, env.fs.Dir )[0]

    def Entry(self, name):
        name = strip_abs_path(name)
        return self.dir.Entry(name)

    def Dir(self, name):
        name = strip_abs_path(name)
        return self.dir.Dir(name)

#
# The Builder Definition
#
install_action   = SCons.Action.Action(installFunc, stringFunc)
installas_action = SCons.Action.Action(installFunc, stringFunc)

def generate(env):
    try:
        env['BUILDERS']['Install']
        env['BUILDERS']['InstallAs']
    except KeyError, e:
        if env.has_key('DESTDIR'):
            target_factory = DESTDIR_factory(env, env.subst('$DESTDIR'))
        else:
            target_factory = env.fs

        InstallBuilder = SCons.Builder.Builder(
            action         = install_action,
            target_factory = target_factory.Entry,
            source_factory = env.fs.File,
            multi          = 1,
            emitter        = [ add_targets_to_INSTALLED_FILES, ],
            name           = 'InstallBuilder')

        def InstallBuilderWrapper(env, target, source, dir=None):
            if target and dir:
                raise SCons.Errors.UserError, "Both target and dir defined for Install(), only one may be defined."
            if not dir:
                dir=target
            try:
                dnodes = env.arg2nodes(dir, target_factory.Dir)
            except TypeError:
                raise SCons.Errors.UserError, "Target `%s' of Install() is a file, but should be a directory.  Perhaps you have the Install() arguments backwards?" % str(dir)
            try:
                sources = env.arg2nodes(source, env.fs.File)
            except TypeError:
                if SCons.Util.is_List(source):
                    raise SCons.Errors.UserError, "Source `%s' of Install() contains one or more non-files.  Install() source must be one or more files." % repr(map(str, source))
                else:
                    raise SCons.Errors.UserError, "Source `%s' of Install() is not a file.  Install() source must be one or more files." % str(source)
            tgt = []
            for dnode in dnodes:
                for src in sources:
                    target = env.fs.File(src.name, dnode)
                    tgt.extend(InstallBuilder(env, target, src))
            return tgt

        def InstallAsBuilderWrapper(env, target, source):
            result = []
            for src, tgt in map(lambda x, y: (x, y), source, target):
                result.extend(InstallBuilder(env, tgt, src))
            return result

        env['BUILDERS']['Install']   = InstallBuilderWrapper
        env['BUILDERS']['InstallAs'] = InstallAsBuilderWrapper

    try:
        env['INSTALLSTR']
    except KeyError:
        env['INSTALLSTR'] = 'Install file: "$SOURCES" as "$TARGETS"',

    try:
        env['INSTALL']
    except KeyError:
        env['INSTALL']    = copyFunc

def exists(env):
    return 1

def options(opts):
    from SCons.Options import PathOption

    opts.AddOptions(
        PathOption( [ 'DESTDIR', '--install-sandbox' ], default=None,
                    help='A directory under which all installed files will be placed.',
                    validator=PathOption.PathIsDirCreate,
                  ),

        PathOption( [ 'prefix', '--install-prefix' ], default='/usr/local',
                    help='The prefix which can be configured for every installed files.'
                  ),
    )
