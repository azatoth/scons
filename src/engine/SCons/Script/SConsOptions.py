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

import SCons.compat

import string
import sys
import textwrap

import SCons.Node.FS

from optparse import OptionParser, OptionValueError, \
                     IndentedHelpFormatter, SUPPRESS_HELP

class SConsOptionParser(OptionParser):
    def error(self, msg):
        self.print_usage(sys.stderr)
        sys.stderr.write("SCons error: %s\n" % msg)
        sys.exit(2)

class SConsIndentedHelpFormatter(IndentedHelpFormatter):
    def format_usage(self, usage):
        return "usage: %s\n" % usage

    def format_heading(self, heading):
        if heading == 'options':
            # The versions of optparse.py shipped with Pythons 2.3 and
            # 2.4 pass this in uncapitalized; override that so we get
            # consistent output on all versions.
            heading = "Options"
        return IndentedHelpFormatter.format_heading(self, heading)

    def format_option(self, option):
        """
        A copy of the normal optparse.IndentedHelpFormatter.format_option()
        method, snarfed so we can set the subsequent_indent on the
        textwrap.wrap() call below...
        """
        # The help for each option consists of two parts:
        #   * the opt strings and metavars
        #     eg. ("-x", or "-fFILENAME, --file=FILENAME")
        #   * the user-supplied help string
        #     eg. ("turn on expert mode", "read data from FILENAME")
        #
        # If possible, we write both of these on the same line:
        #   -x      turn on expert mode
        #
        # But if the opt string list is too long, we put the help
        # string on a second line, indented to the same column it would
        # start in if it fit on the first line.
        #   -fFILENAME, --file=FILENAME
        #           read data from FILENAME
        result = []

        try:
            opts = self.option_strings[option]
        except AttributeError:
            # The Python 2.3 version of optparse attaches this to
            # to the option argument, not to this object.
            opts = option.option_strings

        opt_width = self.help_position - self.current_indent - 2
        if len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        else:                       # start help on same line as opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        if option.help:

            try:
                expand_default = self.expand_default
            except AttributeError:
                # The HelpFormatter base class in the Python 2.3 version
                # of optparse has no expand_default() method.
                help_text = option.help
            else:
                help_text = expand_default(option)

            help_lines = textwrap.wrap(help_text, self.help_width,
                                       subsequent_indent = '  ')
            result.append("%*s%s\n" % (indent_first, "", help_lines[0]))
            for line in help_lines[1:]:
                result.append("%*s%s\n" % (self.help_position, "", line))
        elif opts[-1] != "\n":
            result.append("\n")
        return string.join(result, "")

    # For consistent help output across Python versions, we provide a
    # subclass copy of format_option_strings() and these two variables.
    # This is necessary (?) for Python2.3, which otherwise concatenates
    # a short option with its metavar.
    _short_opt_fmt = "%s %s"
    _long_opt_fmt = "%s=%s"

    def format_option_strings(self, option):
        """Return a comma-separated list of option strings & metavariables."""
        if option.takes_value():
            metavar = option.metavar or string.upper(option.dest)
            short_opts = []
            for sopt in option._short_opts:
                short_opts.append(self._short_opt_fmt % (sopt, metavar))
            long_opts = []
            for lopt in option._long_opts:
                long_opts.append(self._long_opt_fmt % (lopt, metavar))
        else:
            short_opts = option._short_opts
            long_opts = option._long_opts

        if self.short_first:
            opts = short_opts + long_opts
        else:
            opts = long_opts + short_opts

        return string.join(opts, ", ")

def Parser(version):
    """
    Returns an options parser object initialized with the standard
    SCons options.
    """

    formatter = SConsIndentedHelpFormatter(max_help_position=30)

    op = SConsOptionParser(add_help_option=False,
                           formatter=formatter,
                           usage="usage: scons [OPTION] [TARGET] ...",)

    # options ignored for compatibility
    def opt_ignore(option, opt, value, parser):
        sys.stderr.write("Warning:  ignoring %s option\n" % opt)
    op.add_option("-b", "-m", "-S", "-t", "--no-keep-going", "--stop",
                    "--touch", action="callback", callback=opt_ignore,
                    help="Ignored for compatibility.")

    op.add_option('-c', '--clean', '--remove', action="store_true",
                    dest="clean",
                    help="Remove specified targets and dependencies.")

    op.add_option('-C', '--directory', type="string", action = "append",
                    metavar="DIR",
                    help="Change to DIR before doing anything.")

    op.add_option('--cache-debug', action="store",
                    dest="cache_debug", metavar="FILE",
                    help="Print CacheDir debug info to FILE.")

    op.add_option('--cache-disable', '--no-cache',
                    action="store_true", dest='cache_disable', default=0,
                    help="Do not retrieve built targets from CacheDir.")

    op.add_option('--cache-force', '--cache-populate',
                    action="store_true", dest='cache_force', default=0,
                    help="Copy already-built targets into the CacheDir.")

    op.add_option('--cache-show',
                    action="store_true", dest='cache_show', default=0,
                    help="Print build actions for files from CacheDir.")

    config_options = ["auto", "force" ,"cache"]

    def opt_config(option, opt, value, parser, c_options=config_options):
        if value in c_options:
            parser.values.config = value
        else:
            raise OptionValueError("Warning:  %s is not a valid config type" % value)
    op.add_option('--config', action="callback", type="string",
                    callback=opt_config, nargs=1, dest="config",
                    metavar="MODE", default="auto",
                    help="Controls Configure subsystem: "
                         "%s." % string.join(config_options, ", "))

    def opt_not_yet(option, opt, value, parser):
        sys.stderr.write("Warning:  the %s option is not yet implemented\n" % opt)
        sys.exit(0)
    op.add_option('-d', action="callback",
                    callback=opt_not_yet,
                    help = "Print file dependency information.")

    op.add_option('-D', action="store_const", const=2, dest="climb_up",
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
    op.add_option('--debug', action="callback", type="string",
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

    op.add_option('--diskcheck', action="callback", type="string",
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
    op.add_option('--duplicate', action="callback", type="string",
                    callback=opt_duplicate, nargs=1, dest="duplicate",
                    help="Set the preferred duplication methods. Must be one of "
                    + string.join(SCons.Node.FS.Valid_Duplicates, ", "))

    op.add_option('-f', '--file', '--makefile', '--sconstruct',
                    action="append", nargs=1,
                    help="Read FILE as the top-level SConstruct file.")

    op.add_option('-h', '--help', action="store_true", default=0,
                    dest="help",
                    help="Print defined help message, or this one.")

    op.add_option("-H", "--help-options",
                    action="help",
                    help="Print this message and exit.")

    op.add_option('-i', '--ignore-errors', action="store_true",
                    default=0, dest='ignore_errors',
                    help="Ignore errors from build actions.")

    op.add_option('-I', '--include-dir', action="append",
                    dest='include_dir', metavar="DIR",
                    help="Search DIR for imported Python modules.")

    op.add_option('--implicit-cache', action="store_true",
                    dest='implicit_cache',
                    help="Cache implicit dependencies")

    def opt_implicit_deps_changed(option, opt, value, parser):
        parser.values.implicit_cache = True
        parser.values.implicit_deps_changed = True
    op.add_option('--implicit-deps-changed',
                    dest="implicit_deps_changed", default=False,
                    action="callback", callback=opt_implicit_deps_changed,
                    help="Ignore cached implicit dependencies.")

    def opt_implicit_deps_unchanged(option, opt, value, parser):
        parser.values.implicit_cache = True
        parser.values.implicit_deps_unchanged = True
    op.add_option('--implicit-deps-unchanged',
                    dest="implicit_deps_unchanged", default=False,
                    action="callback", callback=opt_implicit_deps_unchanged,
                    help="Ignore changes in implicit dependencies.")

    def opt_j(option, opt, value, parser):
        value = int(value)
        parser.values.num_jobs = value
    op.add_option('-j', '--jobs', action="callback", type="int",
                    callback=opt_j, metavar="N",
                    help="Allow N jobs at once.")

    op.add_option('-k', '--keep-going', action="store_true", default=0,
                    dest='keep_going',
                    help="Keep going when a target can't be made.")

    op.add_option('--max-drift', type="int", action="store",
                    dest='max_drift', metavar="N",
                    help="Set maximum system clock drift to N seconds.")

    op.add_option('-n', '--no-exec', '--just-print', '--dry-run',
                    '--recon', action="store_true", dest='no_exec',
                    default=0, help="Don't build; just print commands.")

    op.add_option('--no-site-dir', action="store_true",
                    dest='no_site_dir', default=0,
                    help="Don't search or use the usual site_scons dir.")

    op.add_option('--profile', action="store",
                    dest="profile_file", metavar="FILE",
                    help="Profile SCons and put results in FILE.")

    op.add_option('-q', '--question', action="store_true", default=0,
                    help="Don't build; exit status says if up to date.")

    op.add_option('-Q', dest='no_progress', action="store_true",
                    default=0,
                    help="Suppress \"Reading/Building\" progress messages.")

    op.add_option('--random', dest="random", action="store_true",
                    default=0, help="Build dependencies in random order.")

    op.add_option('-s', '--silent', '--quiet', action="store_true",
                    default=0, help="Don't print commands.")

    op.add_option('--site-dir', action="store",
                    dest='site_dir', metavar="DIR",
                    help="Use DIR instead of the usual site_scons dir.")

    op.add_option('--taskmastertrace', action="store",
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

    op.add_option('--tree', action="callback", type="string",
                    callback=opt_tree, nargs=1, dest="tree_printers",
                    metavar="OPTIONS", default=[],
                    help="Print a dependency tree in various formats: "
                         "%s." % string.join(tree_options, ", "))

    op.add_option('-u', '--up', '--search-up', action="store_const",
                    dest="climb_up", default=0, const=1,
                    help="Search up directory tree for SConstruct,       "
                         "build targets at or below current directory.")
    op.add_option('-U', action="store_const", dest="climb_up",
                    default=0, const=3,
                    help="Search up directory tree for SConstruct,       "
                         "build Default() targets from local SConscript.")

    def opt_version(option, opt, value, parser, version=version):
        sys.stdout.write(version + '\n')
        sys.exit(0)
    op.add_option("-v", "--version", action="callback", callback=opt_version,
                    help="Print the SCons version number and exit.")

    op.add_option('--warn', '--warning', nargs=1, action="store",
                    metavar="WARNING-SPEC",
                    help="Enable or disable warnings.")

    op.add_option('-Y', '--repository', '--srcdir',
                    nargs=1, action="append",
                    help="Search REPOSITORY for source and target files.")

    # Options from Make and Cons classic that we do not yet support,
    # but which we may support someday and whose (potential) meanings
    # we don't want to change.  These all get a "the -X option is not
    # yet implemented" message and don't show up in the help output.

    op.add_option('-e', '--environment-overrides', action="callback",
                    callback=opt_not_yet,
                    # help="Environment variables override makefiles."
                    help=SUPPRESS_HELP)
    op.add_option('-l', '--load-average', '--max-load', action="callback",
                    callback=opt_not_yet, type="int", dest="load_average",
                    # action="store",
                    # help="Don't start multiple jobs unless load is below "
                    #      "LOAD-AVERAGE."
                    # type="int",
                    help=SUPPRESS_HELP)
    op.add_option('--list-derived', action="callback",
                    callback=opt_not_yet,
                    # help="Don't build; list files that would be built."
                    help=SUPPRESS_HELP)
    op.add_option('--list-actions', action="callback",
                    callback=opt_not_yet,
                    # help="Don't build; list files and build actions."
                    help=SUPPRESS_HELP)
    op.add_option('--list-where', action="callback",
                    callback=opt_not_yet,
                    # help="Don't build; list files and where defined."
                    help=SUPPRESS_HELP)
    op.add_option('-o', '--old-file', '--assume-old', action="callback",
                    callback=opt_not_yet, type="string", dest="old_file",
                    # help = "Consider FILE to be old; don't rebuild it."
                    help=SUPPRESS_HELP)
    op.add_option('--override', action="callback", dest="override",
                    callback=opt_not_yet, type="string",
                    # help="Override variables as specified in FILE."
                    help=SUPPRESS_HELP)
    op.add_option('-p', action="callback",
                    callback=opt_not_yet,
                    # help="Print internal environments/objects."
                    help=SUPPRESS_HELP)
    op.add_option('-r', '-R', '--no-builtin-rules',
                    '--no-builtin-variables', action="callback",
                    callback=opt_not_yet,
                    # help="Clear default environments and variables."
                    help=SUPPRESS_HELP)
    op.add_option('-w', '--print-directory', action="callback",
                    callback=opt_not_yet,
                    # help="Print the current directory."
                    help=SUPPRESS_HELP)
    op.add_option('--no-print-directory', action="callback",
                    callback=opt_not_yet,
                    # help="Turn off -w, even if it was turned on implicitly."
                    help=SUPPRESS_HELP)
    op.add_option('--write-filenames', action="callback",
                    callback=opt_not_yet, type="string", dest="write_filenames",
                    # help="Write all filenames examined into FILE."
                    help=SUPPRESS_HELP)
    op.add_option('-W', '--what-if', '--new-file', '--assume-new',
                    dest="new_file",
                    action="callback", callback=opt_not_yet, type="string",
                    # help="Consider FILE to be changed."
                    help=SUPPRESS_HELP)
    op.add_option('--warn-undefined-variables', action="callback",
                    callback=opt_not_yet,
                    # help="Warn when an undefined variable is referenced."
                    help=SUPPRESS_HELP)

    return op
