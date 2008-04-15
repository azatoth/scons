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
import os.path

import SCons.Action
import SCons.Defaults
import SCons.Scanner.Fortran
import SCons.Tool
import SCons.Util

def isfortran(env, source):
    """Return 1 if any of code in source has fortran files in it, 0
    otherwise."""
    try:
        fsuffixes = env['FORTRANSUFFIXES']
    except KeyError:
        # If no FORTRANSUFFIXES, no fortran tool, so there is no need to look
        # for fortran sources.
        return 0

    if not source:
        # Source might be None for unusual cases like SConf.
        return 0
    for s in source:
        if s.sources:
            ext = os.path.splitext(str(s.sources[0]))[1]
            if ext in fsuffixes:
                return 1
    return 0

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

def CreateDialectActions(dialect):
    """Create dialect specific actions."""
    CompAction = SCons.Action.Action('$%sCOM ' % dialect, '$%sCOMSTR' % dialect)
    CompPPAction = SCons.Action.Action('$%sPPCOM ' % dialect, '$%sPPCOMSTR' % dialect)
    ShCompAction = SCons.Action.Action('$SH%sCOM ' % dialect, '$SH%sCOMSTR' % dialect)
    ShCompPPAction = SCons.Action.Action('$SH%sPPCOM ' % dialect, '$SH%sPPCOMSTR' % dialect)

    return CompAction, CompPPAction, ShCompAction, ShCompPPAction

def DialectAddToEnv(env, dialect, fallback, default, suffixes, ppsuffixes,
                    support_module = 0):
    """Add dialect specific construction variables."""
    ComputeFortranSuffixes(suffixes, ppsuffixes)

    fscan = SCons.Scanner.Fortran.FortranScan("%sPATH" % dialect)

    for suffix in suffixes + ppsuffixes:
        SCons.Tool.SourceFileScanner.add_scanner(suffix, fscan)

    env.AppendUnique(FORTRANSUFFIXES = suffixes + ppsuffixes)

    compaction, compppaction, shcompaction, shcompppaction = \
            CreateDialectActions(dialect)

    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    for suffix in suffixes:
        static_obj.add_action(suffix, compaction)
        shared_obj.add_action(suffix, shcompaction)
        static_obj.add_emitter(suffix, FortranEmitter)
        shared_obj.add_emitter(suffix, ShFortranEmitter)

    for suffix in ppsuffixes:
        static_obj.add_action(suffix, compppaction)
        shared_obj.add_action(suffix, shcompppaction)
        static_obj.add_emitter(suffix, FortranEmitter)
        shared_obj.add_emitter(suffix, ShFortranEmitter)

    if not env.has_key('%sFLAGS' % dialect):
        env['%sFLAGS' % dialect] = SCons.Util.CLVar('')

    if not env.has_key('SH%sFLAGS' % dialect):
        env['SH%sFLAGS' % dialect] = SCons.Util.CLVar('$%sFLAGS' % dialect)

    env['_%sINCFLAGS' % dialect] = '$( ${_concat(INCPREFIX, %sPATH, INCSUFFIX, __env__, RDirs, TARGET, SOURCE)} $)' % dialect

    if support_module == 1:
        env['%sCOM' % dialect]     = '$%s -o $TARGET -c $%sFLAGS $_%sINCFLAGS $_FORTRANMODFLAG $SOURCES' % (dialect, dialect, dialect)
        env['%sPPCOM' % dialect]   = '$%s -o $TARGET -c $%sFLAGS $CPPFLAGS $_CPPDEFFLAGS $_%sINCFLAGS $_FORTRANMODFLAG $SOURCES' % (dialect, dialect, dialect)
        env['SH%sCOM' % dialect]    = '$SH%s -o $TARGET -c $SH%sFLAGS $_%sINCFLAGS $_FORTRANMODFLAG $SOURCES' % (dialect, dialect, dialect)
        env['SH%sPPCOM' % dialect]  = '$SH%s -o $TARGET -c $SH%sFLAGS $CPPFLAGS $_CPPDEFFLAGS $_%sINCFLAGS $_FORTRANMODFLAG $SOURCES' % (dialect, dialect, dialect)
    else:
        env['%sCOM' % dialect]     = '$%s -o $TARGET -c $%sFLAGS $_%sINCFLAGS $SOURCES' % (dialect, dialect, dialect)
        env['%sPPCOM' % dialect]   = '$%s -o $TARGET -c $%sFLAGS $CPPFLAGS $_CPPDEFFLAGS $_%sINCFLAGS $SOURCES' % (dialect, dialect, dialect)
        env['SH%sCOM' % dialect]    = '$SH%s -o $TARGET -c $SH%sFLAGS $_%sINCFLAGS $SOURCES' % (dialect, dialect, dialect)
        env['SH%sPPCOM' % dialect]  = '$SH%s -o $TARGET -c $SH%sFLAGS $CPPFLAGS $_CPPDEFFLAGS $_%sINCFLAGS $SOURCES' % (dialect, dialect, dialect)
