"""SCons.Tool.javac

Tool-specific initialization for javac.

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

import os
import os.path
import string

import SCons.Action
import SCons.Builder
from SCons.Node.FS import _my_normcase
from SCons.Tool.JavaCommon import parse_java_file
import SCons.Util

def classname(path):
    """Turn a string (path name) into a Java class name."""
    return string.replace(os.path.normpath(path), os.sep, '.')

def emit_java_classes(target, source, env):
    """Create and return lists of source java files
    and their corresponding target class files.
    """
    java_suffix = env.get('JAVASUFFIX', '.java')
    class_suffix = env.get('JAVACLASSSUFFIX', '.class')

    target[0].must_be_same(SCons.Node.FS.Dir)
    classdir = target[0]

    s = source[0].rentry().disambiguate()
    if isinstance(s, SCons.Node.FS.File):
        sourcedir = s.dir.rdir()
    elif isinstance(s, SCons.Node.FS.Dir):
        sourcedir = s.rdir()
    else:
        raise SCons.Errors.UserError("Java source must be File or Dir, not '%s'" % s.__class__)

    slist = []
    js = _my_normcase(java_suffix)
    for entry in source:
        entry = entry.rentry().disambiguate()
        if isinstance(entry, SCons.Node.FS.File):
            slist.append(entry)
        elif isinstance(entry, SCons.Node.FS.Dir):
            def visit(arg, dirname, names, js=js, dirnode=entry.rdir()):
                java_files = filter(lambda n, js=js:
                                    _my_normcase(n[-len(js):]) == js,
                                    names)
                # The on-disk entries come back in arbitrary order.  Sort
                # them so our target and source lists are determinate.
                java_files.sort()
                mydir = dirnode.Dir(dirname)
                java_paths = map(lambda f, d=mydir: d.File(f), java_files)
                arg.extend(java_paths)
            os.path.walk(entry.rdir().get_abspath(), visit, slist)
        else:
            raise SCons.Errors.UserError("Java source must be File or Dir, not '%s'" % entry.__class__)

    version = env.get('JAVAVERSION', '1.4')
    tlist = []
    for f in slist:
        pkg_dir, classes = parse_java_file(f.get_abspath(), version)
        if pkg_dir:
            for c in classes:
                t = target[0].Dir(pkg_dir).File(c+class_suffix)
                t.attributes.java_classdir = classdir
                t.attributes.java_sourcedir = sourcedir
                t.attributes.java_classname = classname(pkg_dir + os.sep + c)
                tlist.append(t)
        elif classes:
            for c in classes:
                t = target[0].File(c+class_suffix)
                t.attributes.java_classdir = classdir
                t.attributes.java_sourcedir = sourcedir
                t.attributes.java_classname = classname(c)
                tlist.append(t)
        else:
            # This is an odd end case:  no package and no classes.
            # Just do our best based on the source file name.
            base = str(f)[:-len(java_suffix)]
            t = target[0].File(base + class_suffix)
            t.attributes.java_classdir = classdir
            t.attributes.java_sourcedir = sourcedir
            t.attributes.java_classname = classname(base)
            tlist.append(t)

    return tlist, slist

JavaAction = SCons.Action.Action('$JAVACCOM', '$JAVACCOMSTR')

JavaBuilder = SCons.Builder.Builder(action = JavaAction,
                    emitter = emit_java_classes,
                    target_factory = SCons.Node.FS.Entry,
                    source_factory = SCons.Node.FS.Entry)

def getClassPath(env,target, source, for_signature):
    path = ""
    if env.has_key('JAVACLASSPATH') and env['JAVACLASSPATH']:
        path = SCons.Util.AppendPath(path, env['JAVACLASSPATH'])
        return "-classpath %s" % (path)
    else:
        return ""

def getSourcePath(env,target, source, for_signature):
    path = ""
    if env.has_key('JAVASOURCEPATH') and env['JAVASOURCEPATH']:
        path = SCons.Util.AppendPath(path, env['JAVASOURCEPATH'])
    path = SCons.Util.AppendPath(path,['${TARGET.attributes.java_sourcedir}'])
    return "-sourcepath %s" % (path)

def generate(env):
    """Add Builders and construction variables for javac to an Environment."""
    java_file = SCons.Tool.CreateJavaFileBuilder(env)
    java_class = SCons.Tool.CreateJavaClassBuilder(env)
    java_class_dir = SCons.Tool.CreateJavaClassDirBuilder(env)
    java_class.add_emitter(None, emit_java_classes)
    java_class.add_emitter(env.subst('$JAVASUFFIX'), emit_java_classes)
    java_class_dir.emitter = emit_java_classes

    env['JAVAC']            = 'javac'
    env['JAVACFLAGS']       = SCons.Util.CLVar('')
    env['JAVACLASSPATH']    = []
    env['JAVASOURCEPATH']   = []
    env['_JAVACLASSPATH']   = getClassPath
    env['_JAVASOURCEPATH']  = getSourcePath
    env['_JAVACCOM']        = '$JAVAC $JAVACFLAGS $_JAVACLASSPATH -d ${TARGET.attributes.java_classdir} $_JAVASOURCEPATH $SOURCES'
    env['JAVACCOM']         = "${TEMPFILE('$_JAVACCOM')}"
    env['JAVACLASSSUFFIX']  = '.class'
    env['JAVASUFFIX']       = '.java'

def exists(env):
    return 1
