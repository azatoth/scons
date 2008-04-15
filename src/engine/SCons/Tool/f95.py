"""engine.SCons.Tool.f95

Tool-specific initialization for the generic Posix f95 Fortran compiler.

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

import SCons.Defaults
import SCons.Tool
import SCons.Util
import fortran
from SCons.Tool.FortranCommon import FortranEmitter, ShFortranEmitter, \
                                     ComputeFortranSuffixes,\
                                     CreateDialectGenerator, \
                                     CreateDialectActions

compilers = ['f95']

#
F95Suffixes = ['.f95']
F95PPSuffixes = []
ComputeFortranSuffixes(F95Suffixes, F95PPSuffixes)

#
F95Scan = SCons.Scanner.Fortran.FortranScan("F95PATH")

for suffix in F95Suffixes + F95PPSuffixes:
    SCons.Tool.SourceFileScanner.add_scanner(suffix, F95Scan)
del suffix

#
F95Gen, F95FlagsGen, F95ComGen, F95ComStrGen, F95PPComGen, \
F95PPComStrGen, ShF95Gen, ShF95FlagsGen, ShF95ComGen, \
ShF95ComStrGen, ShF95PPComGen, ShF95PPComStrGen = \
    CreateDialectGenerator("F95", "FORTRAN", "_F95D")

#
F95Action, F95PPAction, ShF95Action, ShF95PPAction = CreateDialectActions("F95")

def add_to_env(env):
    """Add Builders and construction variables for f95 to an Environment."""
    env.AppendUnique(FORTRANSUFFIXES = F95Suffixes + F95PPSuffixes)

    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    for suffix in F95Suffixes:
        static_obj.add_action(suffix, F95Action)
        shared_obj.add_action(suffix, ShF95Action)
        static_obj.add_emitter(suffix, FortranEmitter)
        shared_obj.add_emitter(suffix, ShFortranEmitter)

    for suffix in F95PPSuffixes:
        static_obj.add_action(suffix, F95PPAction)
        shared_obj.add_action(suffix, ShF95PPAction)
        static_obj.add_emitter(suffix, FortranEmitter)
        shared_obj.add_emitter(suffix, ShFortranEmitter)

    env['_F95G']           = F95Gen
    env['_F95FLAGSG']      = F95FlagsGen
    env['_F95COMG']        = F95ComGen
    env['_F95COMSTRG']     = F95ComStrGen
    env['_F95PPCOMG']      = F95PPComGen
    env['_F95PPCOMSTRG']   = F95PPComStrGen

    env['_SHF95G']         = ShF95Gen
    env['_SHF95FLAGSG']    = ShF95FlagsGen
    env['_SHF95COMG']      = ShF95ComGen
    env['_SHF95COMSTRG']   = ShF95ComStrGen
    env['_SHF95PPCOMG']    = ShF95PPComGen
    env['_SHF95PPCOMSTRG'] = ShF95PPComStrGen

    env['_F95INCFLAGS'] = '$( ${_concat(INCPREFIX, F95PATH, INCSUFFIX, __env__, RDirs, TARGET, SOURCE)} $)'

    env['_F95COMD']     = '$_F95G -o $TARGET -c $_F95FLAGSG $_F95INCFLAGS $_FORTRANMODFLAG $SOURCES'
    env['_F95PPCOMD']   = '$_F95G -o $TARGET -c $_F95FLAGSG $CPPFLAGS $_CPPDEFFLAGS $_F95INCFLAGS $_FORTRANMODFLAG $SOURCES'
    env['_SHF95COMD']   = '$_SHF95G -o $TARGET -c $_SHF95FLAGSG $_F95INCFLAGS $_FORTRANMODFLAG $SOURCES'
    env['_SHF95PPCOMD'] = '$_SHF95G -o $TARGET -c $_SHF95FLAGSG $CPPFLAGS $_CPPDEFFLAGS $_F95INCFLAGS $_FORTRANMODFLAG $SOURCES'

def generate(env):
    fortran.add_to_env(env)

    import f77
    f77.add_to_env(env)

    import f90
    f90.add_to_env(env)

    add_to_env(env)

    env['_FORTRAND']        = env.Detect(compilers) or 'f95'

def exists(env):
    return env.Detect(compilers)
