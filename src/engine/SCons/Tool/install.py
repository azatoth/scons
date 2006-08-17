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
import SCons
import shutil, os, stat

#
# Functions to handle options of the install Builder.
#
install_sandbox = None

def set_install_sandbox(option, opt, value, parser):
    global install_sandbox
    install_sandbox = value

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
def dir_argument_override(target, source, env):
    """ The dir argument to the Install Builder overrides all targets.
    """
    if env.has_key('dir'):
        target = env.arg2nodes( env['dir'], env.fs.Dir )

    return (target, source)

def create_install_targets(target, source, env):
    """ create all install targets.
    """
    n_target = []
    for t in target:
        for s in source:
            n_target.append( env.fs.File(s.name, t) )

    return (n_target, source)

class sandbox_factory:
    def __init__(self, env, dir):
        self.env = env
        self.dir = env.arg2nodes( dir, env.fs.Dir )[0]

    def File(self, name):
        name = self.env.strip_abs_path(name)
        return self.dir.File(name)

    def Dir(self, name):
        name = self.env.strip_abs_path(name)
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
        target_factory = env.fs
        if install_sandbox:
            target_factory = sandbox_factory(env, install_sandbox)

        env['BUILDERS']['Install'] = SCons.Builder.Builder(
            action         = install_action,
            target_factory = target_factory.Dir,
            source_factory = env.fs.File,
            multi          = 1,
            emitter        = [ dir_argument_override,
                               create_install_targets ],
            name           = 'InstallBuilder')

        env['BUILDERS']['InstallAs'] = SCons.Builder.Builder(
            action         = installas_action,
            target_factory = target_factory.File,
            source_factory = env.fs.File,
            name           = 'InstallAsBuilder')


    env['INSTALLSTR'] = 'Install file(s): "$SOURCES" as "$TARGETS"',
    env['INSTALL']    = copyFunc

def exists(env):
    return 1
