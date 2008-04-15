"""SCons.Tool.FortranCommon

Stuff for processing Fortran, common to all fortran dialects.

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

import re
import string

import SCons.Action
import SCons.Defaults
import SCons.Scanner.Fortran
import SCons.Tool
import SCons.Util

def _fortranEmitter(target, source, env):
    node = source[0].rfile()
    if not node.exists() and not node.is_derived():
       print "Could not locate " + str(node.name)
       return ([], [])
    mod_regex = """(?i)^\s*MODULE\s+(?!PROCEDURE)(\w+)"""
    cre = re.compile(mod_regex,re.M)
    # Retrieve all USE'd module names
    modules = cre.findall(node.get_contents())
    # Remove unique items from the list
    modules = SCons.Util.unique(modules)
    # Convert module name to a .mod filename
    suffix = env.subst('$FORTRANMODSUFFIX', target=target, source=source)
    moddir = env.subst('$FORTRANMODDIR', target=target, source=source)
    modules = map(lambda x, s=suffix: string.lower(x) + s, modules)
    for m in modules:
       target.append(env.fs.File(m, moddir))
    return (target, source)

def FortranEmitter(target, source, env):
    target, source = _fortranEmitter(target, source, env)
    return SCons.Defaults.StaticObjectEmitter(target, source, env)

def ShFortranEmitter(target, source, env):
    target, source = _fortranEmitter(target, source, env)
    return SCons.Defaults.SharedObjectEmitter(target, source, env)

def ComputeFortranSuffixes(suffixes, ppsuffixes):
    """suffixes are fortran source files, and ppsuffixes the ones to be
    pre-processed. Both should be sequences, not strings."""
    assert len(suffixes) > 0
    s = suffixes[0]
    sup = string.upper(s)
    if SCons.Util.case_sensitive_suffixes(s, sup):
        for i in suffixes:
            ppsuffixes.append(string.upper(i))
    else:
        for i in suffixes:
            suffixes.append(string.upper(i))

class VariableListGenerator:
    def __init__(self, *variablelist):
        self.variablelist = variablelist
    def __call__(self, env, target, source, for_signature=0):
        for v in self.variablelist:
            try: return env[v]
            except KeyError: pass
        return ''

def CreateDialectGenerator(dialect, fallback, default):
    """Create the generator variable for a given fortran dialect, fallback and
    default.
    
    All arguments should be upper case strings: F77, FORTRAN, _FORTRAND,
    etc..."""
    # This is ugly, but this code should not stay long anyway. It will make
    # changing fortran tools easier, because everything is in one place.
    fVLG = VariableListGenerator

    CompGen = fVLG(dialect, fallback, default)
    FlagsGen = fVLG('%sFLAGS' % dialect, '%sFLAGS' % fallback)
    ComGen = fVLG('%sCOM' % dialect, '%sCOM' % fallback, '_%sCOMD' % dialect)
    ComStrGen = fVLG('%sCOMSTR' % dialect, '%sCOMSTR' % fallback, '_%sCOMSTRD' % dialect)
    PPComGen = fVLG('%sPPCOM' % dialect, '%sPPCOM' % fallback, '_%sPPCOMD' % dialect)
    PPComStrGen = fVLG('%sPPCOMSTR' % dialect, '%sPPCOMSTR' % fallback, '_%sPPCOMSTRD' % dialect)
    ShCompGen = fVLG('SH%s' % dialect, 'SH%s' % fallback, '%s' % dialect, '%s' % fallback, '_FORTRAND')
    ShFlagsGen = fVLG('SH%sFLAGS' % dialect, 'SH%sFLAGS' % fallback)
    ShComGen = fVLG('SH%sCOM' % dialect, 'SH%sCOM' % fallback, '_SH%sCOMD' % dialect)
    ShComStrGen = fVLG('SH%sCOMSTR' % dialect, 'SH%sCOMSTR' % fallback, '_SH%sCOMSTRD' % dialect)
    ShPPComGen = fVLG('SH%sPPCOM' % dialect, 'SH%sPPCOM' % fallback, '_SH%sPPCOMD' % dialect)
    ShPPComStrGen = fVLG('SH%sPPCOMSTR' % dialect, 'SH%sPPCOMSTR' % fallback, '_SH%sPPCOMSTRD' % dialect)

    return CompGen, FlagsGen, ComGen, ComStrGen, PPComGen, PPComStrGen, \
           ShCompGen, ShFlagsGen, ShComGen, ShComStrGen, ShPPComGen, \
           ShPPComStrGen
