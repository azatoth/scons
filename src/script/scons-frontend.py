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
import tkFileDialog
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

class FrontendWindow():
    def __init__(self, title = None):
        self.root = Tkinter.Tk()
        self.root.title(title)
        self.root.minsize(640,480)
        
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
        
        optionframe = Tkinter.Frame(master, borderwidth = frame_border_width, relief = Tkinter.GROOVE)
        optionframe.grid(row = 1, sticky = Tkinter.N + Tkinter.S + Tkinter.W + Tkinter.E)
        
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
        
        self.SConsPath = Tkinter.StringVar(value = whereis('scons'))
        self.eSCons = Tkinter.Entry(pathframe, textvariable = self.SConsPath)
        self.eSCons.grid(row = 0, column = 1, sticky = Tkinter.W + Tkinter.E)
        
        self.SConstructPath = Tkinter.StringVar()
        self.eSConstruct = Tkinter.Entry(pathframe, textvariable = self.SConstructPath)
        self.eSConstruct.grid(row = 1, column = 1, sticky = Tkinter.W + Tkinter.E)
        
        self.OptionsString = Tkinter.StringVar()
        self.eOptions = Tkinter.Entry(pathframe, textvariable = self.OptionsString)
        self.eOptions.grid(row = 2, column = 1, sticky = Tkinter.W + Tkinter.E)
        
        Tkinter.Button(pathframe, text = "Select...", padx = button_pad_x, pady = button_pad_y, command = self.select_scons).grid(row = 0, column = 2, sticky = Tkinter.E + Tkinter.W)
        Tkinter.Button(pathframe, text = "Select...", padx = button_pad_x, pady = button_pad_y, command = self.select_sconstruct_dir).grid(row = 1, column = 2, sticky = Tkinter.E + Tkinter.W)
        Tkinter.Button(pathframe, text = "Clear", padx = button_pad_x, pady = button_pad_y, command = self.clear_options).grid(row = 2, column = 2, sticky = Tkinter.E + Tkinter.W)
        
        pathframe.columnconfigure(1, weight = 1)
        
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
        master.rowconfigure(2, weight = 1)

    def clear_options(self):
        self.OptionsString.set("")
        
    def run(self):
        self.root.mainloop()
        
    def run_scons(self):
        scons = self.SConsPath.get()
        
        sconstruct_path = self.SConstructPath.get()
        if sconstruct_path == '':
            return
        
        options = self.OptionsString.get()
        process = subprocess.Popen(string.join([scons,options]), stdout = subprocess.PIPE, stderr = subprocess.PIPE, cwd = sconstruct_path)
        
        self.tOutput.config(state = Tkinter.NORMAL)
        self.tOutput.delete('1.0', Tkinter.END)
        self.tOutput.insert(Tkinter.INSERT, "Running SCons in directory %s\n" % sconstruct_path)
        self.tOutput.insert(Tkinter.INSERT, "Command line: %s %s\n\n" % (scons, options))
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


if __name__ == "__main__":
    window = FrontendWindow(title = "SCons frontend (__VERSION__)")
    if len(sys.argv) == 2:
        if os.path.isdir(sys.argv[1]):
            window.SConstructPath.set(os.path.abspath(sys.argv[1]))
        elif os.path.isfile(sys.argv[1]):
            window.SConstructPath.set(os.path.split(os.path.abspath(sys.argv[1]))[0])
    window.run()