########################################################################
# Imports
########################################################################

import qm
import qm.test.base
from   qm.fields import *
from   qm.executable import *
from   qm.test import database
from   qm.test import test
from   qm.test import resource
from   qm.test import suite
from   qm.test.directory_suite import DirectorySuite
from   qm.extension import get_extension_class_name, get_class_arguments_as_dictionary
import os, dircache

if sys.platform == 'win32':
    console = 'con'
else:
    console = '/dev/tty'

def Trace(msg):
    open(console, 'w').write(msg)

########################################################################
# Classes
########################################################################

def get_explicit_arguments(e):
    """This function can be removed once QMTest 2.4 is out."""

    # Get all of the arguments.
    arguments = get_class_arguments_as_dictionary(e.__class__)
    # Determine which subset of the 'arguments' have been set
    # explicitly.
    explicit_arguments = {}
    for name, field in arguments.items():
        # Do not record computed fields.
        if field.IsComputed():
            continue
        if e.__dict__.has_key(name):
            explicit_arguments[name] = e.__dict__[name]

    return explicit_arguments


def check_exit_status(result, prefix, desc, status):
    """This function can be removed once QMTest 2.4 is out."""

    if sys.platform == "win32" or os.WIFEXITED(status):
        # Obtain the exit code.
        if sys.platform == "win32":
            exit_code = status
        else:
            exit_code = os.WEXITSTATUS(status)
            # If the exit code is non-zero, the test fails.
        if exit_code != 0:
            result.Fail("%s failed with exit code %d." % (desc, exit_code))
            # Record the exit code in the result.
            result[prefix + "exit_code"] = str(exit_code)
            return False

    elif os.WIFSIGNALED(status):
        # Obtain the signal number.
        signal = os.WTERMSIG(status)
        # If the program gets a fatal signal, the test fails .
        result.Fail("%s received fatal signal %d." % (desc, signal))
        result[prefix + "signal"] = str(signal)
        return False
    else:
        # A process should only be able to stop by exiting, or
        # by being terminated with a signal.
        assert None

    return True

# XXX I'd like to annotate the overal test run with the following
# information about the Python version, SCons version, and environment.
# Not sure how to do that yet; ask Stefan.
#
#    sys_keys = ['byteorder', 'exec_prefix', 'executable', 'maxint', 'maxunicode', 'platform', 'prefix', 'version', 'version_info']

# "    <%s>" % tag
# "      <version>%s</version>" % module.__version__
# "      <build>%s</build>" % module.__build__
# "      <buildsys>%s</buildsys>" % module.__buildsys__
# "      <date>%s</date>" % module.__date__
# "      <developer>%s</developer>" % module.__developer__
# "    </%s>" % tag

# "  <scons>"
#    print_version_info("script", scons)
#    print_version_info("engine", SCons)
# "  </scons>"

#    environ_keys = [
#        'PATH',
#        'SCONSFLAGS',
#        'SCONS_LIB_DIR',
#        'PYTHON_ROOT',
#        'QTDIR',
#
#        'COMSPEC',
#        'INTEL_LICENSE_FILE',
#        'INCLUDE',
#        'LIB',
#        'MSDEVDIR',
#        'OS',
#        'PATHEXT',
#        'SYSTEMROOT',
#        'TEMP',
#        'TMP',
#        'USERNAME',
#        'VXDOMNTOOLS',
#        'WINDIR',
#        'XYZZY'
#
#        'ENV',
#        'HOME',
#        'LANG',
#        'LANGUAGE',
#        'LOGNAME',
#        'MACHINE',
#        'OLDPWD',
#        'PWD',
#        'OPSYS',
#        'SHELL',
#        'TMPDIR',
#        'USER',
#    ]

class Test(test.Test):
    """Simple test that runs a python script and checks the status
    to determine whether the test passes."""

    script = TextField(title="Script to test")
    topdir = TextField(title="Top source directory")

    def Run(self, context, result):
        """Run the test. The test passes if the command exits with status=0,
        and fails otherwise. The program output is logged, but not validated."""

        # FIXME: the following is necessary to pull in half of the testing
        #        harness from $srcdir/etc. These modules should be transfered
        #        to here, eventually.
        python_path = os.path.join(self.topdir, 'etc')
        scons = os.path.join(self.topdir, 'src', 'script', 'scons.py')
        lib_dir = os.path.join(self.topdir, 'src', 'engine')
        if not os.path.isabs(lib_dir):
            lib_dir = os.path.join(os.getcwd(), lib_dir)

        # Some sort of command line control to select the following
        # directories when testing built packages will be necessary.
        #python_path = os.path.join(self.topdir, 'build', 'etc')
        #script_dir = os.path.join(self.topdir, 'build', 'test-tar-gz', 'bin')
        #lib_dir = os.path.join(self.topdir, 'build', 'test-tar-gz', 'lib', 'scons')
        python_path += os.pathsep + lib_dir

        try:
            python_path += os.pathsep + os.environ['PYTHONPATH']
        except KeyError:
            pass
        # Let tests inherit our environment but add some special variables.
        env = os.environ.copy()
        env['PYTHONPATH'] = python_path
        env['SCONS'] = scons
        env['SCONS_LIB_DIR'] = lib_dir

        command = RedirectedExecutable()
        status = command.Run([context.get('python', 'python'), self.script],
                             env)
        if not check_exit_status(result, 'Test.', self.script, status):
            # In case of failure record exit code, stdout, and stderr.
            result.Fail("Unexpected exit_code.")
            result["Test.stdout"] = result.Quote(command.stdout)
            result["Test.stderr"] = result.Quote(command.stderr)


class Database(database.Database):
    """Scons test database.
    * The 'src' and 'test' directories are explicit suites.
    * Their subdirectories are implicit suites.
    * All files under 'src/' ending with 'Tests.py' contain tests.
    * All files under 'test/' with extension '.py' contain tests.
    * Right now there is only a single test class, which simply runs
      the specified python interpreter on the given script. To be refined..."""

    srcdir = TextField(title = "Source Directory",
                       description = "The root of the test suite's source tree.")
    _is_generic_database = True

    def is_a_test_under_test(path, t):
        return os.path.splitext(t)[1] == '.py' \
               and os.path.isfile(os.path.join(path, t))

    def is_a_test_under_src(path, t):
        return t[-8:] == 'Tests.py' \
               and os.path.isfile(os.path.join(path, t))

    is_a_test = {
        'src' : is_a_test_under_src,
        'test' : is_a_test_under_test,
    }


    def __init__(self, path, arguments):

        self.label_class = "python_label.PythonLabel"
        self.modifiable = "false"
        # Initialize the base class.
        super(Database, self).__init__(path, arguments)


    def GetRoot(self):

        return self.srcdir


    def GetSubdirectories(self, directory):

        components = self.GetLabelComponents(directory)
        path = os.path.join(self.GetRoot(), *components)
        if directory:
            dirs = [d for d in dircache.listdir(path)
                    if os.path.isdir(os.path.join(path, d))]
        else:
            dirs = self.is_a_test.keys()

        dirs.sort()
        return dirs


    def GetIds(self, kind, directory = "", scan_subdirs = 1):

        components = self.GetLabelComponents(directory)
        path = os.path.join(self.GetRoot(), *components)

        if kind == database.Database.TEST:

            if not components:
                return []

            ids = [self.JoinLabels(directory, os.path.splitext(t)[0])
                   for t in dircache.listdir(path)
                   if self.is_a_test[components[0]](path, t)]

        elif kind == Database.RESOURCE:
            return [] # no resources yet

        else: # SUITE

            if directory:
                ids = [self.JoinLabels(directory, d)
                       for d in dircache.listdir(path)
                       if os.path.isdir(os.path.join(path, d))]
            else:
                ids = self.is_a_test.keys()

        if scan_subdirs:
            for d in dircache.listdir(path):
                if (os.path.isdir(d)):
                    ids.extend(self.GetIds(kind,
                                           self.JoinLabels(directory, d),
                                           True))

        return ids


    def GetExtension(self, id):

        if not id:
            return DirectorySuite(self, id)

        components = self.GetLabelComponents(id)
        path = os.path.join(self.GetRoot(), *components)

        if os.path.isdir(path): # a directory
            return DirectorySuite(self, id)

        elif os.path.isfile(path + '.py'): # a test

            arguments = {}
            arguments['script'] = path + '.py'
            arguments['topdir'] = self.GetRoot()

            return Test(arguments, qmtest_id = id, qmtest_database = self)

        else: # nothing else to offer

            return None


    def GetTest(self, test_id):
        """This method can be removed once QMTest 2.4 is out."""

        t = self.GetExtension(test_id)
        if isinstance(t, test.Test):
            return database.TestDescriptor(self,
                                           test_id,
                                           get_extension_class_name(t.__class__),
                                           get_explicit_arguments(t))

        raise database.NoSuchTestError(test_id)

    def GetSuite(self, suite_id):
        """This method can be removed once QMTest 2.4 is out."""

        if suite_id == "":
            return DirectorySuite(self, "")

        s = self.GetExtension(suite_id)
        if isinstance(s, suite.Suite):
            return s

        raise database.NoSuchSuiteError(suite_id)


    def GetResource(self, resource_id):
        """This method can be removed once QMTest 2.4 is out."""

        r = self.GetExtension(resource_id)
        if isinstance(r, resource.Resource):
            return ResourceDescriptor(self,
                                      resource_id,
                                      get_extension_class_name(r.__class__),
                                      get_explicit_arguments(r))

        raise database.NoSuchResourceError(resource_id)
