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
                     IndentedHelpFormatter, SUPPRESS_HELP, Values

diskcheck_all = SCons.Node.FS.diskcheck_types()

def diskcheck_convert(value):
    if value is None:
        return []
    if not SCons.Util.is_List(value):
        value = string.split(value, ',')
    result = []
    for v in map(string.lower, value):
        if v == 'all':
            result = diskcheck_all
        elif v == 'none':
            result = []
        elif v in diskcheck_all:
            result.append(v)
        else:
            raise ValueError, v
    return result

class SConsValues(Values):
    """

    Holder class for uniform access to SCons options, regardless
    of whether or not they can be set on the command line or in the
    SConscript files (using the SetOption() function).

    A SCons option value can originate three different ways:

        1)  set on the command line;
        2)  set in an SConscript file;
        3)  the default setting (from the the op.add_option()
            calls in the Parser() function, below).

    The command line always overrides a value set in a SConscript file,
    which in turn always overrides default settings.  Because we want
    to support user-specified options in the SConscript file itself,
    though, we may not know about all of the options when the command
    line is first parsed, so we can't make all the necessary precedence
    decisions at the time the option is configured.

    The solution implemented in this class is to keep these different sets
    of settings separate (command line, SConscript file, and default)
    and to override the __getattr__() method to check them in turn.
    This should allow the rest of the code to just fetch values as
    attributes of an instance of this class, without having to worry
    about where they came from.

    Note that not all command line options are settable from SConscript
    files, and the ones that are must be explicitly added to the
    "settable" list in this class, and optionally validated and coerced
    in the set_option() method.
    """

    def __init__(self, defaults):
        self.__dict__['__defaults__'] = defaults
        self.__dict__['__SConscript_settings__'] = {}

    def __getattr__(self, attr):
        """
        Fetches an options value, checking first for explicit settings
        from the command line (which are direct attributes), then the
        SConscript file settings, then the default values.
        """
        try:
            return self.__dict__[attr]
        except KeyError:
            try:
                return self.__dict__['__SConscript_settings__'][attr]
            except KeyError:
                return getattr(self.__dict__['__defaults__'], attr)

    settable = [
        'clean',
        'diskcheck',
        'duplicate',
        'help',
        'implicit_cache',
        'max_drift',
        'no_exec',
        'num_jobs',
        'random',
    ]

    def set_option(self, name, value):
        """
        Sets an option from an SConscript file.
        """
        if not name in self.settable:
            raise SCons.Errors.UserError, "This option is not settable from a SConscript file: %s"%name

        if name == 'num_jobs':
            try:
                value = int(value)
                if value < 1:
                    raise ValueError
            except ValueError:
                raise SCons.Errors.UserError, "A positive integer is required: %s"%repr(value)
        elif name == 'max_drift':
            try:
                value = int(value)
            except ValueError:
                raise SCons.Errors.UserError, "An integer is required: %s"%repr(value)
        elif name == 'duplicate':
            try:
                value = str(value)
            except ValueError:
                raise SCons.Errors.UserError, "A string is required: %s"%repr(value)
            if not value in SCons.Node.FS.Valid_Duplicates:
                raise SCons.Errors.UserError, "Not a valid duplication style: %s" % value
            # Set the duplicate style right away so it can affect linking
            # of SConscript files.
            SCons.Node.FS.set_duplicate(value)
        elif name == 'diskcheck':
            try:
                value = diskcheck_convert(value)
            except ValueError, v:
                raise SCons.Errors.UserError, "Not a valid diskcheck value: %s"%v
            if not self.__dict__.has_key('diskcheck'):
                # No --diskcheck= option was specified on the command line.
                # Set this right away so it can affect the rest of the
                # file/Node lookups while processing the SConscript files.
                SCons.Node.FS.set_diskcheck(value)

        self.__SConscript_settings__[name] = value

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

    # Add the options to the parser we just created.
    #
    # These are in the order we want them to show up in the -H help
    # text, basically alphabetical.  Each op.add_option() call below
    # should have a consistent format:
    #
    #   op.add_option("-L", "--long-option-name",
    #                 dest="long_option_name", default='foo',
    #                 action="callback", callback=opt_long_option,
    #                 help="help text goes here",
    #                 metavar="VAR")
    #
    # Even though the optparse module constructs reasonable default
    # destination names from the long option names, we're going to be
    # explicit about each one for easier readability and so this code
    # will at least show up when grepping the source for option attribute
    # names, or otherwise browsing the source code.

    # options ignored for compatibility
    def opt_ignore(option, opt, value, parser):
        sys.stderr.write("Warning:  ignoring %s option\n" % opt)
    op.add_option("-b", "-m", "-S", "-t",
                  "--no-keep-going", "--stop", "--touch",
                  action="callback", callback=opt_ignore,
                  help="Ignored for compatibility.")

    op.add_option('-c', '--clean', '--remove',
                  dest="clean", default=False,
                  action="store_true",
                  help="Remove specified targets and dependencies.")

    op.add_option('-C', '--directory',
                  nargs=1, type="string",
                  dest="directory", default=[],
                  action="append",
                  help="Change to DIR before doing anything.",
                  metavar="DIR")

    op.add_option('--cache-debug',
                  nargs=1,
                  dest="cache_debug", default=None,
                  action="store",
                  help="Print CacheDir debug info to FILE.",
                  metavar="FILE")

    op.add_option('--cache-disable', '--no-cache',
                  dest='cache_disable', default=False,
                  action="store_true",
                  help="Do not retrieve built targets from CacheDir.")

    op.add_option('--cache-force', '--cache-populate',
                  dest='cache_force', default=False,
                  action="store_true",
                  help="Copy already-built targets into the CacheDir.")

    op.add_option('--cache-show',
                  dest='cache_show', default=False,
                  action="store_true",
                  help="Print build actions for files from CacheDir.")

    config_options = ["auto", "force" ,"cache"]

    def opt_config(option, opt, value, parser, c_options=config_options):
        if not value in c_options:
            raise OptionValueError("Warning:  %s is not a valid config type" % value)
        setattr(parser.values, option.dest, value)
    opt_config_help = "Controls Configure subsystem: %s." \
                      % string.join(config_options, ", ")
    op.add_option('--config',
                  nargs=1, type="string",
                  dest="config", default="auto",
                  action="callback", callback=opt_config,
                  help = opt_config_help,
                  metavar="MODE")

    def opt_not_yet(option, opt, value, parser):
        sys.stderr.write("Warning:  the %s option is not yet implemented\n" % opt)
        sys.exit(0)
    op.add_option('-d',
                  action="callback", callback=opt_not_yet,
                  help = "Print file dependency information.")

    op.add_option('-D',
                  dest="climb_up", default=None,
                  action="store_const", const=2,
                  help="Search up directory tree for SConstruct,       "
                       "build all Default() targets.")

    debug_options = ["count", "dtree", "explain", "findlibs",
                     "includes", "memoizer", "memory", "objects",
                     "pdb", "presub", "stacktrace", "stree",
                     "time", "tree"]

    deprecated_debug_options = {
        "nomemoizer" : ' and has no effect',
    }

    def opt_debug(option, opt, value, parser,
                  debug_options=debug_options,
                  deprecated_debug_options=deprecated_debug_options):
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
    opt_debug_help = "Print various types of debugging information: %s." \
                     % string.join(debug_options, ", ")
    op.add_option('--debug',
                  nargs=1, type="string",
                  dest="debug", default=[],
                  action="callback", callback=opt_debug,
                  help=opt_debug_help,
                  metavar="TYPE")

    def opt_diskcheck(option, opt, value, parser):
        try:
            diskcheck_value = diskcheck_convert(value)
        except ValueError, e:
            raise OptionValueError("Warning: `%s' is not a valid diskcheck type" % e)
        setattr(parser.values, option.dest, diskcheck_value)

    op.add_option('--diskcheck',
                  nargs=1, type="string",
                  dest='diskcheck', default=None,
                  action="callback", callback=opt_diskcheck,
                  help="Enable specific on-disk checks.",
                  metavar="TYPE")

    def opt_duplicate(option, opt, value, parser):
        if not value in SCons.Node.FS.Valid_Duplicates:
            raise OptionValueError("`%s' is not a valid duplication style." % value)
        setattr(parser.values, option.dest, value)
        # Set the duplicate style right away so it can affect linking
        # of SConscript files.
        SCons.Node.FS.set_duplicate(value)

    opt_duplicate_help = "Set the preferred duplication methods. Must be one of " \
                         + string.join(SCons.Node.FS.Valid_Duplicates, ", ")

    op.add_option('--duplicate',
                  nargs=1, type="string",
                  dest="duplicate", default='hard-soft-copy',
                  action="callback", callback=opt_duplicate,
                  help=opt_duplicate_help)

    op.add_option('-f', '--file', '--makefile', '--sconstruct',
                  nargs=1, type="string",
                  dest="file", default=[],
                  action="append",
                  help="Read FILE as the top-level SConstruct file.")

    op.add_option('-h', '--help',
                  dest="help", default=False,
                  action="store_true",
                  help="Print defined help message, or this one.")

    op.add_option("-H", "--help-options",
                  action="help",
                  help="Print this message and exit.")

    op.add_option('-i', '--ignore-errors',
                  dest='ignore_errors', default=False,
                  action="store_true",
                  help="Ignore errors from build actions.")

    op.add_option('-I', '--include-dir',
                  nargs=1,
                  dest='include_dir', default=[],
                  action="append",
                  help="Search DIR for imported Python modules.",
                  metavar="DIR")

    op.add_option('--implicit-cache',
                  dest='implicit_cache', default=False,
                  action="store_true",
                  help="Cache implicit dependencies")

    def opt_implicit_deps(option, opt, value, parser):
        setattr(parser.values, 'implicit_cache', True)
        setattr(parser.values, option.dest, True)

    op.add_option('--implicit-deps-changed',
                  dest="implicit_deps_changed", default=False,
                  action="callback", callback=opt_implicit_deps,
                  help="Ignore cached implicit dependencies.")

    op.add_option('--implicit-deps-unchanged',
                  dest="implicit_deps_unchanged", default=False,
                  action="callback", callback=opt_implicit_deps,
                  help="Ignore changes in implicit dependencies.")

    op.add_option('-j', '--jobs',
                  nargs=1, type="int",
                  dest="num_jobs", default=1,
                  action="store",
                  help="Allow N jobs at once.",
                  metavar="N")

    op.add_option('-k', '--keep-going',
                  dest='keep_going', default=False,
                  action="store_true",
                  help="Keep going when a target can't be made.")

    op.add_option('--max-drift',
                  nargs=1, type="int",
                  dest='max_drift', default=SCons.Node.FS.default_max_drift,
                  action="store",
                  help="Set maximum system clock drift to N seconds.",
                  metavar="N")

    op.add_option('-n', '--no-exec', '--just-print', '--dry-run', '--recon',
                  dest='no_exec', default=False,
                  action="store_true",
                  help="Don't build; just print commands.")

    op.add_option('--no-site-dir',
                  dest='no_site_dir', default=False,
                  action="store_true",
                  help="Don't search or use the usual site_scons dir.")

    op.add_option('--profile',
                  nargs=1,
                  dest="profile_file", default=None,
                  action="store",
                  help="Profile SCons and put results in FILE.",
                  metavar="FILE")

    op.add_option('-q', '--question',
                  dest="question", default=False,
                  action="store_true",
                  help="Don't build; exit status says if up to date.")

    op.add_option('-Q',
                  dest='no_progress', default=False,
                  action="store_true",
                  help="Suppress \"Reading/Building\" progress messages.")

    op.add_option('--random',
                  dest="random", default=False,
                  action="store_true",
                  help="Build dependencies in random order.")

    op.add_option('-s', '--silent', '--quiet',
                  dest="silent", default=False,
                  action="store_true",
                  help="Don't print commands.")

    op.add_option('--site-dir',
                  nargs=1,
                  dest='site_dir', default=None,
                  action="store",
                  help="Use DIR instead of the usual site_scons dir.",
                  metavar="DIR")

    op.add_option('--taskmastertrace',
                  nargs=1,
                  dest="taskmastertrace_file", default=None,
                  action="store",
                  help="Trace Node evaluation to FILE.",
                  metavar="FILE")

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

    opt_tree_help = "Print a dependency tree in various formats: %s." \
                    % string.join(tree_options, ", ")

    op.add_option('--tree',
                  nargs=1, type="string",
                  dest="tree_printers", default=[],
                  action="callback", callback=opt_tree,
                  help=opt_tree_help,
                  metavar="OPTIONS")

    op.add_option('-u', '--up', '--search-up',
                  dest="climb_up", default=0,
                  action="store_const", const=1,
                  help="Search up directory tree for SConstruct,       "
                       "build targets at or below current directory.")

    op.add_option('-U',
                  dest="climb_up", default=0,
                  action="store_const", const=3,
                  help="Search up directory tree for SConstruct,       "
                       "build Default() targets from local SConscript.")

    def opt_version(option, opt, value, parser, version=version):
        sys.stdout.write(version + '\n')
        sys.exit(0)
    op.add_option("-v", "--version",
                  action="callback", callback=opt_version,
                  help="Print the SCons version number and exit.")

    op.add_option('--warn', '--warning',
                  nargs=1,
                  dest="warn", default=None,
                  action="store",
                  help="Enable or disable warnings.",
                  metavar="WARNING-SPEC")

    op.add_option('-Y', '--repository', '--srcdir',
                  nargs=1,
                  dest="repository", default=[],
                  action="append",
                  help="Search REPOSITORY for source and target files.")

    # Options from Make and Cons classic that we do not yet support,
    # but which we may support someday and whose (potential) meanings
    # we don't want to change.  These all get a "the -X option is not
    # yet implemented" message and don't show up in the help output.

    op.add_option('-e', '--environment-overrides',
                  action="callback", callback=opt_not_yet,
                  # help="Environment variables override makefiles."
                  help=SUPPRESS_HELP)
    op.add_option('-l', '--load-average', '--max-load',
                  nargs=1, type="int",
                  action="callback", callback=opt_not_yet,
                  # dest="load_average", default=0,
                  # action="store",
                  # help="Don't start multiple jobs unless load is below "
                  #      "LOAD-AVERAGE."
                  help=SUPPRESS_HELP)
    op.add_option('--list-derived',
                  action="callback", callback=opt_not_yet,
                  # help="Don't build; list files that would be built."
                  help=SUPPRESS_HELP)
    op.add_option('--list-actions',
                  action="callback", callback=opt_not_yet,
                  # help="Don't build; list files and build actions."
                  help=SUPPRESS_HELP)
    op.add_option('--list-where',
                  action="callback", callback=opt_not_yet,
                  # help="Don't build; list files and where defined."
                  help=SUPPRESS_HELP)
    op.add_option('-o', '--old-file', '--assume-old',
                  nargs=1, type="string",
                  action="callback", callback=opt_not_yet,
                  # dest="old_file", default=[]
                  # action="append",
                  # help = "Consider FILE to be old; don't rebuild it."
                  help=SUPPRESS_HELP)
    op.add_option('--override',
                  nargs=1, type="string",
                  action="callback", callback=opt_not_yet,
                  # dest="override",
                  # help="Override variables as specified in FILE."
                  help=SUPPRESS_HELP)
    op.add_option('-p',
                  action="callback", callback=opt_not_yet,
                  # help="Print internal environments/objects."
                  help=SUPPRESS_HELP)
    op.add_option('-r', '-R', '--no-builtin-rules', '--no-builtin-variables',
                  action="callback", callback=opt_not_yet,
                  # help="Clear default environments and variables."
                  help=SUPPRESS_HELP)
    op.add_option('-w', '--print-directory',
                  action="callback", callback=opt_not_yet,
                  # help="Print the current directory."
                  help=SUPPRESS_HELP)
    op.add_option('--no-print-directory',
                  action="callback", callback=opt_not_yet,
                  # help="Turn off -w, even if it was turned on implicitly."
                  help=SUPPRESS_HELP)
    op.add_option('--write-filenames',
                  nargs=1, type="string",
                  action="callback", callback=opt_not_yet,
                  # dest="write_filenames",
                  # help="Write all filenames examined into FILE."
                  help=SUPPRESS_HELP)
    op.add_option('-W', '--what-if', '--new-file', '--assume-new',
                  nargs=1, type="string",
                  action="callback", callback=opt_not_yet,
                  # dest="new_file",
                  # help="Consider FILE to be changed."
                  help=SUPPRESS_HELP)
    op.add_option('--warn-undefined-variables',
                  action="callback", callback=opt_not_yet,
                  # help="Warn when an undefined variable is referenced."
                  help=SUPPRESS_HELP)

    return op
