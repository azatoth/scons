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
    from distutils import sysconfig
    env['PYEXTINCPATH'] = sysconfig.get_python_inc()
    env['PYEXTCPPPATH'] = SCons.Util.CLVar('$PYEXTINCPATH')

    env['_PYEXTCPPINCFLAGS'] = '$( ${_concat(INCPREFIX, PYEXTCPPPATH, '\
                               'INCSUFFIX, __env__, RDirs, TARGET, SOURCE)} $)'
    env['PYEXTOBJSUFFIX'] = '$SHOBJSUFFIX'
    env['PYEXTOBJPREFIX'] = '$SHOBJPREFIX'

    # XXX: This won't work with MS tools ...
    env['PYEXTCCCOM'] = "$PYEXTCC -o $TARGET -c $PYEXTCCSHARED "\
                        "$PYEXTCFLAGS $_PYEXTCPPINCFLAGS $SOURCES"

    # XXX: This won't work with MS tools ...
    env['PYEXTLINKCOM'] = "$PYEXTLINK -o $TARGET $PYEXTLINKFLAGS $SOURCES"

    set_default(env)

def set_default(env):
    if not env.has_key('PYEXTCC'):
        env['PYEXTCC'] = '$CC'

    if not env.has_key('PYEXTLINK'):
        env['PYEXTLINK'] = '$LDMODULE'

    if not env.has_key('PYEXTLINKFLAGS'):
        env['PYEXTLINKFLAGS'] = '$LDMODULEFLAGS'
    else:
        env['PYEXTLINKFLAGS'] = SCons.Util.CLVar('$PYEXTLINKFLAGS ' \
                                                 '$LDMODULEFLAGS')

    if not env.has_key('PYEXTSUFFIX'):
        env['PYEXTSUFFIX'] = '$SHLIBSUFFIX'

def generate(env):
    """Add Builders and construction variables for python extensions to an
    Environment."""

    # This sets all constructions variables used in actions, like PYEXTCC,
    # etc...
    set_basic_vars(env)

    # Create the PythonObject builder
    pyobj = createPythonObjectBuilder(env)
    action = SCons.Action.Action("$PYEXTCCCOM", "$PYEXTCCCOMSTR")
    pyobj.add_emitter('.c', SCons.Defaults.SharedObjectEmitter)
    pyobj.add_action('.c', action)

    # Create the PythonExtension builder
    createPythonExtensionBuilder(env)

def exists(env):
    try:
        from distutils import sysconfig
        return True
    except ImportError:
        return False
