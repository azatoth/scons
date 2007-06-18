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

import string
import sys

import SCons.Node.FS
from SCons.Optik import OptionParser, SUPPRESS_HELP, OptionValueError

class OptParser(OptionParser):
    def __init__(self, version):
        OptionParser.__init__(self, version=version,
                              usage="usage: scons [OPTION] [TARGET] ...")

        # options ignored for compatibility
        def opt_ignore(option, opt, value, parser):
            sys.stderr.write("Warning:  ignoring %s option\n" % opt)
        self.add_option("-b", "-m", "-S", "-t", "--no-keep-going", "--stop",
                        "--touch", action="callback", callback=opt_ignore,
                        help="Ignored for compatibility.")

        self.add_option('-c', '--clean', '--remove', action="store_true",
                        dest="clean",
                        help="Remove specified targets and dependencies.")

        self.add_option('-C', '--directory', type="string", action = "append",
                        metavar="DIR",
                        help="Change to DIR before doing anything.")

        self.add_option('--cache-debug', action="store",
                        dest="cache_debug", metavar="FILE",
                        help="Print CacheDir debug info to FILE.")

        self.add_option('--cache-disable', '--no-cache',
                        action="store_true", dest='cache_disable', default=0,
                        help="Do not retrieve built targets from CacheDir.")

        self.add_option('--cache-force', '--cache-populate',
                        action="store_true", dest='cache_force', default=0,
                        help="Copy already-built targets into the CacheDir.")

        self.add_option('--cache-show',
                        action="store_true", dest='cache_show', default=0,
                        help="Print build actions for files from CacheDir.")

        config_options = ["auto", "force" ,"cache"]

        def opt_config(option, opt, value, parser, c_options=config_options):
            if value in c_options:
                parser.values.config = value
            else:
                raise OptionValueError("Warning:  %s is not a valid config type" % value)
        self.add_option('--config', action="callback", type="string",
                        callback=opt_config, nargs=1, dest="config",
                        metavar="MODE", default="auto",
                        help="Controls Configure subsystem: "
                             "%s." % string.join(config_options, ", "))

        def opt_not_yet(option, opt, value, parser):
            sys.stderr.write("Warning:  the %s option is not yet implemented\n" % opt)
            sys.exit(0)
        self.add_option('-d', action="callback",
                        callback=opt_not_yet,
                        help = "Print file dependency information.")

        self.add_option('-D', action="store_const", const=2, dest="climb_up",
                        help="Search up directory tree for SConstruct,       "
                             "build all Default() targets.")

        debug_options = ["count", "dtree", "explain", "findlibs",
                         "includes", "memoizer", "memory", "objects",
                         "pdb", "presub", "stacktrace", "stree",
                         "time", "tree"]

        deprecated_debug_options = {
            "nomemoizer" : ' and has no effect',
        }

        def opt_debug(option, opt, value, parser, debug_options=debug_options, deprecated_debug_options=deprecated_debug_options):
            if value in debug_options:
                parser.values.debug.append(value)
            elif value in deprecated_debug_options.keys():
                try:
                    parser.values.delayed_warnings
                except AttributeError:
                    parser.values.delayed_warnings = []
                msg = deprecated_debug_options[value]
                w = "The --debug=%s option is deprecated%s." % (value, msg)
                t = (SCons.Warnings.DeprecatedWarning, w)
                parser.values.delayed_warnings.append(t)
            else:
                raise OptionValueError("Warning:  %s is not a valid debug type" % value)
        self.add_option('--debug', action="callback", type="string",
                        callback=opt_debug, nargs=1, dest="debug",
                        metavar="TYPE", default=[],
                        help="Print various types of debugging information: "
                             "%s." % string.join(debug_options, ", "))

        def opt_diskcheck(option, opt, value, parser):
            import Main
            try:
                parser.values.diskcheck = Main.diskcheck_convert(value)
            except ValueError, e:
                raise OptionValueError("Warning: `%s' is not a valid diskcheck type" % e)

        self.add_option('--diskcheck', action="callback", type="string",
                        callback=opt_diskcheck, dest='diskcheck',
                        metavar="TYPE", default=None,
                        help="Enable specific on-disk checks.")

        def opt_duplicate(option, opt, value, parser):
            if not value in SCons.Node.FS.Valid_Duplicates:
                raise OptionValueError("`%s' is not a valid duplication style." % value)
            parser.values.duplicate = value
            # Set the duplicate style right away so it can affect linking
            # of SConscript files.
            SCons.Node.FS.set_duplicate(value)
        self.add_option('--duplicate', action="callback", type="string",
                        callback=opt_duplicate, nargs=1, dest="duplicate",
                        help="Set the preferred duplication methods. Must be one of "
                        + string.join(SCons.Node.FS.Valid_Duplicates, ", "))

        self.add_option('-f', '--file', '--makefile', '--sconstruct',
                        action="append", nargs=1,
                        help="Read FILE as the top-level SConstruct file.")

        self.add_option('-h', '--help', action="store_true", default=0,
                        dest="help",
                        help="Print defined help message, or this one.")

        self.add_option("-H", "--help-options",
                        action="help",
                        help="Print this message and exit.")

        self.add_option('-i', '--ignore-errors', action="store_true",
                        default=0, dest='ignore_errors',
                        help="Ignore errors from build actions.")

        self.add_option('-I', '--include-dir', action="append",
                        dest='include_dir', metavar="DIR",
                        help="Search DIR for imported Python modules.")

        self.add_option('--implicit-cache', action="store_true",
                        dest='implicit_cache',
                        help="Cache implicit dependencies")

        self.add_option('--implicit-deps-changed', action="store_true",
                        default=0, dest='implicit_deps_changed',
                        help="Ignore cached implicit dependencies.")
        self.add_option('--implicit-deps-unchanged', action="store_true",
                        default=0, dest='implicit_deps_unchanged',
                        help="Ignore changes in implicit dependencies.")

        def opt_j(option, opt, value, parser):
            value = int(value)
            parser.values.num_jobs = value
        self.add_option('-j', '--jobs', action="callback", type="int",
                        callback=opt_j, metavar="N",
                        help="Allow N jobs at once.")

        self.add_option('-k', '--keep-going', action="store_true", default=0,
                        dest='keep_going',
                        help="Keep going when a target can't be made.")

        self.add_option('--max-drift', type="int", action="store",
                        dest='max_drift', metavar="N",
                        help="Set maximum system clock drift to N seconds.")

        self.add_option('-n', '--no-exec', '--just-print', '--dry-run',
                        '--recon', action="store_true", dest='no_exec',
                        default=0, help="Don't build; just print commands.")

        self.add_option('--no-site-dir', action="store_true",
                        dest='no_site_dir', default=0,
                        help="Don't search or use the usual site_scons dir.")

        self.add_option('--profile', action="store",
                        dest="profile_file", metavar="FILE",
                        help="Profile SCons and put results in FILE.")

        self.add_option('-q', '--question', action="store_true", default=0,
                        help="Don't build; exit status says if up to date.")

        self.add_option('-Q', dest='no_progress', action="store_true",
                        default=0,
                        help="Suppress \"Reading/Building\" progress messages.")

        self.add_option('--random', dest="random", action="store_true",
                        default=0, help="Build dependencies in random order.")

        self.add_option('-s', '--silent', '--quiet', action="store_true",
                        default=0, help="Don't print commands.")

        self.add_option('--site-dir', action="store",
                        dest='site_dir', metavar="DIR",
                        help="Use DIR instead of the usual site_scons dir.")

        self.add_option('--taskmastertrace', action="store",
                        dest="taskmastertrace_file", metavar="FILE",
                        help="Trace Node evaluation to FILE.")

        tree_options = ["all", "derived", "prune", "status"]

        def opt_tree(option, opt, value, parser, tree_options=tree_options):
            import Main
            tp = Main.TreePrinter()
            for o in string.split(value, ','):
                if o == 'all':
                    tp.derived = False
                elif o == 'derived':
                    tp.derived = True
                elif o == 'prune':
                    tp.prune = True
                elif o == 'status':
                    tp.status = True
                else:
                    raise OptionValueError("Warning:  %s is not a valid --tree option" % o)
            parser.values.tree_printers.append(tp)

        self.add_option('--tree', action="callback", type="string",
                        callback=opt_tree, nargs=1, dest="tree_printers",
                        metavar="OPTIONS", default=[],
                        help="Print a dependency tree in various formats: "
                             "%s." % string.join(tree_options, ", "))

        self.add_option('-u', '--up', '--search-up', action="store_const",
                        dest="climb_up", default=0, const=1,
                        help="Search up directory tree for SConstruct,       "
                             "build targets at or below current directory.")
        self.add_option('-U', action="store_const", dest="climb_up",
                        default=0, const=3,
                        help="Search up directory tree for SConstruct,       "
                             "build Default() targets from local SConscript.")

        self.add_option("-v", "--version",
                        action="version",
                        help="Print the SCons version number and exit.")

        self.add_option('--warn', '--warning', nargs=1, action="store",
                        metavar="WARNING-SPEC",
                        help="Enable or disable warnings.")

        self.add_option('-Y', '--repository', '--srcdir',
                        nargs=1, action="append",
                        help="Search REPOSITORY for source and target files.")

        self.add_option('-e', '--environment-overrides', action="callback",
                        callback=opt_not_yet,
                        # help="Environment variables override makefiles."
                        help=SUPPRESS_HELP)
        self.add_option('-l', '--load-average', '--max-load', action="callback",
                        callback=opt_not_yet, type="int", dest="load_average",
                        # action="store",
                        # help="Don't start multiple jobs unless load is below "
                        #      "LOAD-AVERAGE."
                        # type="int",
                        help=SUPPRESS_HELP)
        self.add_option('--list-derived', action="callback",
                        callback=opt_not_yet,
                        # help="Don't build; list files that would be built."
                        help=SUPPRESS_HELP)
        self.add_option('--list-actions', action="callback",
                        callback=opt_not_yet,
                        # help="Don't build; list files and build actions."
                        help=SUPPRESS_HELP)
        self.add_option('--list-where', action="callback",
                        callback=opt_not_yet,
                        # help="Don't build; list files and where defined."
                        help=SUPPRESS_HELP)
        self.add_option('-o', '--old-file', '--assume-old', action="callback",
                        callback=opt_not_yet, type="string", dest="old_file",
                        # help = "Consider FILE to be old; don't rebuild it."
                        help=SUPPRESS_HELP)
        self.add_option('--override', action="callback", dest="override",
                        callback=opt_not_yet, type="string",
                        # help="Override variables as specified in FILE."
                        help=SUPPRESS_HELP)
        self.add_option('-p', action="callback",
                        callback=opt_not_yet,
                        # help="Print internal environments/objects."
                        help=SUPPRESS_HELP)
        self.add_option('-r', '-R', '--no-builtin-rules',
                        '--no-builtin-variables', action="callback",
                        callback=opt_not_yet,
                        # help="Clear default environments and variables."
                        help=SUPPRESS_HELP)
        self.add_option('-w', '--print-directory', action="callback",
                        callback=opt_not_yet,
                        # help="Print the current directory."
                        help=SUPPRESS_HELP)
        self.add_option('--no-print-directory', action="callback",
                        callback=opt_not_yet,
                        # help="Turn off -w, even if it was turned on implicitly."
                        help=SUPPRESS_HELP)
        self.add_option('--write-filenames', action="callback",
                        callback=opt_not_yet, type="string", dest="write_filenames",
                        # help="Write all filenames examined into FILE."
                        help=SUPPRESS_HELP)
        self.add_option('-W', '--what-if', '--new-file', '--assume-new',
                        dest="new_file",
                        action="callback", callback=opt_not_yet, type="string",
                        # help="Consider FILE to be changed."
                        help=SUPPRESS_HELP)
        self.add_option('--warn-undefined-variables', action="callback",
                        callback=opt_not_yet,
                        # help="Warn when an undefined variable is referenced."
                        help=SUPPRESS_HELP)

    def parse_args(self, args=None, values=None):
        opt, arglist = OptionParser.parse_args(self, args, values)
        if opt.implicit_deps_changed or opt.implicit_deps_unchanged:
            opt.implicit_cache = 1
        return opt, arglist
