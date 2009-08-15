#! /usr/bin/env python
#
# SCons frontend
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

__version__ = "__VERSION__"

__build__ = "__BUILD__"

__buildsys__ = "__BUILDSYS__"

__date__ = "__DATE__"

__developer__ = "__DEVELOPER__"

import Tkinter
import Tix
import tkFileDialog
import tkMessageBox
import sys
import os
import os.path
import string

##############################################################################
# BEGIN STANDARD SCons SCRIPT HEADER
#
# This is the cut-and-paste logic so that a self-contained script can
# interoperate correctly with different SCons versions and installation
# locations for the engine.  If you modify anything in this section, you
# should also change other scripts that use this same header.
##############################################################################

# Strip the script directory from sys.path() so on case-insensitive
# (WIN32) systems Python doesn't think that the "scons" script is the
# "SCons" package.  Replace it with our own library directories
# (version-specific first, in case they installed by hand there,
# followed by generic) so we pick up the right version of the build
# engine modules if they're in either directory.

script_dir = sys.path[0]

if script_dir in sys.path:
    sys.path.remove(script_dir)

libs = []

if os.environ.has_key("SCONS_LIB_DIR"):
    libs.append(os.environ["SCONS_LIB_DIR"])

local_version = 'scons-local-' + __version__
local = 'scons-local'
if script_dir:
    local_version = os.path.join(script_dir, local_version)
    local = os.path.join(script_dir, local)
libs.append(os.path.abspath(local_version))
libs.append(os.path.abspath(local))

scons_version = 'scons-%s' % __version__

prefs = []

if sys.platform == 'win32':
    # sys.prefix is (likely) C:\Python*;
    # check only C:\Python*.
    prefs.append(sys.prefix)
    prefs.append(os.path.join(sys.prefix, 'Lib', 'site-packages'))
else:
    # On other (POSIX) platforms, things are more complicated due to
    # the variety of path names and library locations.  Try to be smart
    # about it.
    if script_dir == 'bin':
        # script_dir is `pwd`/bin;
        # check `pwd`/lib/scons*.
        prefs.append(os.getcwd())
    else:
        if script_dir == '.' or script_dir == '':
            script_dir = os.getcwd()
        head, tail = os.path.split(script_dir)
        if tail == "bin":
            # script_dir is /foo/bin;
            # check /foo/lib/scons*.
            prefs.append(head)

    head, tail = os.path.split(sys.prefix)
    if tail == "usr":
        # sys.prefix is /foo/usr;
        # check /foo/usr/lib/scons* first,
        # then /foo/usr/local/lib/scons*.
        prefs.append(sys.prefix)
        prefs.append(os.path.join(sys.prefix, "local"))
    elif tail == "local":
        h, t = os.path.split(head)
        if t == "usr":
            # sys.prefix is /foo/usr/local;
            # check /foo/usr/local/lib/scons* first,
            # then /foo/usr/lib/scons*.
            prefs.append(sys.prefix)
            prefs.append(head)
        else:
            # sys.prefix is /foo/local;
            # check only /foo/local/lib/scons*.
            prefs.append(sys.prefix)
    else:
        # sys.prefix is /foo (ends in neither /usr or /local);
        # check only /foo/lib/scons*.
        prefs.append(sys.prefix)

    temp = map(lambda x: os.path.join(x, 'lib'), prefs)
    temp.extend(map(lambda x: os.path.join(x,
                                           'lib',
                                           'python' + sys.version[:3],
                                           'site-packages'),
                           prefs))
    prefs = temp

    # Add the parent directory of the current python's library to the
    # preferences.  On SuSE-91/AMD64, for example, this is /usr/lib64,
    # not /usr/lib.
    try:
        libpath = os.__file__
    except AttributeError:
        pass
    else:
        # Split /usr/libfoo/python*/os.py to /usr/libfoo/python*.
        libpath, tail = os.path.split(libpath)
        # Split /usr/libfoo/python* to /usr/libfoo
        libpath, tail = os.path.split(libpath)
        # Check /usr/libfoo/scons*.
        prefs.append(libpath)

# Look first for 'scons-__version__' in all of our preference libs,
# then for 'scons'.
libs.extend(map(lambda x: os.path.join(x, scons_version), prefs))
libs.extend(map(lambda x: os.path.join(x, 'scons'), prefs))

# If this is the binary version of SCons, don't manipulate the path
if (not hasattr(sys, 'frozen')) or (sys.frozen == 0):
    sys.path = libs + sys.path

##############################################################################
# END STANDARD SCons SCRIPT HEADER
##############################################################################

import SCons.compat
import subprocess

if sys.platform in ('win32', 'cygwin'):

    def whereis(file):
        pathext = [''] + string.split(os.environ['PATHEXT'], os.pathsep)
        for dir in string.split(os.environ['PATH'], os.pathsep):
            f = os.path.join(dir, file)
            for ext in pathext:
                fext = f + ext
                if os.path.isfile(fext):
                    return fext
        return None

else:

    def whereis(file):
        for dir in string.split(os.environ['PATH'], os.pathsep):
            f = os.path.join(dir, file)
            if os.path.isfile(f):
                try:
                    st = os.stat(f)
                except OSError:
                    continue
                if stat.S_IMODE(st[stat.ST_MODE]) & 0111:
                    return f
        return None

class OptionsBridge():
    def __init__(self):
        self.options = {}
        self.options_string = Tkinter.StringVar()
        self.sKey = Tkinter.StringVar()
        self.sValue = Tkinter.StringVar()
        self.lVariables = None
        
        self._create_option('help', '-h', 'Help (-h)')        
        self._create_option('help_options', '-H', 'Help options (-H)')
        self._create_option('debug', '--debug=', 'Debug (--debug=TYPE)')
        self._create_option('clean', '-c', 'Clean (-c)')
        self._create_option('profile', '--profile=', 'Profile (--profile=FILE)')
        self._create_option('repository', '--repository=', 'Repository (--repository=REPOSITORY)')
        self._create_option('taskmastertrace', '--taskmastertrace=', 'Task master trace (--taskmastertrace=FILE)')
        self._create_option('tree', '--tree=', 'Tree (--tree=OPTIONS)')
        self._create_option('warn', '--warn=', 'Warn (--warn=WARNING-SPEC)')
        self._create_option('file', '--file=', 'SConstruct file (--file=FILE)')
        self._create_option('ignore_errors', '-i', 'Ignore errors (-i)')
        self._create_option('include_dir', '--include-dir=', 'Python module directory (--include-dir=DIR)')
        self._create_option('jobs', '--jobs=', 'Jobs (--jobs=N)')
        self._create_option('keep_going', '-k', 'Keep going (-k)')
        self._create_option('dry_run', '-n', 'Dry run (-n)')
        self._create_option('Q', '-Q', 'Supress progress messages (-Q)')
        self._create_option('random', '--random', 'Random (--random)')
        self._create_option('silent', '--silent', 'Silent (--silent)')
        self._create_option('version', '-v', 'Version (-v)')
        self._create_option('additional', '', 'Additional options:')
        
        self.option_changed()
    
    def _create_option(self, name, cmd_line, description):
        self.options[name] = Tkinter.IntVar()
        self.options[name].cmd_line = cmd_line
        self.options[name].parameter = Tkinter.StringVar()
        self.options[name].parameter.set('')
        self.options[name].description = description
    
    def option_changed(self):
        new_cmd_line = ''
        
        for key in self.options.keys():
            if self.options[key].get() == 1:
                if self.options[key].parameter.get() == '':
                    new_cmd_line = new_cmd_line + self.options[key].cmd_line + ' '
                else:
                    new_cmd_line = new_cmd_line + self.options[key].cmd_line + self.options[key].parameter.get() + ' '
        
        if self.lVariables is not None:
            for variable in self.lVariables.listbox.get(0, Tkinter.END):
                new_cmd_line = new_cmd_line + variable + ' '
        
        self.options_string.set(new_cmd_line)
    
    def clear_options(self):
        for var in self.options.values():
            var.set(0)
        
        if self.lVariables.listbox.size() > 0 and tkMessageBox.askyesno("Clear options", "Remove build variables as well?"):
            self.lVariables.listbox.delete(0, Tkinter.END)
        
        self.option_changed()
        
    def set_variable(self):
        new_variable = self.sKey.get()
        new_value = self.sValue.get()
        
        for index in range(0, self.lVariables.listbox.size()):
            variable = self.lVariables.listbox.get(index)
            if variable.find('=') != -1:
                variable = variable[:variable.find('=')]
            if variable == new_variable:
                self.lVariables.listbox.delete(index)
                self.lVariables.listbox.insert(index, "%s=%s" % (new_variable, new_value))
                self.lVariables.listbox.see(index)
                return

        self.lVariables.listbox.insert(Tkinter.END, "%s=%s" % (new_variable, new_value))
        self.lVariables.listbox.see(Tkinter.END)
        
        self.option_changed()

    def edit_variable(self):
        selection = self.lVariables.listbox.curselection()
        if len(selection) > 0:
            key_value = self.lVariables.listbox.get(selection[0])
            i = key_value.find('=')
            if i != -1:
                self.sKey.set(key_value[:i])
                self.sValue.set(key_value[i+1:])
            else:
                self.sKey.set(key_value)
                self.sValue.set('')

    def delete_variable(self):
        selection = self.lVariables.listbox.curselection()
        if len(selection) > 0:
            self.lVariables.listbox.delete(selection[0])
            self.option_changed()
        

class FrontendWindow():
    def __init__(self, title = None):
        self.root = Tix.Tk()
        self.root.title(title)
        self.root.minsize(750,500)
        
        self.options_bridge = OptionsBridge()
        
        self.create_window(self.root)
    
    def create_window(self, master):
        #
        # Constants
        #
        
        frame_border_width = 2
        button_pad_x = 2
        button_pad_y = 2
        
        #
        # Frames
        #
        pathframe = Tkinter.Frame(master, borderwidth = frame_border_width, relief = Tkinter.GROOVE)
        pathframe.grid(row = 0, sticky = Tkinter.N + Tkinter.W + Tkinter.E)
        
        optionframe = Tkinter.Frame(master, borderwidth = frame_border_width, relief = Tkinter.GROOVE, height = 150)
        optionframe.grid(row = 1, sticky = Tkinter.N + Tkinter.S + Tkinter.W + Tkinter.E)
        optionframe.pack_propagate(0)
        
        outputframe = Tkinter.Frame(master, borderwidth = frame_border_width, relief = Tkinter.GROOVE)
        outputframe.grid(row = 2, sticky = Tkinter.N + Tkinter.S + Tkinter.W + Tkinter.E)
        
        buttonframe = Tkinter.Frame(master, borderwidth = frame_border_width, relief = Tkinter.GROOVE)
        buttonframe.grid(row = 3, sticky =  Tkinter.S + Tkinter.W + Tkinter.E)
        
        #
        # Path frame
        #
        Tkinter.Label(pathframe, text = "SCons:").grid(row = 0, sticky = Tkinter.W)
        Tkinter.Label(pathframe, text = "SConstruct directory:").grid(row = 1, sticky = Tkinter.W)
        Tkinter.Label(pathframe, text = "Options:").grid(row = 2, sticky = Tkinter.W)
        Tkinter.Label(pathframe, text = "Targets:").grid(row = 3, sticky = Tkinter.W)
        
        self.SConsPath = Tkinter.StringVar(value = whereis('scons'))
        self.eSCons = Tkinter.Entry(pathframe, textvariable = self.SConsPath)
        self.eSCons.grid(row = 0, column = 1, sticky = Tkinter.W + Tkinter.E)
        
        self.SConstructPath = Tkinter.StringVar()
        self.eSConstruct = Tkinter.Entry(pathframe, textvariable = self.SConstructPath)
        self.eSConstruct.grid(row = 1, column = 1, sticky = Tkinter.W + Tkinter.E)
        
        self.OptionsString = self.options_bridge.options_string
        self.eOptions = Tkinter.Entry(pathframe, textvariable = self.OptionsString, state = 'readonly')
        self.eOptions.grid(row = 2, column = 1, sticky = Tkinter.W + Tkinter.E)
        
        self.TargetsString = Tkinter.StringVar()
        self.eTargets = Tkinter.Entry(pathframe, textvariable = self.TargetsString)
        self.eTargets.grid(row = 3, column = 1, sticky = Tkinter.W + Tkinter.E)
        
        Tkinter.Button(pathframe, text = "Select...", padx = button_pad_x, pady = button_pad_y, command = self.select_scons).grid(row = 0, column = 2, sticky = Tkinter.E + Tkinter.W)
        Tkinter.Button(pathframe, text = "Select...", padx = button_pad_x, pady = button_pad_y, command = self.select_sconstruct_dir).grid(row = 1, column = 2, sticky = Tkinter.E + Tkinter.W)
        Tkinter.Button(pathframe, text = "Clear", padx = button_pad_x, pady = button_pad_y, command = self.clear_options).grid(row = 2, column = 2, sticky = Tkinter.E + Tkinter.W)
        Tkinter.Button(pathframe, text = "Clear", padx = button_pad_x, pady = button_pad_y, command = self.clear_targets).grid(row = 3, column = 2, sticky = Tkinter.E + Tkinter.W)
        
        pathframe.columnconfigure(1, weight = 1)

        #
        # Option frame
        #
        
        notebook = Tix.NoteBook(optionframe)
        notebook.pack(fill = Tix.BOTH, expand = 1)
        
        p_options = notebook.add('options', label = 'Options')
        p_values = notebook.add('values', label = 'Values')
        
        w_options = Tix.ScrolledWindow(p_options, scrollbar='auto')
        w_options.pack(fill = Tix.BOTH, expand = 1)
        
        ob = self.options_bridge
        
        def create_option(name, row, column, parameter):
            Tkinter.Checkbutton(w_options.window, text = ob.options[name].description, variable = ob.options[name], command = ob.option_changed).grid(row = row, column = 2 * column, sticky = Tkinter.W)
            if parameter == 1:
                Tkinter.Entry(w_options.window, textvariable = ob.options[name].parameter).grid(row = row, column = 2 * column + 1, sticky = Tkinter.W + Tkinter.E)

        create_option('help',           0,  0, 0)
        create_option('help_options',   1,  0, 0)
        create_option('clean',          2,  0, 0)
        create_option('ignore_errors',  3,  0, 0)
        create_option('keep_going',     4,  0, 0)
        create_option('dry_run',        5,  0, 0)
        create_option('Q',              6,  0, 0)
        create_option('silent',         7,  0, 0)
        create_option('version',        8,  0, 0)
        create_option('random',         9,  0, 0)

        create_option('file',               0,  1, 1)
        create_option('jobs',               1,  1, 1)
        create_option('repository',         2,  1, 1)
        create_option('include_dir',        3,  1, 1)
        create_option('tree',               4,  1, 1)
        create_option('warn',               5,  1, 1)
        create_option('debug',              6,  1, 1)
        create_option('profile',            7,  1, 1)
        create_option('taskmastertrace',    8,  1, 1)
        create_option('additional',         9,  1, 1)
        
        w_options.window.columnconfigure(3, weight = 1)
        w_options.window.rowconfigure(99, weight = 1)
        
        self.options_bridge.lVariables = Tix.ScrolledListBox(p_values, height = 10)
        self.options_bridge.lVariables.grid(row = 0, column = 0, rowspan = 4, sticky = Tkinter.W + Tkinter.E + Tkinter.S + Tkinter.N)
        self.options_bridge.lVariables.listbox.configure(selectmode = Tkinter.SINGLE)
        
        Tkinter.Label(p_values, text = "Variable:").grid(row = 0, column = 1, sticky = Tkinter.W)
        
        self.sKey = Tkinter.StringVar()
        Tkinter.Entry(p_values, textvariable = self.options_bridge.sKey).grid(row = 0, column = 2, columnspan = 2)
        
        Tkinter.Label(p_values, text = "Value:").grid(row = 1, column = 1, sticky = Tkinter.W)
        
        self.sValue = Tkinter.StringVar()
        Tkinter.Entry(p_values, textvariable = self.options_bridge.sValue).grid(row = 1, column = 2, columnspan = 2)
        
        Tkinter.Button(p_values, text = "Set", padx = button_pad_x, pady = button_pad_y, command = self.options_bridge.set_variable).grid(row = 2, column = 1, sticky = Tkinter.W + Tkinter.E)
        Tkinter.Button(p_values, text = "Edit", padx = button_pad_x, pady = button_pad_y, command = self.options_bridge.edit_variable).grid(row = 2, column = 2, sticky = Tkinter.W + Tkinter.E)
        Tkinter.Button(p_values, text = "Delete", padx = button_pad_x, pady = button_pad_y, command = self.options_bridge.delete_variable).grid(row = 2, column = 3, sticky = Tkinter.W + Tkinter.E)
        
        p_values.rowconfigure(3, weight = 1)
        p_values.columnconfigure(0, weight = 1)
        
        #
        # Output frame
        #
        self.tOutput = Tkinter.Text(outputframe)
        self.tOutput.grid(row = 0, column = 0, sticky = Tkinter.N + Tkinter.S + Tkinter.W + Tkinter.E)
        self.tOutput.tag_config('stderr', foreground = "red")
        self.tOutput.insert(Tkinter.INSERT, "SCons output will appear here.")
        self.tOutput.config(state = Tkinter.DISABLED)
        
        scrollbar = Tkinter.Scrollbar(outputframe)
        scrollbar.grid(row = 0, column = 1, sticky = Tkinter.N + Tkinter.S + Tkinter.W + Tkinter.E)
        
        self.tOutput.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = self.tOutput.yview)
        
        outputframe.rowconfigure(0, weight = 1)
        outputframe.columnconfigure(0, weight = 1)
        
        #
        # Button frame
        #
        Tkinter.Button(buttonframe, text = "Run SCons", padx = button_pad_x, pady = button_pad_y, command = self.run_scons).grid(row = 0, column = 0)
        Tkinter.Button(buttonframe, text = "Close", padx = button_pad_x, pady = button_pad_y, command = master.destroy).grid(row = 0, column = 2)
        
        buttonframe.columnconfigure(1, weight = 1)
        
        master.columnconfigure(0, weight = 1)
        #master.rowconfigure(1, weight = 1)
        master.rowconfigure(2, weight = 3)

    def clear_options(self):
        self.options_bridge.clear_options()

    def clear_targets(self):
        self.TargetsString.set('')

    def run(self):
        self.root.mainloop()

    def run_scons(self):
        scons = self.SConsPath.get()

        sconstruct_path = self.SConstructPath.get()
        if sconstruct_path == '':
            return
        
        self.options_bridge.option_changed()
        options = self.OptionsString.get()
        targets = self.TargetsString.get()
        variables = string.join(self.options_bridge.lVariables.listbox.get(0, Tkinter.END))
        cmd_line = string.join([scons, options, targets, variables, '--'])
        process = subprocess.Popen(cmd_line, stdout = subprocess.PIPE, stderr = subprocess.PIPE, cwd = sconstruct_path)
        
        self.tOutput.config(state = Tkinter.NORMAL)
        self.tOutput.delete('1.0', Tkinter.END)
        self.tOutput.insert(Tkinter.INSERT, "Running SCons in directory %s\n" % sconstruct_path)
        self.tOutput.insert(Tkinter.INSERT, "Command line: %s\n\n" % cmd_line)
        self.tOutput.config(state = Tkinter.DISABLED)
        
        while process.poll() == None:
            output = process.communicate()
            self.tOutput.config(state = Tkinter.NORMAL)
            self.tOutput.insert(Tkinter.INSERT, output[0])
            self.tOutput.insert(Tkinter.INSERT, output[1], "stderr")
            self.tOutput.config(state = Tkinter.DISABLED)
    
    def select_scons(self):
        scons = tkFileDialog.askopenfilename(parent = self.root, title = 'Select SCons executable', filetypes = [('Executables', '*.exe;*.bat')], initialdir = os.path.dirname(self.SConsPath.get()))
        if scons != '':
            self.SConsPath.set(scons)
    
    def select_sconstruct_dir(self):
        sconstruct_dir = tkFileDialog.askdirectory(parent = self.root, title = 'Select directory', initialdir = os.path.dirname(self.SConstructPath.get()), mustexist = 1)
        
        if sconstruct_dir != '':
            self.SConstructPath.set(sconstruct_dir)


def run_test_options_bridge():
    class MockIntVar():
        def __init__(self):
            self.value = 0
        def set(self, value):
            self.value = value
        def get(self):
            return self.value
    def MockIntVarFactory():
        return MockIntVar()
    Tkinter.IntVar = MockIntVarFactory
    
    class MockStringVar():
        def __init__(self):
            self.value = ''
        def set(self, value):
            self.value = value
        def get(self):
            return self.value
    def MockStringVarFactory():
        return MockStringVar()
    Tkinter.StringVar = MockStringVarFactory

    bridge = OptionsBridge()
    
    assert bridge.options_string.get() == '', bridge.options_string.get()
    
    bridge.options['version'].set(1)
    assert bridge.options_string.get() == '', bridge.options_string.get()
    
    bridge.option_changed()
    assert bridge.options_string.get() == '-v ', bridge.options_string.get()
    
    bridge.clear_options()
    assert bridge.options_string.get() == '', bridge.options_string.get()
    
    bridge.options['include_dir'].parameter.set('bar')
    bridge.options['include_dir'].set(1)
    bridge.option_changed()
    assert bridge.options_string.get() == '--include-dir=bar ', bridge.options_string.get()
    
    return 0
            
if __name__ == "__main__":
    if len(sys.argv) == 3:
        if  sys.argv[1] == 'test':
            if sys.argv[2] == 'options-bridge':
                result = run_test_options_bridge()
                sys.exit(result)
            elif sys.argv[2] == 'create-window':
                window = FrontendWindow(title = '')
                sys.exit(0)
            else:
                sys.stderr.writelines('Unknown test option: ' + sys.argv[2])
                sys.exit(1)
    else:
        window = FrontendWindow(title = "SCons frontend (__VERSION__)")    
        if len(sys.argv) == 2:
            if os.path.isdir(sys.argv[1]):
                window.SConstructPath.set(os.path.abspath(sys.argv[1]))
            elif os.path.isfile(sys.argv[1]):
                window.SConstructPath.set(os.path.split(os.path.abspath(sys.argv[1]))[0])
                window.options_bridge.options['file'].parameter.set(os.path.split(os.path.abspath(sys.argv[1]))[1])
                window.options_bridge.options['file'].set(1)
                window.options_bridge.option_changed()
            else:
                window.SConstructPath.set(os.getcwd())
        else:
            window.SConstructPath.set(os.getcwd())
        window.run()