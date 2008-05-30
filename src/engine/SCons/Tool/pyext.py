"""SCons.Tool.pyext

Tool-specific initialization for python extensions builder.

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

import sys

import SCons
from SCons.Tool import SourceFileScanner, ProgramScanner

#  Create common python builders

def createPythonObjectBuilder(env):
    """This is a utility function that creates the PythonObject Builder in an
    Environment if it is not there already.

    If it is already there, we return the existing one.
    """

    try:
        pyobj = env['BUILDERS']['PythonObject']
    except KeyError:
        pyobj = SCons.Builder.Builder(action = {},
                                      emitter = {},
                                      prefix = '$PYEXTOBJPREFIX',
                                      suffix = '$PYEXTOBJSUFFIX',
                                      src_builder = ['CFile'],
                                      source_scanner = SourceFileScanner,
                                      single_source = 1)
        env['BUILDERS']['PythonObject'] = pyobj

    return pyobj

def createPythonExtensionBuilder(env):
    """This is a utility function that creates the PythonExtension Builder in
    an Environment if it is not there already.

    If it is already there, we return the existing one.
    """

    try:
        pyext = env['BUILDERS']['PythonExtension']
    except KeyError:
        import SCons.Action
        import SCons.Defaults
        action = SCons.Action.Action("$PYEXTLINKCOM", "$PYEXTLINKCOMSTR")
        action_list = [ SCons.Defaults.SharedCheck,
                        action]
        pyext = SCons.Builder.Builder(action = action_list,
                                      emitter = "$SHLIBEMITTER",
                                      prefix = '$PYEXTPREFIX',
                                      suffix = '$PYEXTSUFFIX',
                                      target_scanner = ProgramScanner,
                                      src_suffix = '$PYEXTOBJSUFFIX',
                                      src_builder = 'PythonObject')
        env['BUILDERS']['PythonExtension'] = pyext

    return pyext

def set_basic_vars(env):
    # Set construction variables which are independant on whether we are using
    # distutils or not.
    env['PYEXTCPPPATH'] = SCons.Util.CLVar('$PYEXTINCPATH')

    env['_PYEXTCPPINCFLAGS'] = '$( ${_concat(INCPREFIX, PYEXTCPPPATH, '\
                               'INCSUFFIX, __env__, RDirs, TARGET, SOURCE)} $)'
    env['PYEXTOBJSUFFIX'] = '$SHOBJSUFFIX'
    env['PYEXTOBJPREFIX'] = '$SHOBJPREFIX'

    # XXX: This won't work in all cases (using mingw, for example). To make
    # this work, we need to know whether PYEXTCC accepts /c and /Fo or -c -o.
    # This is difficult with the current way tools work in scons.
    if sys.platform == 'win32':
        env['PYEXTCCCOM'] = "$PYEXTCC /Fo$TARGET /c $PYEXTCCSHARED "\
                            "$PYEXTCFLAGS $_PYEXTCPPINCFLAGS $SOURCES"
    else:
        env['PYEXTCCCOM'] = "$PYEXTCC -o $TARGET -c $PYEXTCCSHARED "\
                            "$PYEXTCFLAGS $_PYEXTCPPINCFLAGS $SOURCES"

    # XXX: cf comment on PYEXTCCCOM
    if sys.platform == 'win32':
        env['PYEXTLINKCOM'] = '${TEMPFILE("$PYEXTLINK $PYEXTLINKFLAGS /OUT:$TARGET.windows $SOURCES.windows")}'
    else:
        env['PYEXTLINKCOM'] = "$PYEXTLINK -o $TARGET $PYEXTLINKFLAGS $SOURCES"

def set_configuration(env, use_distutils):
    """Set construction variables which are platform dependants.

    If use_distutils == True, use distutils configuration. Otherwise, use
    'sensible' default.

    Any variable already defined is untouched."""

    def_cfg = {'PYEXTCC' : '$SHCC',
               'PYEXTCFLAGS' : '$SHCCFLAGS',
               'PYEXTLINK' : '$LDMODULE',
               'PYEXTLINKFLAGS' : '$LDMODULEFLAGS',
               'PYEXTSUFFIX' : '$SHLIBSUFFIX',
               'PYEXTPREFIX' : ''}

    # We define commands as strings so that we can either execute them using
    # eval (same python for scons and distutils) or by executing them through
    # the shell.
    dist_cfg = {'PYEXTCC': "sysconfig.get_config_var('CC')", 
                'PYEXTCFLAGS': "sysconfig.get_config_var('CFLAGS')", 
                'PYEXTCCSHARED': "sysconfig.get_config_var('CCSHARED')", 
                'PYEXTLINKFLAGS': "sysconfig.get_config_var('LDFLAGS')", 
                'PYEXTLINK': "sysconfig.get_config_var('LDSHARED')", 
                'PYEXTINCPATH': "sysconfig.get_python_inc()", 
                'PYEXTSUFFIX': "sysconfig.get_config_var('SO')"} 

    def ifnotset(name, value):
        if not env.has_key(name):
            env[name] = value

    from distutils import sysconfig

    # We set the python path even when not using distutils, because we rarely
    # want to change this, even if not using distutils
    ifnotset('PYEXTINCPATH', sysconfig.get_python_inc())

    if use_distutils:
        for k, v in dist_cfg.items():
            ifnotset(k, eval(v))
    else:
        for k, v in def_cfg.items():
            ifnotset(k, v)

def generate(env):
    """Add Builders and construction variables for python extensions to an
    Environment."""

    if sys.platform == 'win32':
        raise NotImplementedError(
                "Sorry: building python extensions "\
                "on windows is not supported yet")

    if not env.has_key('PYEXT_USE_DISTUTILS'):
        env['PYEXT_USE_DISTUTILS'] = False

    # This sets all constructions variables used for pyext builders. 
    set_basic_vars(env)

    set_configuration(env, env['PYEXT_USE_DISTUTILS'])

    # Create the PythonObject builder
    pyobj = createPythonObjectBuilder(env)
    action = SCons.Action.Action("$PYEXTCCCOM", "$PYEXTCCCOMSTR")
    pyobj.add_emitter('.c', SCons.Defaults.SharedObjectEmitter)
    pyobj.add_action('.c', action)

    # Create the PythonExtension builder
    createPythonExtensionBuilder(env)

def exists(env):
    try:
        if sys.platform == 'win32':
            return False
        # This is not quite right: if someone defines all variables by himself,
        # it would work without distutils
        from distutils import sysconfig
        return True
    except ImportError:
        return False
