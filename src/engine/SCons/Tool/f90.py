"""engine.SCons.Tool.f90

Tool-specific initialization for the generic Posix f90 Fortran compiler.

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
import SCons.Scanner.Fortran
import SCons.Tool
import SCons.Util
import fortran
from SCons.Tool.FortranCommon import FortranEmitter, ShFortranEmitter, \
                                     ComputeFortranSuffixes,\
                                     CreateDialectGenerator, \
                                     CreateDialectActions

compilers = ['f90']

#
F90Suffixes = ['.f90']
F90PPSuffixes = []
ComputeFortranSuffixes(F90Suffixes, F90PPSuffixes)

#
F90Scan = SCons.Scanner.Fortran.FortranScan("F90PATH")

for suffix in F90Suffixes + F90PPSuffixes:
    SCons.Tool.SourceFileScanner.add_scanner(suffix, F90Scan)
del suffix

#
F90Gen, F90FlagsGen, F90ComGen, F90ComStrGen, F90PPComGen, \
F90PPComStrGen, ShF90Gen, ShF90FlagsGen, ShF90ComGen, \
ShF90ComStrGen, ShF90PPComGen, ShF90PPComStrGen = \
    CreateDialectGenerator("F90", "FORTRAN", "_F90D")

#
F90Action, F90PPAction, ShF90Action, ShF90PPAction = CreateDialectActions("F90")

def add_to_env(env):
    """Add Builders and construction variables for f90 to an Environment."""
    env.AppendUnique(FORTRANSUFFIXES = F90Suffixes + F90PPSuffixes)

    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    for suffix in F90Suffixes:
        static_obj.add_action(suffix, F90Action)
        shared_obj.add_action(suffix, ShF90Action)
        static_obj.add_emitter(suffix, FortranEmitter)
        shared_obj.add_emitter(suffix, ShFortranEmitter)

    for suffix in F90PPSuffixes:
        static_obj.add_action(suffix, F90PPAction)
        shared_obj.add_action(suffix, ShF90PPAction)
        static_obj.add_emitter(suffix, FortranEmitter)
        shared_obj.add_emitter(suffix, ShFortranEmitter)
  
    env['_F90G']            = F90Gen
    env['_F90FLAGSG']       = F90FlagsGen
    env['_F90COMG']         = F90ComGen
    env['_F90COMSTRG']      = F90ComStrGen
    env['_F90PPCOMG']       = F90PPComGen
    env['_F90PPCOMSTRG']    = F90PPComStrGen

    env['_SHF90G']          = ShF90Gen
    env['_SHF90FLAGSG']     = ShF90FlagsGen
    env['_SHF90COMG']       = ShF90ComGen
    env['_SHF90COMSTRG']    = ShF90ComStrGen
    env['_SHF90PPCOMG']     = ShF90PPComGen
    env['_SHF90PPCOMSTRG']  = ShF90PPComStrGen

    env['_F90INCFLAGS'] = '$( ${_concat(INCPREFIX, F90PATH, INCSUFFIX, __env__, RDirs, TARGET, SOURCE)} $)'
    env['_F90COMD']     = '$_F90G -o $TARGET -c $_F90FLAGSG $_F90INCFLAGS $_FORTRANMODFLAG $SOURCES'
    env['_F90PPCOMD']   = '$_F90G -o $TARGET -c $_F90FLAGSG $CPPFLAGS $_CPPDEFFLAGS $_F90INCFLAGS $_FORTRANMODFLAG $SOURCES'
    env['_SHF90COMD']   = '$_SHF90G -o $TARGET -c $_SHF90FLAGSG $_F90INCFLAGS $_FORTRANMODFLAG $SOURCES'
    env['_SHF90PPCOMD'] = '$_SHF90G -o $TARGET -c $_SHF90FLAGSG $CPPFLAGS $_CPPDEFFLAGS $_F90INCFLAGS $_FORTRANMODFLAG $SOURCES'

def generate(env):
    fortran.add_to_env(env)

    import f77
    f77.add_to_env(env)

    add_to_env(env)

    env['_FORTRAND']        = env.Detect(compilers) or 'f90'

def exists(env):
    return env.Detect(compilers)
