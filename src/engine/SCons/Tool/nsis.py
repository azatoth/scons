"""SCons.Tool.nsis
 
This tool provides SCons support for the Nullsoft Scriptable Install System,
a windows installer builder available at http://nsis.sourceforge.net/home

You can do 'env.Installer("foobar")' which will read foobar.nsi and
create dependencies on all the files you put into your installer, so that if
anything changes your installer will be rebuilt.  It also makes the target
equal to the filename you specified in foobar.nsi.  Wildcards are handled correctly.

In addition, if you set NSISDEFINES to a dictionary, those variables will be passed
to NSIS.
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
# Originally written by Mike Elkins, January 2004

import SCons.Builder
import SCons.Util
import SCons.Scanner
import os
import os.path
import sys

is_windows = (sys.platform == 'win32')

def quoteIfSpaced(text):
    if ' ' in text:
        return '"'+text+'"'
    else:
        return text
    
def toString(item,env):
    if type(item) == list:
        ret = ''
        for i in item:
            if ret:
                ret += ' '
            val = toString(i,env)
            if ' ' in val:
                val = "'"+val+"'"
            ret += val
        return ret
    else:
        # For convienence, handle #s here
        if str(item).startswith('#'):
            item = env.File(item).get_abspath()
        return str(item)

def runNSIS(source,target,env,for_signature):
    ret = quoteIfSpaced(env['NSIS'])+" "
    if env.has_key('NSISFLAGS'):
        for flag in env['NSISFLAGS']:
            ret += flag
            ret += ' '
    if env.has_key('NSISDEFINES'):
        for d in env['NSISDEFINES'].keys():
            ret += '-D'+d
            if env['NSISDEFINES'][d]:
                ret +='='+quoteIfSpaced(toString(env['NSISDEFINES'][d],env))
            ret += ' '
        
        ret += '-- '
    for s in source:
        ret += quoteIfSpaced(str(s))
    return ret
    
def nsis_emitter( source, target, env ):
    """
    The emitter changes the target name to match what the command actually will
    output, which is the argument to the OutFile command.
    """
    nsp = nsis_parse(source,'OutFile',0, env['NSISDEFINES'])
    if not nsp:
        # Assume that the installer will have the same name as the first source file
        target = nsis_path(str(source[0]), env['NSISDEFINES'], '')
        target = os.path.splitext(target)[0] + '.exe'
        return (target,source)
    nsp = nsis_path(nsp,env['NSISDEFINES'],'')
    if not SCons.Util.is_List(nsp):
        nsp = [ nsp]
    for n in range(0, len(source)):
        nsp[n] = os.path.join(os.path.dirname(str(source[n])), nsp[n])
    x  = (
        nsp,
        source)
    return x

def nsis_path( filename, nsisdefines, rootdir ):
    """
    Do environment replacement, and prepend with the SCons root dir if
    necessary
    """
    # We can't do variables defined by NSIS itself (like $INSTDIR),
    # only user supplied ones (like ${FOO})
    varPos = filename.find('${')
    while varPos != -1:
        endpos = filename.find('}',varPos)
        assert endpos != -1
        if not nsisdefines.has_key(filename[varPos+2:endpos]):
            raise KeyError ("Could not find %s in NSISDEFINES" % filename[varPos+2:endpos])
        val = nsisdefines[filename[varPos+2:endpos]]
        if type(val) == list:
            if varPos != 0 or endpos+1 != len(filename):
                raise Exception("Can't use lists on variables that aren't complete filenames")
            return val
        filename = filename[0:varPos] + val + filename[endpos+1:]
        varPos = filename.find('${')
    return filename
    
def nsis_scanner( node, env, path, source_dir = None, known_includes = None, include_dirs = None):
    """
    The scanner that looks through the source .nsi files and finds all lines
    that are the 'File' command, fixes the directories etc, and returns them.
    """
    nodes = node.rfile()
    if not node.exists():
        return []
    nodes = []
    if source_dir is None:
        try:
            source_dir = env['NSISSRCDIR']
        except:
            source_dir = node.get_dir()
    if known_includes is None:
        known_includes = []
    if include_dirs is None:
        nsis_install_location = os.path.dirname(env.WhereIs(env['NSIS']))
        if is_windows:
            nsis_include_dir = os.path.abspath(os.path.join(nsis_install_location, 'Include'))
        else:
            # get ../bin/makensis and go up two directories
             nsis_include_dir = os.path.abspath(os.path.join(nsis_install_location, '..', 'share', 'nsis', 'Include'))
        include_dirs = [nsis_include_dir]
    for include in nsis_parse([node],'file',1, env['NSISDEFINES']):
        exp = nsis_path(include,env['NSISDEFINES'],source_dir)
        if type(exp) != list:
            exp = [exp]
        for p in exp:
            for filename in env.Glob( os.path.abspath(
                os.path.join(str(source_dir),p))):
                    # Why absolute path?  Cause it breaks mysteriously without it :(
                    nodes.append(filename)
    for include_dir in nsis_parse([node], '!addincludedir', 1, env['NSISDEFINES']):
        if not os.path.isabs(include_dir):
            new_include_dir = os.path.abspath(os.path.join(str(source_dir), include_dir))
        else:
            new_include_dir = include_dir
        if new_include_dir not in include_dirs:
            include_dirs.append(new_include_dir)
    for include in nsis_parse([node],'!include',1, env['NSISDEFINES']):
        exp = nsis_path(include,env['NSISDEFINES'],source_dir)
        if type(exp) != list:
            exp = [exp]
        for p in exp:
            if p not in [ 'LogicLib.nsh', 'MUI2.nsh' ]:
                for include_dir in include_dirs:
                    filename = os.path.join(include_dir, p)
                    if os.path.isfile(filename):
                        break
                if not os.path.isfile(filename):
                    filename = os.path.abspath(os.path.join(str(source_dir),p))
                # Why absolute path?  Cause it breaks mysteriously without it :(
                if filename not in known_includes:
                        nodes.append(filename)
                        known_includes.append(filename)
                        nodes += nsis_scanner(env.File(filename), env, path, source_dir = source_dir, 
                                              known_includes = known_includes, include_dirs = include_dirs)
    return nodes

def nsis_parse( sources, keyword, multiple, nsisdefines ):
    """
    A function that knows how to read a .nsi file and figure
    out what files are referenced, or find the 'OutFile' line.

    sources is a list of nsi files.
    keyword is the command ('File' or 'OutFile') to look for
    multiple is true if you want all the args as a list, false if you
    just want the first one.
    """
    stuff = []
    current_ignored = 0
    for s in sources:
        c = s.get_contents()
        linenum = 0
        for l in c.split('\n'):
            linenum += 1
            try:
                semi = l.find(';')
                if (semi != -1):
                    l = l[:semi]
                hash = l.find('#')
                if (hash != -1):
                    l = l[:hash]
                # Look for the keyword
                l = l.strip()
                spl = l.split(None,1)
                if len(spl) == 1 and current_ignored > 0 and spl[0].capitalize() == '!endif':
                    current_ignored -= 1
                elif len(spl) > 1:
                    if current_ignored > 0 and spl[0].capitalize() in [ '!ifdef', '!ifmacrodef', '!ifndef' ]:
                        current_ignored += 1
                    elif current_ignored == 0 and spl[0].capitalize() == '!ifdef' and spl[1] not in nsisdefines:
                        current_ignored += 1
                    elif current_ignored == 0 and spl[0].capitalize() == '!ifndef' and spl[1] in nsisdefines:
                        current_ignored += 1
                    elif current_ignored == 0 and spl[0].capitalize() == keyword.capitalize():
                        arg = spl[1]
                        if keyword.capitalize() == 'File' and arg.lower().startswith('/oname') and len(spl) > 1:
                            arg = spl[2]
                        if arg.startswith('"') and arg.endswith('"'):
                            arg = arg[1:-1]
                        if multiple:
                            stuff += [ arg ]
                        else:
                            return arg
            except:
                print "in %(source)s, line %(linenum)d\n" % { 'source': s, 'linenum': linenum }
                raise
    return stuff

def find_nsis(env):
    nsis_exe = 'makensis'
    
    nsis = env.Detect(nsis_exe)
    if nsis:
        return nsis

    if is_windows:
        env_vars = ['ProgramFiles', 'ProgramFiles(x86)']
        
        for var in env_vars:
            if os.environ.has_key(var):
                nsis = os.path.join(os.environ[var], 'NSIS', nsis_exe + '.exe')
                if os.path.isfile(nsis):
                    return nsis
    else:
        locations = ['/usr/bin', '/usr/local/bin']
        
        for location in locations:
            nsis = os.path.join(location, nsis_exe)
            if os.path.isfile(nsis):
                return nsis

    return None

def generate(env):
    env['BUILDERS']['NSISInstaller'] = SCons.Builder.Builder(generator=runNSIS,
                                       src_suffix='.nsi',
                                       emitter=nsis_emitter)
    env.Append(SCANNERS = SCons.Scanner.Scanner( function = nsis_scanner,
               skeys = ['.nsi','.nsh']))
    if not env.has_key('NSISDEFINES'):
        env['NSISDEFINES'] = {}
    env['NSIS'] = find_nsis(env)

def exists(env):
    return find_nsis(env)
